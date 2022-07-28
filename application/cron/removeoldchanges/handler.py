# import psycopg2
# import psycopg2.extras
from utilities import logger, database, cron_common
from datetime import datetime
import os

task_description = "Remove old changes"
threshold_in_days = 90
# threshold_in_seconds = threshold_in_days * 60 * 60 * 24
# threshold_in_seconds = 7776000
# ignore_org_types = [1, 2]
# interval_type = "interval"
# new_status = 1
# modified_by = "ROBOT"
# modified_by_id = 9
# notes = ""


def request(event, context):
    print("Event: {}".format(event))
    env = os.getenv("DB_NAME")
    event_id = event["id"]
    event_time = event["time"]
    logger.log_for_audit(env, "operation:start")
    logger.log_for_audit(env, "Event id: {0}, event time: {1} , environment: {2}".format(event_id, event_time, env))
    db_connection = database.connect_to_database(env)
    remove_old_changes(env, db_connection)
    cron_common.cron_cleanup(env, db_connection)
    logger.log_for_audit(env, "operation:end")
    return task_description + " execution successful"


def remove_old_changes(env, db_connection):

    try:
        threshold_date = getThresholdDate
        delete_query, data = generate_delete_query(threshold_date)
        deleted_services = database.execute_cron_query(db_connection, delete_query, data)
        log_deleted_services(env, db_connection, deleted_services)
    except KeyError as e:
        logger.log_for_error(env, "Exception raised running remove old changes job {}".format(e))
        raise e


def generate_delete_query(threshold_date):
    query = """
        delete from pathwaysdos.changes c where c.createdTimestamp < (%s)
        returning
        *
    """
    data = (threshold_date,)
    return query, data


def get_log_data(db_connection, service_id):
    # service_data = get_service_data(db_connection, service_id)
    # parent_data = get_parent_uid(db_connection, service_id)
    # region_data = get_region_name(db_connection, service_id)
    log_info = {}
    log_info["operation"] = "delete"
    # log_info["capacity_status"] = "GREEN"
    # log_info["modified_by"] = modified_by
    # log_info["org_id"] = service_data[0]["uid"]
    # log_info["org_name"] = service_data[0]["name"]
    # log_info["org_type_id"] = service_data[0]["typeid"]
    # log_info["parent_org_id"] = parent_data[0]["parentuid"]
    # log_info["region"] = region_data[0]["name"]
    return log_info


def get_log_entry(log_info):
    log_text = ""
    for key, value in log_info.items():
        kv_pair = key + ":" + str(value)
        log_text = log_text + "|" + kv_pair
    log_text = log_text + "|"
    return log_text


def log_deleted_services(env, db_connection, deleted_services):
    for service in deleted_services:
        try:
            service_id = service["serviceid"]
            log_info = get_log_data(db_connection, service_id)
            log_text = get_log_entry(log_info)
            logger.log_for_audit(env, log_text)
        except KeyError as e:
            logger.log_for_error(env, "Data returned from db does not include serviceid column ")
            raise e
    format_data = "%b %d %Y %H:%M:%S"
    end_at = datetime.utcnow()
    logger.log_for_audit(
        env,
        "operation:RemoveOldChanges|records deleted:{0}|updated at:{1}".format(
            str(len(deleted_services)), end_at.strftime(format_data)
        ),
    )


def getThresholdDate(threshold_in_days):
    threshold_in_seconds = 60 * 60 * 24 * threshold_in_days
    current_timestamp = datetime.now()
    threshold_date = current_timestamp - threshold_in_seconds
    threshold_date = threshold_date.strftime("%d-%b-%Y %H:%M:%S")
    print(threshold_date)
    return threshold_date


# def

# def get_service_data(db_connection, service_id):
#     query, data = generate_service_query(service_id)
#     result_set = database.execute_cron_query(db_connection, query, data)
#     return result_set


# def generate_service_query(service_id):
#     query = """select uid, name, typeid, parentid
#             from services
#             where id = %s
#     """
#     data = (service_id,)
#     return query, data


# def get_parent_uid(db_connection, service_id):
#     query, data = generate_parent_uid_query(service_id)
#     result_set = database.execute_cron_query(db_connection, query, data)
#     return result_set


# def generate_parent_uid_query(service_id):
#     query = """select
#             ser.id as parentid,
#             ser.uid as parentuid
#             from services as ser
#             where ser.id = (select parentid from services where id = %s);
#     """
#     data = (service_id,)
#     return query, data
