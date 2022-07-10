import psycopg2
import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime

csv_column_count = 3
data_column_count = 3

task_description = "Referral roles"


def request(event, context):
    start = datetime.utcnow()
    message.send_start_message(event, start)
    print("Event: {}".format(event))
    env = event["env"]
    filename = event["filename"]
    bucket = event["bucket"]
    try:
        summary_count_dict = common.initialise_summary_count()
        db_connection = database.connect_to_database(env, event, start)
        csv_file = common.retrieve_file_from_bucket(bucket, filename, event, start)
        csv_data = common.process_file(csv_file, event, start, data_column_count, summary_count_dict)
        process_extracted_data(db_connection, csv_data, summary_count_dict, event)
        common.report_summary_counts(summary_count_dict, env)
        logger.log_for_audit(event["env"], "action:close DB connection")
        message.send_success_slack_message(event, start, summary_count_dict)
    except Exception as e:
        logger.log_for_error(env, "Problem {}".format(e))
        message.send_failure_slack_message(event, start)
    finally:
        database.close_connection(event, db_connection)
        common.archive_file(bucket, filename, event, start)
    return task_description + " execution completed"


def generate_db_query(row_values, env):
    if row_values["action"] in ("CREATE", "INSERT"):
        return create_query(row_values)
    elif row_values["action"] in ("UPDATE", "MODIFY"):
        return update_query(row_values)
    elif row_values["action"] in ("DELETE", "REMOVE"):
        return delete_query(row_values)
    else:
        logger.log_for_error(env, "action:validation | {} not in approved list of actions".format(row_values["action"]))
        raise psycopg2.DatabaseError("Database Action {} is invalid".format(row_values["action"]))


def create_query(row_values):
    query = """
        insert into pathwaysdos.referralroles (id, name) values (%s, %s)
        returning id, name;
    """
    data = (
        row_values["id"],
        row_values["name"],
    )
    return query, data


def update_query(row_values):
    query = """
        update pathwaysdos.referralroles set name = (%s) where id = (%s);
    """
    data = (
        row_values["name"],
        row_values["id"],
    )
    return query, data


def delete_query(row_values):
    query = """
        delete from pathwaysdos.referralroles where id = (%s)
    """
    data = (row_values["id"],)
    return query, data


def process_extracted_data(db_connection, row_data, summary_count_dict, event):
    for row_number, row_values in row_data.items():
        try:
            record_exists = database.does_record_exist(db_connection, row_values, "referralroles", event["env"])
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
                "Processing {0} data failed with |{1}|{2}| => {3}".format(
                    task_description, row_values["id"], row_values["name"], str(e)
                ),
            )
            raise e
