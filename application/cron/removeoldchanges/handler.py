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
        print("remove old changes")
        print(threshold_date)
        # delete_query, data = generate_delete_query(threshold_date)
        delete_query = generate_delete_query(threshold_date)
        print(delete_query)
        # database.execute_cron_delete_query(env, db_connection, delete_query, data)
        database.execute_cron_delete_query(env, db_connection, delete_query)
    # log_deleted_changes(env, db_connection, deleted_changes)
    except KeyError as e:
        logger.log_for_error(env, "Delete query failed")
        raise e


def generate_delete_query(threshold_date):
    query = """delete from pathwaysdos.changes c where c.createdTimestamp < now()+ interval '-90 days'
        returning
        *
    """
    # data = (threshold_date,)
    return query
    # , data
    # return query

def generate_delete_count_query():
    query = """select count(*) as removed_count from pathwaysdos.changes c where c.createdTimestamp < now()+ interval '-90 days'
        returning
        *
    """
    return query

def get_delete_count(db_connection):
    query = generate_delete_count_query()
    result_set = database.execute_cron_query(db_connection, query)
    return result_set

def get_log_data(db_connection):
    delete_count = get_delete_count(db_connection,)
    log_info = {}
    log_info["operation"] = "delete"
    log_info["removed_count"] = delete_count[0]["removed_count"]
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
    print(threshold_date)
    return threshold_date
