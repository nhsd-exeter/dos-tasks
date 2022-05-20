import csv
import psycopg2
from utilities import s3, logging, database, message
from datetime import datetime

start = datetime.utcnow()


def request(event, context):
    message.send_start_message(event, start)
    print("Event: {}".format(event))
    env = event["env"]
    filename = event["filename"]
    bucket = event["bucket"]
    db_connection = connect_to_database(env, event, start)
    csv_file = retrieve_file_from_bucket(bucket, filename, event, start)
    lines = process_file(csv_file, event, start)
    for row in lines:
        if check_table_for_id(db_connection, row, filename, event, start):
            query, data = generate_db_query(row, event, start)
            execute_db_query(db_connection, query, data, row)
    cleanup(db_connection, bucket, filename, event, start)


def connect_to_database(env, event, start):
    db = database.DB()
    logging.log_for_audit("Setting DB connection details")
    if not db.db_set_connection_details(env, event, start):
        logging.log_for_error("Error DB Paramater(s) not found in secrets store.")
        message.send_failure_slack_message(event, start)
        raise ValueError("DB Paramater(s) not found in secrets store")
    return db.db_connect(event, start)


def retrieve_file_from_bucket(bucket, filename, event, start):
    logging.log_for_audit("Looking in {} for {} file".format(bucket, filename))
    s3_bucket = s3.S3
    return s3_bucket.get_object(bucket, filename, event, start)


def process_file(csv_file, event, start):
    lines = {}
    count = 0
    csv_reader = csv.reader(csv_file.split("\n"))
    for line in csv_reader:
        count += 1
        if len(line) == 0:
            continue
        if len(line) != 3:
            logging.log_for_error("Incorrect line format, should be 3 but is {}".format(len(line)))
            message.send_failure_slack_message(event, start)
            raise IndexError("Unexpected data in csv file")
        lines[str(count)] = {"id": line[0], "name": line[1], "action": line[2]}
    return lines


def generate_db_query(row, event, start):
    if row["action"] == ("CREATE" or "INSERT"):
        return create_query(row)
    elif row["action"] == ("UPDATE" or "MODIFY"):
        return update_query(row)
    elif row["action"] == ("DELETE" or "REMOVE"):
        return delete_query(row)
    else:
        logging.log_for_error("Action {} not in approved list of actions".format(row["action"]))
        message.send_failure_slack_message(event, start)
        raise psycopg2.DatabaseError("Database Action {} is invalid".format(row["action"]))


def create_query(row):
    query = """
        insert into pathwaysdos.referralroles (id, name) values (%s, %s)
        returning id, name;
    """
    data = (
        row["id"],
        row["name"],
    )
    return query, data


def update_query(row):
    query = """
        update pathwaysdos.referralroles set name = (%s) where id = (%s);
    """
    data = (
        row["id"],
        row["name"],
    )
    return query, data


def delete_query(row):
    query = """
        delete from pathwaysdos.referralroles where id = (%s)
    """
    data = (row["id"],)
    return query, data


def check_table_for_id(db_connection, line, filename, event, start):
    try:
        with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            select_query = """select * from pathwaysdos.referralroles where id=%s"""
            cursor.execute(select_query, (line["id"],))
            if cursor.rowcount == 0:
                record_exists = True
            else:
                record_exists = False
    except Exception as e:
        logging.log_for_error("Error checking table referralroles for ID {}. Error: {}".format(line["id"], e))
        message.send_failure_slack_message(event, start)
        raise e
    if record_exists and line["action"] == ("UPDATE" or "MODIFY" or "DELETE" or "REMOVE"):
        return True
    elif not record_exists and line["action"] == ("CREATE" or "INSERT"):
        return True
    else:
        if record_exists:
            logging.log_for_error(
                "Action {} but the record with ID {} already exists. File: {} | Line: {} | Name: {}".format(
                    line["action"], line["id"], filename, line.key, line["name"]
                )
            )
        elif not record_exists:
            logging.log_for_error(
                "Action {} but the record with ID {} does not exist. File: {} | Line: {} | Name: {}".format(
                    line["action"], line["id"], filename, line.key, line["name"]
                )
            )
        return False


def execute_db_query(db_connection, query, data, line):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query, data)
        db_connection.commit()
        logging.log_for_audit(
            "Action: {}, ID: {}, for referralrole {}".format(query["action"], query["id"], query["name"])
        )
    except Exception as e:
        logging.log_for_error("Line {} in transaction failed. Rolling back".format(line.key))
        logging.log_for_error("Error: {}".format(e))
        db_connection.rollback()
    finally:
        cursor.close()


def cleanup(db_connection, bucket, filename, event, start):
    # Close DB connection
    logging.log_for_audit("Closing DB connection...")
    db_connection.close()
    # Archive file
    s3.S3.copy_object(bucket, filename, event, start)
    s3.S3.delete_object(bucket, filename, event, start)
    logging.log_for_audit("Archived file {} to /archive/{}".format(filename, filename))
    # Send Slack Notification
    logging.log_for_audit("Sending slack message...")
    message.send_success_slack_message(event, start)
