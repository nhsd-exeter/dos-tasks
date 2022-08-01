# import psycopg2
# import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime
import os

# Handler called after all hk lambdas in list of lambdas have been triggered
# Iterates thru same list of hk lambdas run and for each one executes a bespoke query
# Checks result of query against expected results - eg should be a new record with id of x
# If tests pass for hk job A proceed to check job B otherwise fail fast
# Need to pass db_name as per cron
# Need function per hk job


def request(event, context):
    success = False
    start = datetime.utcnow()
    env = os.getenv("DB_NAME")
    db_connection = None
    logger.log_for_audit(env, "action:task started")
    try:
        db_connection = database.connect_to_database(env, event)
        success = check_results(db_connection)
        logger.log_for_audit(event["env"], "action:task complete")
    except Exception as e:
        logger.log_for_error(env, "Problem {}".format(e))
        message.send_failure_slack_message(event, start)
    finally:
        database.close_connection(event, db_connection)
    return success


def create_symptomgroup_query(row_values):
    query = """
        select id, name, zcodeexists from pathwaysdos.symptomgroups where id in (%s);
    """
    data = (
        row_values["id"],
    )
    return query, data

def get_symptomgroups_data(db_connection):
    result_set = {}
    symptom_group_ids = '(2000,2001,2002)'
    try:
        query, data = create_symptomgroup_query(symptom_group_ids)
        result_set = database.execute_db_query(db_connection, query, data)
    except Exception as e:
        logger.log_for_error(
            "Error checking results for {0} => {1}".format("symptomgroups", str(e)),
        )
    return result_set

def check_symptomgroups(db_connection):
    symptomgroup_data = get_symptomgroups_data(db_connection)
    # TODO
    # check record inserted, check record updated, check record deleted

def check_results(db_connection):
    check_symptomgroups(db_connection)
