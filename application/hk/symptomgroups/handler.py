import psycopg2
import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime

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
    summary_count_dict = common.initialise_summary_count()
    db_connection = database.connect_to_database(env, event, start)
    csv_file = common.retrieve_file_from_bucket(bucket, filename, event, start)
    csv_data = common.process_file(csv_file, event, start, 3)
    extracted_data = extract_query_data_from_csv(csv_data)
    process_extracted_data(db_connection, extracted_data)
    logger.log_for_audit(
        "Symptom groups updated: {0}, inserted: {1}, deleted: {2}".format(
            summary_count_dict[update_action], summary_count_dict[create_action], summary_count_dict[delete_action]
        )
    )
    common.cleanup(db_connection, bucket, filename, event, start)
    return "Symptom groups execution successful"


# TODO consider moving to common ultimately
# def process_file(csv_file):
#     lines = {}
#     count = 0
#     csv_reader = csv.reader(csv_file.split("\n"))
#     for line in csv_reader:
#         count += 1
#         if len(line) > 0:
#             query_data = extract_query_data_from_csv(line)
#             if len(query_data) != data_column_count:
#                 logger.log_for_audit(
#                     "Problem constructing data from line {} of csv expecting {} items but have {}".format(
#                         str(count), str(csv_column_count), str(len(line))
#                     ),
#                 )
#             else:
#                 lines[str(count)] = query_data
#     return lines


# TODO move to common
def process_extracted_data(db_connection, row_data):
    for row_number, row_values in row_data.items():
        try:
            record_exists = database.does_record_exist(db_connection, row_values)
            if common.valid_action(record_exists, row_values):
                query, data = generate_db_query(row_values)
                execute_db_query(db_connection, query, data, row_number, row_values)
        except Exception as e:
            logger.log_for_error(
                "Processing symptom group data failed with |{0}|{1}|{2}| => {3}".format(
                    row_values["id"], row_values["name"], row_values["zcode"], str(e)
                ),
            )
            raise e


def extract_query_data_from_csv(lines):
    """
    Checks  maps data to db cols if correct
    """
    query_data = {}
    for row_number, row_data in lines.items():

        data_dict = {}
        try:
            data_dict["id"] = row_data["id"]
            data_dict["name"] = row_data["description"]
            data_dict["zcode"] = row_data["description"].startswith("z2.0 - ")
            data_dict["action"] = row_data["action"].upper()
        except Exception as ex:
            logger.log_for_audit("CSV data invalid " + ex)
        query_data[str(row_number)] = data_dict
    return query_data


# TODO move to util but call back to here for query content
def generate_db_query(row_values):
    if row_values["action"] in ("CREATE"):
        return create_query(row_values)
    elif row_values["action"] in ("UPDATE"):
        return update_query(row_values)
    elif row_values["action"] in ("DELETE"):
        return delete_query(row_values)
    else:
        logger.log_for_error("Action {} not in approved list of actions".format(row_values["action"]))
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


# TODO move to database
def execute_db_query(db_connection, query, data, line, values):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query, data)
        db_connection.commit()
        common.increment_summary_count(summary_count_dict, values)
        logger.log_for_audit(
            "Action: {}, ID: {}, for symptomgroup {}".format(values["action"], values["id"], values["name"])
        )
    except Exception as e:
        logger.log_for_error("Line {} in transaction failed. Rolling back".format(line))
        logger.log_for_error("Error: {}".format(e))
        db_connection.rollback()
    finally:
        cursor.close()
