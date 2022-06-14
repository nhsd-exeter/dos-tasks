import csv
import psycopg2
import psycopg2.extras
from utilities import s3, database, message
from datetime import datetime

from utilities.common_task import check_csv_format, valid_action
from utilities.logger import log_for_audit, log_for_error  # noqa

csv_column_count = 3
data_column_count = 4
create_action = "CREATE"
update_action = "UPDATE"
delete_action = "DELETE"
summary_count_dict = {}


def request(event, context):
    start = datetime.utcnow()
    message.send_start_message(event, start)
    print("Event: {}".format(event))
    env = event["env"]
    filename = event["filename"]
    bucket = event["bucket"]
    initialise_summary_count()
    db_connection = connect_to_database(env, event, start)

    csv_file = retrieve_file_from_bucket(bucket, filename, event, start)
    extracted_data = extract_data_from_file(csv_file, filename, start)
    process_extracted_data(db_connection, extracted_data)
    log_for_audit(
        "Symptom groups updated: {0}, inserted: {1}, deleted: {2}".format(
            summary_count_dict[update_action], summary_count_dict[create_action], summary_count_dict[delete_action]
        )
    )
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
    s3_bucket = s3.S3()
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
                    row_values["id"], row_values["name"], row_values["zcode"], str(e)
                ),
            )
            raise e


# TODO move to util with parameterised query or table name
def does_record_exist(db, row_dict):
    """
    Checks to see if symptom group already exists in db with the id
    """
    record_exists = False
    try:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            select_query = """select * from pathwaysdos.symptomgroups where id=%s"""
            cursor.execute(select_query, (row_dict["id"],))
            if cursor.rowcount != 0:
                record_exists = True
    except (Exception, psycopg2.Error) as e:
        log_for_error(
            "Select symptom group by id failed - {0} => {1}".format(row_dict["id"], str(e)),
        )
        raise e
    return record_exists


def extract_query_data_from_csv(line):
    """
    Checks  maps data to db cols if correct
    """
    csv_dict = {}
    if check_csv_format(line, csv_column_count):
        try:
            id = line[0]
            if id == "":
                id = None
            else:
                id = int(id)
            name = line[1]
            if name == "":
                name = None
                zcode = False
            else:
                zcode = name.startswith("z2.0 - ")
            csv_action = line[2].upper()
            csv_dict["id"] = id
            csv_dict["name"] = name
            csv_dict["zcode"] = zcode
            csv_dict["action"] = csv_action
        except Exception as ex:
            log_for_audit("CSV data invalid " + ex)
    return csv_dict


# TODO move to util but call back to here for query content
def generate_db_query(row_values):
    if row_values["action"] in ("CREATE"):
        return create_query(row_values)
    elif row_values["action"] in ("UPDATE"):
        return update_query(row_values)
    elif row_values["action"] in ("DELETE"):
        return delete_query(row_values)
    else:
        log_for_error("Action {} not in approved list of actions".format(row_values["action"]))
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
    data = (row_values["id"], row_values["name"], row_values["zcode"])
    return query, data


def update_query(row_values):
    query = """
        update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s) where id = (%s);
    """
    data = (row_values["name"], row_values["zcode"], row_values["id"])
    return query, data


def delete_query(row_values):
    query = """
        delete from pathwaysdos.symptomgroups where id = (%s)
    """
    data = (row_values["id"],)
    return query, data


def execute_db_query(db_connection, query, data, line, values):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query, data)
        db_connection.commit()
        increment_summary_count(values)
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
    s3_bucket = s3.S3()
    s3_bucket.copy_object(bucket, filename, event, start)
    s3_bucket.delete_object(bucket, filename, event, start)
    log_for_audit("Archived file {} to {}/archive/{}".format(filename, filename.split("/")[0], filename.split("/")[1]))
    # Send Slack Notification
    log_for_audit("Sending slack message...")
    message.send_success_slack_message(event, start)


# TODO move to util if other jobs report counts
def initialise_summary_count():
    summary_count_dict[create_action] = 0
    summary_count_dict[update_action] = 0
    summary_count_dict[delete_action] = 0


#  TODO move to util if other jobs report counts
def increment_summary_count(values):
    if values["action"] in [create_action, update_action, delete_action]:
        summary_count_dict[values["action"]] = summary_count_dict[values["action"]] + 1
    else:
        log_for_error(
            "Can't increment count for action {0}. Valid actions are {1},{2},{3}".format(
                values["action"], create_action, update_action, delete_action
            )
        )
