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
    logger.log_for_audit(env, "| operation:start")
    logger.log_for_audit(env, "| Event id: {0}, event time: {1} , environment: {2}".format(event_id, event_time, env))
    db_connection = database.connect_to_database(env)
    remove_old_changes(env, db_connection)
    cron_common.cron_cleanup(env, db_connection)
    logger.log_for_audit(env, "| operation:end")
    return task_description + " execution successful"


def remove_old_changes(env, db_connection):
    try:
        threshold_date = getThresholdDate(threshold_in_days)
        delete_count_result = get_delete_count(env, db_connection, threshold_date)
        delete_query, data = generate_delete_query(threshold_date)
        database.execute_cron_query_no_returning_rows(env, db_connection, delete_query, data)
        log_removed_changes(env, db_connection, delete_count_result)
    except KeyError as e:
        logger.log_for_error(env, "| Delete query failed")
        raise e


def log_removed_changes(env, db_connection, delete_count_result):
    deleted_count = delete_count_result[0]["removed_count"]
    format_data = "%b %d %Y %H:%M:%S"
    end_at = datetime.utcnow()
    logger.log_for_audit(
        env,
        "| operation:RemoveOldChanges | records deleted:{0} | deleted at:{1} ".format(
            deleted_count, end_at.strftime(format_data)
        ),
    )


def generate_delete_query(threshold_date):
    query = """delete from pathwaysdos.changes c where c.createdTimestamp < %s
    """
    data = (threshold_date,)
    return query, data


def generate_delete_count_query(threshold_date):
    query = """select count(*) removed_count from pathwaysdos.changes c where c.createdTimestamp < %s
    """
    data = (threshold_date,)
    return query, data


def get_delete_count(env, db_connection, threshold_date):
    query, data = generate_delete_count_query(threshold_date)
    result_set = database.execute_cron_query(env, db_connection, query, data)
    return result_set


def getThresholdDate(threshold_in_days):
    current_timestamp = datetime.now()
    threshold_date = current_timestamp - timedelta(days=threshold_in_days)
    threshold_date = threshold_date.strftime("%Y-%m-%d %H:%M:%S")
    return threshold_date
