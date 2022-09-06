import utilities.s3
from utilities.logger import log_for_audit, log_for_error  # noqa
import utilities.message
import csv

create_action = "CREATE"
update_action = "UPDATE"
delete_action = "DELETE"
blank_lines = "BLANK"
error_lines = "ERROR"


def check_csv_format(csv_row, expected_col_count, env, count):
    """Checks length of csv data"""
    if len(csv_row) == expected_col_count:
        return True
    else:
        log_for_audit(
            env,
            "action:validation | Incorrect line format | line:{0} | expected:{1} | actual:{2}".format(
                count, expected_col_count, len(csv_row)
            ),
        )
        return False


def valid_action(record_exists, row_data, env):
    """Returns True if action is valid; otherwise returns False"""
    valid_action = False
    if record_exists and row_data["action"] in ("UPDATE", "DELETE"):
        valid_action = True
    if not record_exists and row_data["action"] in ("CREATE"):
        valid_action = True
    if not valid_action:
        log_for_error(
            env, "validation:Invalid action {} for the record with ID {}".format(row_data["action"], row_data["id"])
        )
    return valid_action


# TODO move to S3
def archive_file(bucket, filename, event, start):
    # Archive file
    s3_class = utilities.s3.S3()
    s3_class.copy_object(bucket, filename, event, start)
    s3_class.delete_object(bucket, filename, event, start)
    log_for_audit(
        event["env"],
        "action:archive file:{} | bucket:{}/archive/{}".format(
            filename, filename.split("/")[0], filename.split("/")[1]
        ),
    )
    return "File Archive Successful"


def retrieve_file_from_bucket(bucket, filename, event, start):
    log_for_audit(event["env"], "| action:retrieve file | bucket:{} | file:{}".format(bucket, filename))
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
    summary_count_dict[blank_lines] = -1
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


def process_file(csv_file, event, expected_col_count, summary_count_dict):
    """returns dictionary of row data keyed on row number col1=id, col2=description, col3=action"""
    lines = {}
    count = 0
    csv_reader = csv.reader(csv_file.split("\n"))
    for line in csv_reader:
        count += 1
        if len(line) == 0:
            increment_summary_count(summary_count_dict, "BLANK", event["env"])
            continue
        if check_csv_format(line, expected_col_count, event["env"], count) and check_csv_values(line, event["env"]):
            lines[str(count)] = {"id": line[0], "name": line[1], "action": line[2]}
        else:
            increment_summary_count(summary_count_dict, "ERROR", event["env"])
    return lines


def report_summary_counts(summary_count_dict, env):
    log_for_audit(env, slack_summary_counts(summary_count_dict))


def slack_summary_counts(summary_count_dict):
    if summary_count_dict is not None:
        report = "updated:{0}, inserted:{1}, deleted:{2}, blank:{3}, errored:{4}".format(
            summary_count_dict[update_action],
            summary_count_dict[create_action],
            summary_count_dict[delete_action],
            summary_count_dict[blank_lines] if summary_count_dict[blank_lines] > 0 else 0,
            summary_count_dict[error_lines],
        )
    else:
        report = ""
    return report
