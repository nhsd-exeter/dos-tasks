from utilities import logger, database, cron_common

from datetime import datetime, timedelta
import os

task_description = "Remove old changes"
# threshold_in_days = 90


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
        delete_query = generate_delete_query(threshold_date)
        database.execute_cron_delete_query(env, db_connection, delete_query)
    # log_deleted_changes(env, db_connection, deleted_changes)
    except KeyError as e:
        logger.log_for_error(env, "Delete query failed")
        raise e


# where c.createdTimestamp < (%s)


def generate_delete_query(threshold_date):
    query = """delete from pathwaysdos.changes c where c.createdTimestamp < (%s)
        returning
        *
    """
    data = (threshold_date,)
    print(query)
    print(data)
    return query, data
    # return query


# def get_log_data(db_connection):
#     # service_data = get_service_data(db_connection, service_id)
#     # parent_data = get_parent_uid(db_connection, service_id)
#     # region_data = get_region_name(db_connection, service_id)
#     log_info = {}
#     log_info["operation"] = "delete"
#     # log_info["capacity_status"] = "GREEN"
#     # log_info["modified_by"] = modified_by
#     # log_info["org_id"] = service_data[0]["uid"]
#     # log_info["org_name"] = service_data[0]["name"]
#     # log_info["org_type_id"] = service_data[0]["typeid"]
#     # log_info["parent_org_id"] = parent_data[0]["parentuid"]
#     # log_info["region"] = region_data[0]["name"]
#     return log_info


# def get_log_entry(log_info):
#     log_text = ""
#     for key, value in log_info.items():
#         kv_pair = key + ":" + str(value)
#         log_text = log_text + "|" + kv_pair
#     log_text = log_text + "|"
#     return log_text


# def log_deleted_changes(env, db_connection):
#     try:
#         log_info = get_log_data(db_connection)
#         log_text = get_log_entry(log_info)
#         logger.log_for_audit(env, log_text)
#     except KeyError as e:
#         logger.log_for_error(env, "Data returned from db does not include something column ")
#         raise e
#     format_data = "%b %d %Y %H:%M:%S"
#     end_at = datetime.utcnow()
#     logger.log_for_audit(
#         env,
#         "operation:RemoveOldChanges|records |updated at:{0}".format( end_at.strftime(format_data)
#         ),
#     )


def getThresholdDate(threshold_in_days):
    current_timestamp = datetime.now()
    threshold_date = current_timestamp - timedelta(days=threshold_in_days)
    threshold_date = threshold_date.strftime("%Y-%m-%d %H:%M:%S")
    print(threshold_date)
    return threshold_date
