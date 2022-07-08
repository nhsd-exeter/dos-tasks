import psycopg2
import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime

csv_column_count = 3
data_column_count = 4

task_description = "Symptom Groups"


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
    csv_data = common.process_file(csv_file, event, start, 3, summary_count_dict)
    extracted_data = extract_query_data_from_csv(csv_data, env)
    process_extracted_data(db_connection, extracted_data, summary_count_dict, event)
    common.report_summary_counts(summary_count_dict, env)
    common.cleanup(db_connection, bucket, filename, event, start, summary_count_dict)
    return task_description + " execution successful"


# TODO consider moving to common or refactoring
def process_extracted_data(db_connection, row_data, summary_count_dict, event):
    for row_number, row_values in row_data.items():
        try:
            record_exists = database.does_record_exist(db_connection, row_values, "symptomgroups", event["env"])
            if common.valid_action(record_exists, row_values, event["env"]):
                query, data = generate_db_query(row_values, event["env"])
                database.execute_db_query(
                    db_connection, query, data, row_number, row_values, summary_count_dict, event["env"]
                )
            else:
                common.increment_summary_count(summary_count_dict, "ERROR", event["env"])
        except Exception as e:
            common.increment_summary_count(summary_count_dict, "ERROR", event["env"])
            logger.log_for_error(
                "Processing {0} data failed with | {1} | {2} | {3} | => {4}".format(
                    task_description, row_values["id"], row_values["name"], row_values["zcode"], str(e)
                ),
            )
            raise e


def extract_query_data_from_csv(lines, env):
    """
    Maps data from csv and derives zcode data NOT in the csv
    """
    query_data = {}
    for row_number, row_data in lines.items():

        data_dict = {}
        try:
            data_dict["id"] = row_data["id"]
            data_dict["name"] = row_data["name"]
            data_dict["zcode"] = row_data["name"].startswith("z2.0 - ")
            data_dict["action"] = row_data["action"].upper()
        except Exception as ex:
            logger.log_for_audit(env, "action:validation | CSV data invalid | " + ex)
        query_data[str(row_number)] = data_dict
    return query_data


# TODO consider moving to common or refactoring
def generate_db_query(row_values, env):
    if row_values["action"] in ("CREATE"):
        return create_query(row_values)
    elif row_values["action"] in ("UPDATE"):
        return update_query(row_values)
    elif row_values["action"] in ("DELETE"):
        return delete_query(row_values)
    else:
        logger.log_for_error(env, "action:validation | {} not in approved list of actions".format(row_values["action"]))
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


# TODO move to util
def delete_query(row_values):
    query = """
        delete from pathwaysdos.symptomgroups where id = (%s)
    """
    data = (row_values["id"],)
    return query, data
