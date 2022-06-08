import csv
import psycopg2
import psycopg2.extras
import sys
from .utilities import s3, database, message
from datetime import datetime

sys.path.append(".")

from .utilities.logging import log_for_audit, log_for_error  # noqa

csv_column_count = 3
data_column_count = 4


def request(event, context):
    start = datetime.utcnow()
    message.send_start_message(event, start)
    print("Event: {}".format(event))
    env = event["env"]
    filename = event["filename"]
    bucket = event["bucket"]
    db_connection = connect_to_database(env, event, start)

    csv_file = retrieve_file_from_bucket(bucket, filename, event, start)
    extracted_data = extract_data_from_file(csv_file, filename, start)
    process_extracted_data(db_connection, extracted_data)
    cleanup(db_connection, bucket, filename, event, start)


def connect_to_database(env, event, start):
    db = database.DB()
    log_for_audit("Setting DB connection details")
    if not db.db_set_connection_details(env, event, start):
        log_for_error("Error DB Paramater(s) not found in secrets store.")
        message.send_failure_slack_message(event, start)
        raise ValueError("One or more DB Parameters not found in secrets store")
    return db.db_connect(event, start)


def retrieve_file_from_bucket(bucket, filename, event, start):
    log_for_audit("Looking in {} for {} file".format(bucket, filename))
    s3_bucket = s3.S3
    return s3_bucket.get_object(bucket, filename, event, start)


def extract_data_from_file(csv_file, event, start):
    lines = {}
    count = 0
    csv_reader = csv.reader(csv_file.split("\n"))
    for line in csv_reader:
        count += 1
        if len(line) > 0:
            query_data = extract_query_data_from_csv(line)
            if len(query_data) != data_column_count:
                log_for_error(
                    "Problem constructing data from csv expecting {} items but have {}".format(
                        str(data_column_count), str(len(query_data))
                    ),
                )
                message.send_failure_slack_message(event, start)
                raise IndexError("Unexpected data in csv file")
            lines[str(count)] = query_data
    return lines


def process_extracted_data(db_connection, row_data):
    for row_number, row_values in row_data.items():
        try:
            record_exists = does_record_exist(db_connection, row_values)
            if valid_action(record_exists, row_values):
                query, data = generate_db_query(row_values)
                execute_db_query(db_connection, query, data, row_number, row_values)
        except Exception as e:
            log_for_error(
                "Processing symptom group data failed with |{0}|{1}|{2}| => {3}".format(
                    row_values["csv_sgid"], row_values["csv_name"], row_values["csv_zcode"], str(e)
                ),
            )
            raise e


def valid_action(record_exists, row_data):
    valid_action = False
    if record_exists and row_data["action"] in ("UPDATE", "DELETE"):
        valid_action = True
    if not record_exists and row_data["action"] in ("CREATE"):
        valid_action = True

    if not valid_action:
        log_for_error("Invalid action {} for the record with ID {}".format(row_data["action"], row_data["csv_sgid"]))
    return valid_action


def does_record_exist(db, row_dict):
    """
    Checks to see if symptom group already exists in db with the id
    """
    record_exists = False
    try:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as symptom_group_cur:
            select_query = """select * from pathwaysdos.symptomgroups where id=%s"""
            symptom_group_cur.execute(select_query, (str(row_dict["csv_sgid"]),))
            if symptom_group_cur.rowcount == 1:
                record_exists = True
    except Exception as e:
        log_for_error(
            "Select symptom group by id failed - {0} => {1}".format(row_dict["csv_sgid"], str(e)),
        )
        raise e
    return record_exists


def check_csv_format(csv_row):
    if len(csv_row) == csv_column_count:
        return True
    else:
        log_for_audit("CSV format invalid - invalid length")
        return False


def extract_query_data_from_csv(line):
    """
    Checks  maps data to db cols if correct
    """
    csv_dict = {}
    if check_csv_format(line):
        try:
            csv_sgid = line[0]
            if csv_sgid == "":
                csv_sgid = None
            else:
                csv_sgid = int(csv_sgid)
            csv_name = line[1]
            if csv_name == "":
                csv_name = None
                csv_zcode = False
            else:
                csv_zcode = csv_name.startswith("z2.0 - ")
            csv_action = line[2].upper()
            csv_dict["csv_sgid"] = csv_sgid
            csv_dict["csv_name"] = csv_name
            csv_dict["csv_zcode"] = csv_zcode
            csv_dict["action"] = csv_action
        except Exception as ex:
            log_for_audit("CSV data invalid " + ex)

    return csv_dict


def generate_db_query(row_values):
    if row_values["action"] in ("CREATE"):
        return create_query(row_values)
    elif row_values["action"] in ("UPDATE"):
        return update_query(row_values)
    elif row_values["action"] in ("DELETE"):
        return delete_query(row_values)
    else:
        log_for_error("Action {} not in approved list of actions".format(row_values["action"]))
        # message.send_failure_slack_message(event, start)
        raise psycopg2.DatabaseError("Database Action {} is invalid".format(row_values["action"]))


def create_query(row_values):
    query = """
        insert into pathwaysdos.symptomgroups(id,name,zcodeexists)
        values (%s, %s, %s)
        returning
        id,
        name,
        zcodeexists;
    """
    data = (row_values["csv_sgid"], row_values["csv_name"], row_values["csv_zcode"])
    return query, data


def update_query(row_values):
    query = """
        update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s) where id = (%s);
    """
    data = (row_values["csv_name"], row_values["csv_zcode"], row_values["csv_sgid"])
    return query, data


def delete_query(row_values):
    query = """
        delete from pathwaysdos.symptomgroups where id = (%s)
    """
    data = (row_values["csv_sgid"],)
    return query, data


def execute_db_query(db_connection, query, data, line, values):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query, data)
        db_connection.commit()
        log_for_audit("Action: {}, ID: {}, for symptomgroup {}".format(values["action"], values["id"], values["name"]))
    except Exception as e:
        log_for_error("Line {} in transaction failed. Rolling back".format(line))
        log_for_error("Error: {}".format(e))
        db_connection.rollback()
    finally:
        cursor.close()


def cleanup(db_connection, bucket, filename, event, start):
    # Close DB connection
    log_for_audit("Closing DB connection...")
    db_connection.close()
    # Archive file
    s3.S3.copy_object(bucket, filename, event, start)
    s3.S3.delete_object(bucket, filename, event, start)
    log_for_audit("Archived file {} to {}/archive/{}".format(filename, filename.split("/")[0], filename.split("/")[1]))
    # Send Slack Notification
    log_for_audit("Sending slack message...")
    message.send_success_slack_message(event, start)
