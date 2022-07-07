import utilities.s3
from utilities.logger import log_for_audit, log_for_error  # noqa
import utilities.message
import csv

create_action = "CREATE"
update_action = "UPDATE"
delete_action = "DELETE"
blank_lines = "BLANK"
error_lines = "ERROR"


def check_csv_format(csv_row, csv_column_count, env):
    """Checks length of csv data"""
    if len(csv_row) == csv_column_count:
        return True
    else:
        log_for_audit(env, "action:validation | Problem:CSV format invalid - invalid length")
        return False


def valid_action(record_exists, row_data, env):
    """Returns True if action is valid; otherwise returns False"""
    valid_action = False
    if record_exists and row_data["action"] in ("UPDATE", "DELETE"):
        valid_action = True
    if not record_exists and row_data["action"] in ("CREATE"):
        valid_action = True
    if not valid_action:
        log_for_error(env, "Invalid action {} for the record with ID {}".format(row_data["action"], row_data["id"]))
    return valid_action


def cleanup(db_connection, bucket, filename, event, start, summary_count_dict):
    # Close DB connection
    log_for_audit(event["env"], "action: close DB connection")
    db_connection.close()
    # Archive file
    s3_class = utilities.s3.S3()
    s3_class.copy_object(bucket, filename, event, start)
    s3_class.delete_object(bucket, filename, event, start)
    log_for_audit(
        event["env"],
        "action:archive file:{} | bucket:{}/archive/{}".format(filename, filename.split("/")[0], filename.split("/")[1]),
    )
    # Send Slack Notification
    log_for_audit(event["env"], "action:task complete")
    utilities.message.send_success_slack_message(event, start, summary_count_dict)
    return "Cleanup Successful"


def retrieve_file_from_bucket(bucket, filename, event, start):
    log_for_audit(event["env"], "action:retrieve file | bucket:{} | file:{}".format(bucket, filename))
    s3_bucket = utilities.s3.S3()
    return s3_bucket.get_object(bucket, filename, event, start)


def check_csv_values(line, env):
    """Returns false if either id or name are null or empty string"""
    valid_values = True
    try:
        int(line[0])
    except ValueError:
        log_for_audit(env, "action:validation | Problem:Id {} must be a integer".format(line[0]))
        valid_values = False
    if not str(line[0]):
        log_for_audit(env, "action:validation | Problem:Id {} can not be null or empty".format(line[0]))
        valid_values = False
    if not line[1]:
        log_for_audit(env, "action:validation | Problem:Name/Description {} can not be null or empty".format(line[1]))
        valid_values = False
    return valid_values


def initialise_summary_count():
    summary_count_dict = {}
    summary_count_dict[create_action] = 0
    summary_count_dict[update_action] = 0
    summary_count_dict[delete_action] = 0
    summary_count_dict[blank_lines] = 0
    summary_count_dict[error_lines] = 0
    return summary_count_dict


def increment_summary_count(summary_count_dict, action, env):
    if action in [create_action, update_action, delete_action, blank_lines, error_lines]:
        try:
            summary_count_dict[action] = summary_count_dict[action] + 1
        except (KeyError) as e:
            log_for_error(env, "Summary count does not have the key {0}".format(action))
            raise e
    else:
        log_for_error(
            env,
            "Can't increment count for action {0}. Valid actions are {1},{2},{3},{4},{5}".format(
                action, create_action, update_action, delete_action, blank_lines, error_lines
            ),
        )


def process_file(csv_file, event, start, expected_col_count, summary_count_dict):
    """returns dictionary of row data keyed on row number col1=id, col2=description, col3=action"""
    lines = {}
    count = 0
    csv_reader = csv.reader(csv_file.split("\n"))
    for line in csv_reader:
        count += 1
        if len(line) == 0:
            increment_summary_count(summary_count_dict, "BLANK", event["env"])
            continue
        if check_csv_format(line, expected_col_count, event["env"]) and check_csv_values(line, event["env"]):
            lines[str(count)] = {"id": line[0], "name": line[1], "action": line[2]}
        else:
            increment_summary_count(summary_count_dict, "ERROR", event["env"])
            log_for_audit(
                event["env"],
                "action:Incorrect line format | line: {0} | expected:{1} | actual:{2}".format(
                    count, expected_col_count, len(line)
                ),
            )
    if lines == {}:
        utilities.message.send_failure_slack_message(event, start, summary_count_dict)
    return lines


def report_summary_counts(summary_count_dict, env):
    log_for_audit(env, slack_summary_counts(summary_count_dict))


def slack_summary_counts(summary_count_dict):
    report = "updated: {0}, inserted: {1}, deleted: {2}, blank: {3}, errored: {4}".format(
        summary_count_dict[update_action],
        summary_count_dict[create_action],
        summary_count_dict[delete_action],
        summary_count_dict[blank_lines],
        summary_count_dict[error_lines],
    )
    return report
