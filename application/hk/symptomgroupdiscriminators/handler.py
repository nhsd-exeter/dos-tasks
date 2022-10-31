import psycopg2
import psycopg2.extras
from utilities import logger, message, common, database, common_file_processing
from datetime import datetime

csv_column_count = 3
data_column_count = 3

task_description = "Symptom group symptom discriminators"


def request(event, context):
    start = datetime.utcnow()
    message.send_start_message(event, start)
    print("Event: {}".format(event))
    env = event["env"]
    filename = event["filename"]
    bucket = event["bucket"]
    logger.log_for_audit(env, "action=task started")
    try:
        summary_count_dict = common.initialise_summary_count()
        db_connection = database.connect_to_database(env)
        csv_file = common.retrieve_file_from_bucket(bucket, filename, event, start)
        csv_data = common_file_processing.process_ids_file(csv_file, event, csv_column_count, summary_count_dict)
        if csv_data == {}:
            message.send_failure_slack_message(event, start, summary_count_dict)
        else:
            process_extracted_data(db_connection, csv_data, summary_count_dict, event)
            message.send_success_slack_message(event, start, summary_count_dict)
        common.report_summary_counts(summary_count_dict, env)
        logger.log_for_audit(env, "action=task complete")
    except Exception as e:
        logger.log_for_error(env, "Problem {}".format(e))
        message.send_failure_slack_message(event, start)
    finally:
        if db_connection is not None:
            database.close_connection(env, db_connection)
        common.archive_file(bucket, filename, event, start)
    return task_description + " execution completed"


def generate_db_query(row_values, env):
    if row_values["action"] == ("CREATE"):
        return create_query(row_values)
    elif row_values["action"] == ("DELETE"):
        return delete_query(row_values)
    else:
        logger.log_for_error(env, "action=validation | {} not in approved list of actions".format(row_values["action"]))
        raise psycopg2.DatabaseError("Database Action {} is invalid".format(row_values["action"]))


def create_query(row_values):
    query = """
        insert into pathwaysdos.symptomgroupsymptomdiscriminators
        (symptomgroupid, symptomdiscriminatorid) values (%s, %s)
        returning symptomgroupid, symptomdiscriminatorid;
    """
    data = (
        row_values["id1"],
        row_values["id2"],
    )
    return query, data


def delete_query(row_values):
    query = """
        delete from pathwaysdos.symptomgroupsymptomdiscriminators
        where symptomgroupid = (%s) and symptomdiscriminatorid = (%s)
    """
    data = (
        row_values["id1"],
        row_values["id2"],
    )
    return query, data


def record_exists_query(row_values):
    query = """
        select * from pathwaysdos.symptomgroupsymptomdiscriminators
        where symptomgroupid = (%s) and symptomdiscriminatorid = (%s)
    """
    data = (
        row_values["id1"],
        row_values["id2"],
    )
    return query, data


def process_extracted_data(db_connection, row_data, summary_count_dict, event):
    for row_number, row_values in row_data.items():
        try:
            record_exists = does_sgd_record_exist(db_connection, row_values, event["env"])
            if common.valid_action(record_exists, row_values, event["env"], "UPDATE"):
                query, data = generate_db_query(row_values, event["env"])
                database.execute_db_query(
                    db_connection, query, data, row_number, row_values, summary_count_dict, event["env"]
                )
            else:
                common.increment_summary_count(summary_count_dict, "ERROR", event["env"])
        except Exception as e:
            logger.log_for_error(
                event["env"],
                "Processing {0} data failed with |{1}|{2}| => {3}".format(
                    task_description, row_values["id1"], row_values["id2"], str(e)
                ),
            )
            raise e


def does_sgd_record_exist(db_connection, row_values, env):
    """
    Checks to see if record already exists in db table with the symptomgroupid and symptomdiscriminatorid
    """
    record_exists = False
    try:
        with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query, data = record_exists_query(row_values)
            cursor.execute(query, data)
            if cursor.rowcount != 0:
                record_exists = True
    except (Exception, psycopg2.Error) as e:
        logger.log_for_error(
            env,
            "Select from symptomgroupsymptomdiscriminators by sgid and sdid failed - {0} , {1} => {2}".format(
                data["id1"], data["id2"], str(e)
            ),
        )
        raise e
    return record_exists
