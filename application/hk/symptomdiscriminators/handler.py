import psycopg2
import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime

csv_column_count = 3
data_column_count = 3
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
    db_connection = database.connect_to_database(env, event, start)
    csv_file = common.retrieve_file_from_bucket(bucket, filename, event, start)
    lines = common.process_file(csv_file, event, start, 3)
    for row, values in lines.items():
        if check_table_for_id(db_connection, row, values, filename, event, start):
            query, data = generate_db_query(values, event, start)
            execute_db_query(db_connection, query, data, row, values)
    logger.log_for_audit(
        "Symptom discriminators updated: {0}, inserted: {1}, deleted: {2}".format(
            summary_count_dict[update_action], summary_count_dict[create_action], summary_count_dict[delete_action]
        )
    )
    common.cleanup(db_connection, bucket, filename, event, start)
    return "Symptom discriminators execution successful"


# def process_file(csv_file, event, start):
#     lines = {}
#     count = 0
#     csv_reader = csv.reader(csv_file.split("\n"))
#     for line in csv_reader:
#         count += 1
#         if not common.check_csv_format(line, csv_column_count):
#             logger.log_for_error("Incorrect line format, should be 3 but is {}".format(len(line)))
#         else:
#             lines[str(count)] = {"id": line[0], "description": line[1], "action": line[2]}
#     if lines == {}:
#         message.send_failure_slack_message(event, start)
#     return lines


def generate_db_query(row_values, event, start):
    if row_values["action"] == ("CREATE"):
        return create_query(row_values)
    elif row_values["action"] == ("UPDATE"):
        return update_query(row_values)
    elif row_values["action"] == ("DELETE"):
        return delete_query(row_values)
    else:
        logger.log_for_error("Action {} not in approved list of actions".format(row_values["action"]))
        message.send_failure_slack_message(event, start)
        raise psycopg2.DatabaseError("Database Action {} is invalid".format(row_values["action"]))


def create_query(row_values):
    query = """
        insert into pathwaysdos.symptomdiscriminators (id, description) values (%s, %s)
        returning id, description;
    """
    data = (
        row_values["id"],
        row_values["description"],
    )
    return query, data


def update_query(row_values):
    query = """
        update pathwaysdos.symptomdiscriminators set description = (%s) where id = (%s);
    """
    data = (
        row_values["description"],
        row_values["id"],
    )
    return query, data


def delete_query(row_values):
    query = """
        delete from pathwaysdos.symptomdiscriminators where id = (%s)
    """
    data = (row_values["id"],)
    return query, data


def check_table_for_id(db_connection, line, values, filename, event, start):
    try:
        with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            select_query = """select * from pathwaysdos.symptomdiscriminators where id=%s"""
            cursor.execute(select_query, (values["id"],))
            if cursor.rowcount != 0:
                record_exists = True
            else:
                record_exists = False
    except Exception as e:
        logger.log_for_error("Error checking table symptomdiscriminators for ID {}. Error: {}".format(values["id"], e))
        message.send_failure_slack_message(event, start)
        raise e
    if record_exists and values["action"] in ("UPDATE", "DELETE"):
        return True
    elif not record_exists and values["action"] in ("CREATE"):
        return True
    else:
        if record_exists:
            logger.log_for_error(
                "Action {} but the record with ID {} already exists. File: {} | Line: {} | Description: {}".format(
                    values["action"], values["id"], filename, line, values["description"]
                )
            )
        elif not record_exists:
            logger.log_for_error(
                "Action {} but the record with ID {} does not exist. File: {} | Line: {} | Description: {}".format(
                    values["action"], values["id"], filename, line, values["description"]
                )
            )
        return False


def execute_db_query(db_connection, query, data, line, values):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query, data)
        db_connection.commit()
        increment_summary_count(values)
        logger.log_for_audit(
            "Action: {}, ID: {}, for symptom discriminators {}".format(
                values["action"], values["id"], values["description"]
            )
        )
    except Exception as e:
        logger.log_for_error("Line {} in transaction failed. Rolling back".format(line))
        logger.log_for_error("Error: {}".format(e))
        db_connection.rollback()
    finally:
        cursor.close()


def initialise_summary_count():
    summary_count_dict[create_action] = 0
    summary_count_dict[update_action] = 0
    summary_count_dict[delete_action] = 0


def increment_summary_count(values):
    if values["action"] in [create_action, update_action, delete_action]:
        summary_count_dict[values["action"]] = summary_count_dict[values["action"]] + 1
    else:
        logger.log_for_error(
            "Can't increment count for action {0}. Valid actions are {1},{2},{3}".format(
                values["action"], create_action, update_action, delete_action
            )
        )
