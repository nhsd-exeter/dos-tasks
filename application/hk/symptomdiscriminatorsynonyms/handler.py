import psycopg2
import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime

csv_column_count = 3
data_column_count = 3

task_description = "Symptom discriminator synonyms"


def request(event, context):
    start = datetime.utcnow()
    message.send_start_message(event, start)
    print("Event: {}".format(event))
    env = event["env"]
    filename = event["filename"]
    bucket = event["bucket"]
    summary_count_dict = common.initialise_summary_count()
    db_connection = database.connect_to_database(env)
    csv_file = common.retrieve_file_from_bucket(bucket, filename, event, start)
    csv_data = common.process_file(csv_file, event, csv_column_count, summary_count_dict)
    process_extracted_data(env, db_connection, csv_data, summary_count_dict, event, start)
    common.report_summary_counts(task_description, env)
    return task_description + " execution successful"


def generate_db_query(env, row_values, event, start):
    if row_values["action"] == ("CREATE"):
        return create_query(row_values)
    elif row_values["action"] == ("UPDATE"):
        return update_query(row_values)
    elif row_values["action"] == ("DELETE"):
        return delete_query(row_values)
    else:
        logger.log_for_error(env, "action:validation | {} not in approved list of actions".format(row_values["action"]))
        raise psycopg2.DatabaseError("Database Action {} is invalid".format(row_values["action"]))


def create_query(row_values):
    query = """
        insert into pathwaysdos.symptomdiscriminatorsynonyms (symptomdiscriminatorid, name) values (%s, %s)
        returning id, name;
    """
    data = (
        row_values["id"],
        row_values["name"],
    )
    return query, data


def update_query(row_values):
    query = """
        update pathwaysdos.symptomdiscriminatorsynonyms set name = (%s) where symptomdiscriminatorid = (%s);
    """
    data = (
        row_values["name"],
        row_values["id"],
    )
    return query, data


def delete_query(row_values):
    query = """
        delete from pathwaysdos.symptomdiscriminatorsynonyms where symptomdiscriminatorid = (%s)
    """
    data = (row_values["id"],)
    return query, data


def process_extracted_data(env, db_connection, row_data, summary_count_dict, event, start):
    for row_number, row_values in row_data.items():
        try:
            record_exists = database.does_record_exist(db_connection, row_values, "symptomdiscriminatorsynonyms", event["env"])
            if common.valid_action(record_exists, row_values, event["env"]):
                query, data = generate_db_query(row_values, event["env"])
                database.execute_db_query(
                    db_connection, query, data, row_number, row_values, summary_count_dict, event["env"]
                )
            else:
                common.increment_summary_count(summary_count_dict, "ERROR", event["env"])
        except Exception as e:
            logger.log_for_error(  event["env"],
                "Processing {0} data failed with |{1}|{2}| => {3}".format(
                    task_description, row_values["id"], row_values["name"], str(e)
                ),
            )
            raise e
