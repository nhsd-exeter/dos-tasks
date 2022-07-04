from utilities.s3 import S3
from utilities.logger import log_for_audit, log_for_error  # noqa
from utilities.message import send_success_slack_message, send_failure_slack_message
import csv

create_action = "CREATE"
update_action = "UPDATE"
delete_action = "DELETE"


def check_csv_format(csv_row, csv_column_count):
    """Checks length of csv data"""
    if len(csv_row) == csv_column_count:
        return True
    else:
        log_for_audit("CSV format invalid - invalid length")
        return False


def valid_action(record_exists, row_data):
    """Returns True if action is valid; otherwise returns False"""
    valid_action = False
    if record_exists and row_data["action"] in ("UPDATE", "DELETE"):
        valid_action = True
    if not record_exists and row_data["action"] in ("CREATE"):
        valid_action = True
    if not valid_action:
        log_for_error("Invalid action {} for the record with ID {}".format(row_data["action"], row_data["id"]))
    return valid_action


def cleanup(db_connection, bucket, filename, event, start):
    # Close DB connection
    log_for_audit("Closing DB connection...")
    db_connection.close()
    # Archive file
    s3_class = S3()
    s3_class.copy_object(bucket, filename, event, start)
    s3_class.delete_object(bucket, filename, event, start)
    log_for_audit("Archived file {} to {}/archive/{}".format(filename, filename.split("/")[0], filename.split("/")[1]))
    # Send Slack Notification
    log_for_audit("Sending slack message...")
    send_success_slack_message(event, start)
    return "Cleanup Successful"


def retrieve_file_from_bucket(bucket, filename, event, start):
    log_for_audit("Looking in {} for {} file".format(bucket, filename))
    s3_bucket = S3()
    return s3_bucket.get_object(bucket, filename, event, start)


def check_csv_values(line):
    """Returns false if either id or name are null or empty string"""
    valid_values = True
    try:
        int(line[0])
    except ValueError:
        log_for_audit("Id {} must be a integer".format(line[0]))
        valid_values = False
    if not str(line[0]):
        log_for_audit("Id {} can not be null or empty".format(line[0]))
        valid_values = False
    if not line[1]:
        log_for_audit("Name/Description {} can not be null or empty".format(line[1]))
        valid_values = False
    return valid_values


def initialise_summary_count():
    summary_count_dict = {}
    summary_count_dict[create_action] = 0
    summary_count_dict[update_action] = 0
    summary_count_dict[delete_action] = 0
    return summary_count_dict


def increment_summary_count(summary_count_dict, values):
    if values["action"] in [create_action, update_action, delete_action]:
        try:
            summary_count_dict[values["action"]] = summary_count_dict[values["action"]] + 1
        except (KeyError) as e:
            log_for_error("Summary count does not have the key {0}".format(values["action"]))
            raise e
    else:
        log_for_error(
            "Can't increment count for action {0}. Valid actions are {1},{2},{3}".format(
                values["action"], create_action, update_action, delete_action
            )
        )


def process_file(csv_file, event, start, expected_col_count) -> dict:
    """returns dictionary of row data keyed on row number col1=id, col2=description, col3=action"""
    lines = {}
    count = 0
    csv_reader = csv.reader(csv_file.split("\n"))
    for line in csv_reader:
        count += 1
        if len(line) == 0:
            continue
        if check_csv_format(line, expected_col_count) and check_csv_values(line):
            lines[str(count)] = {"id": line[0], "name": line[1], "action": line[2]}
        else:
            log_for_audit(
                "Incorrect line format on line {0}, should be {1} but is {2}".format(
                    count, expected_col_count, len(line)
                )
            )
    if lines == {}:
        send_failure_slack_message(event, start)
    return lines


def report_summary_counts(task_description, summary_count_dict):
    log_for_audit(
        "{0} updated: {1}, inserted: {2}, deleted: {3}".format(
            task_description,
            summary_count_dict[update_action],
            summary_count_dict[create_action],
            summary_count_dict[delete_action],
        )
    )
