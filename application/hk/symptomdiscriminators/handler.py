import psycopg2
import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime

csv_column_count = 3
data_column_count = 3
create_action = "CREATE"
update_action = "UPDATE"
delete_action = "DELETE"

task_description = "Symptom discriminators"


def request(event, context):
    start = datetime.utcnow()
    message.send_start_message(event, start)
    print("Event: {}".format(event))
    env = event["env"]
    filename = event["filename"]
    bucket = event["bucket"]
    summary_count_dict = common.initialise_summary_count()
    db_connection = database.connect_to_database(env, event, start)
    csv_file = common.retrieve_file_from_bucket(bucket, filename, event, start)
    csv_data = common.process_file(csv_file, event, start, data_column_count)
    # lines = common.process_file(csv_file, event, start, 3)
    extracted_data = extract_query_data_from_csv(csv_data)
    process_extracted_data(db_connection, extracted_data, summary_count_dict, event, start)
    common.report_summary_counts(task_description, summary_count_dict)
    common.cleanup(db_connection, bucket, filename, event, start)
    return task_description + " execution successful"


def extract_query_data_from_csv(csv_data):
    """
    Maps data from csv and derives zcode data NOT in the csv
    """
    query_data = {}
    for row_number, row_data in csv_data.items():

        data_dict = {}
        try:
            data_dict["id"] = row_data["id"]
            data_dict["name"] = row_data["name"]
            data_dict["action"] = row_data["action"].upper()
        except Exception as ex:
            logger.log_for_audit("CSV data invalid " + ex)
        query_data[str(row_number)] = data_dict
    return query_data


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
        row_values["name"],
    )
    return query, data


def update_query(row_values):
    query = """
        update pathwaysdos.symptomdiscriminators set description = (%s) where id = (%s);
    """
    data = (
        row_values["name"],
        row_values["id"],
    )
    return query, data


def delete_query(row_values):
    query = """
        delete from pathwaysdos.symptomdiscriminators where id = (%s)
    """
    data = (row_values["id"],)
    return query, data


def process_extracted_data(db_connection, row_data, summary_count_dict, event, start):
    for row_number, row_values in row_data.items():
        try:
            record_exists = database.does_record_exist(db_connection, row_values, "symptomdiscriminators")
            if common.valid_action(record_exists, row_values):
                query, data = generate_db_query(row_values, event, start)
                database.execute_db_query(db_connection, query, data, row_number, row_values, summary_count_dict)
        except Exception as e:
            logger.log_for_error(
                "Processing {0} data failed with |{1}|{2}| => {3}".format(
                    task_description, row_values["id"], row_values["description"], str(e)
                ),
            )
            raise e
