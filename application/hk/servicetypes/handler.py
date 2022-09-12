import psycopg2
import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime

data_column_count = 4

task_description = "Service types"
v_searchcapacitystatus = True
v_capacitymodel = "n/a"
v_capacityreset = "interval"


def request(event, context):
    start = datetime.utcnow()
    message.send_start_message(event, start)
    print("Event: {}".format(event))
    env = event["env"]
    filename = event["filename"]
    bucket = event["bucket"]
    db_connection = None
    logger.log_for_audit(event["env"], "action:task started")
    try:
        summary_count_dict = common.initialise_summary_count()
        db_connection = database.connect_to_database(env)
        csv_file = common.retrieve_file_from_bucket(bucket, filename, event, start)
        csv_data = common.process_file(csv_file, event, data_column_count, summary_count_dict)
        if csv_data == {}:
            message.send_failure_slack_message(event, start, summary_count_dict)
        else:
            process_extracted_data(db_connection, csv_data, summary_count_dict, event)
            message.send_success_slack_message(event, start, summary_count_dict)
        common.report_summary_counts(summary_count_dict, env)
        logger.log_for_audit(event["env"], "action:task complete")
    except Exception as e:
        logger.log_for_error(env, "Problem {}".format(e))
        message.send_failure_slack_message(event, start)
    finally:
        database.close_connection(env, db_connection)
        common.archive_file(bucket, filename, event, start)
    return task_description + " execution completed"


def extract_query_data_from_csv(lines):
    """
    Maps data from csv and derives data NOT in the csv
    """
    query_data = {}
    for row_number, row_data in lines.items():

        data_dict = {}
        try:
            data_dict["id"] = row_data["id"]
            data_dict["name"] = row_data["name"]
            data_dict["nationalranking"] = row_data["nationalranking"]
            data_dict["searchcapacitystatus"] = v_searchcapacitystatus
            data_dict["capacitymodel"] = v_capacitymodel
            data_dict["capacityreset"] = v_capacityreset
            data_dict["action"] = row_data["action"].upper()
        except Exception as ex:
            logger.log_for_audit("CSV data invalid " + ex)
        query_data[str(row_number)] = data_dict
    return query_data


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
        insert into pathwaysdos.servicetypes
        (id, name, nationalranking, searchcapacitystatus, capacitymodel, capacityreset)
        values (%s, %s, %s, %s, %s, %s, %s)
        returning id, name, nationalranking, searchcapacitystatus, capacitymodel, capacityreset;
    """
    data = (
        row_values["id"],
        row_values["name"],
        row_values["nationalranking"],
        row_values["searchcapacitystatus"],
        row_values["capacitymodel"],
        row_values["capacityreset"],
    )
    return query, data


def update_query(row_values):
    query = """
        update pathwaysdos.servicetypes
        set name = (%s),
        nationalranking = (%s),
        searchcapacitystatus = (%s),
        capacitymodel = (%s),
        capacityreset = (%s)
        where id = (%s);
    """
    data = (
        row_values["name"],
        row_values["nationalranking"],
        row_values["searchcapacitystatus"],
        row_values["capacitymodel"],
        row_values["capacityreset"],
        row_values["id"],
    )
    return query, data


def delete_query(row_values):
    query = """
        delete from pathwaysdos.servicetypes where id = (%s)
    """
    data = (row_values["id"],)
    return query, data


def process_extracted_data(db_connection, row_data, summary_count_dict, event):
    for row_number, row_values in row_data.items():
        try:
            record_exists = database.does_record_exist(db_connection, row_values, "servicetypes", event["env"])
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
                event["env"],
                "Processing {0} data failed with | {1} | {2} | {3} | => {4}".format(
                    task_description, row_values["id"], row_values["name"], row_values["rank"], str(e)
                ),
            )
            raise e
