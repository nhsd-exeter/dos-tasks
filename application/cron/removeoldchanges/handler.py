from utilities import logger, database, cron_common

from datetime import datetime, timedelta
import os

task_description = "Remove old changes"
threshold_in_days = 90


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
        delete_count_result = get_delete_count(env, db_connection)
        # rows = delete_count_result
        delete_query = generate_delete_query(threshold_date)
        database.execute_cron_delete_query(env, db_connection, delete_query)
        log_removed_changes(env, db_connection, delete_count_result)
    except KeyError as e:
        logger.log_for_error(env, "Delete query failed")
        raise e


def log_removed_changes(env, db_connection, delete_count_result):
    log_info = get_log_data(env, db_connection, delete_count_result)
    log_text = get_log_entry(log_info)
    logger.log_for_audit(env, log_text)
    deleted_count = delete_count_result[0]["removed_count"]
    format_data = "%b %d %Y %H:%M:%S"
    end_at = datetime.utcnow()
    logger.log_for_audit(
        env,
        "operation:RemoveOldChanges|records deleted:{0}|deleted at:{1}".format(
            deleted_count, end_at.strftime(format_data)
        ),
    )


def generate_delete_query(threshold_date):
    query = """delete from pathwaysdos.changes c where c.createdTimestamp < now()+ interval '-90 days'
        returning
        *
    """
    return query


def generate_delete_count_query():
    query = """select count(*) removed_count from pathwaysdos.changes c where c.createdTimestamp < now()+ interval '-90 days'
    """
    return query


def get_delete_count(env, db_connection):
    query = generate_delete_count_query()
    result_set = database.execute_cron_nodata_query(env, db_connection, query)
    return result_set


def get_log_data(env, db_connectiond, delete_count_result):
    log_info = {}
    log_info["operation"] = "delete"
    log_info["records deleted"] = delete_count_result[0]["removed_count"]
    return log_info


def get_log_entry(log_info):
    log_text = ""
    for key, value in log_info.items():
        kv_pair = key + ":" + str(value)
        log_text = log_text + "|" + kv_pair
    log_text = log_text + "|"
    return log_text


def getThresholdDate(threshold_in_days):
    current_timestamp = datetime.now()
    threshold_date = current_timestamp - timedelta(days=threshold_in_days)
    threshold_date = threshold_date.strftime("%Y-%m-%d %H:%M:%S")
    return threshold_date
