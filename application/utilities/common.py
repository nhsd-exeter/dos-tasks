from utilities.database import DB
from utilities.s3 import S3
from utilities.logger import log_for_audit, log_for_error  # noqa
from utilities.message import send_success_slack_message, send_failure_slack_message


# TODO rename as common
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


def connect_to_database(env, event, start):
    db = DB()
    log_for_audit("Setting DB connection details")
    if not db.db_set_connection_details(env, event, start):
        log_for_error("Error DB Parameter(s) not found in secrets store.")
        send_failure_slack_message(event, start)
        raise ValueError("DB Parameter(s) not found in secrets store")
    return db.db_connect(event, start)


def retrieve_file_from_bucket(bucket, filename, event, start):
    log_for_audit("Looking in {} for {} file".format(bucket, filename))
    s3_bucket = S3()
    return s3_bucket.get_object(bucket, filename, event, start)
