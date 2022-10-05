from application.hk.integration.utilities import logger, message, common, database
from datetime import datetime
import os
import boto3
from botocore.exceptions import ClientError
import psycopg2
import json
# from . import model
# from . import model.symptomgroup
from application.hk.integration.model import symptomgroup

data_sql_scripts = ("/data-files/test-data.sql",)
# List of tasks handled by this code DO NOT change the order
valid_tasks = ("data","symptomgroups")
def request(event, context):
    success = False
    start = datetime.utcnow()
    env = os.getenv("DB_NAME")
    # where task could be data or name of hk job eg symptomgroup
    task = event['task']
    db_connection = None
    logger.log_for_audit(env, "action:task started")
    if is_valid_task(env, task):
        try:
            db_connection = database.connect_to_database(env, event)
            if task.lower() == valid_tasks[0]:
                insert_test_data(env, db_connection)
            else:
                success = run_data_checks_for_hk_task(env, task, db_connection)
                logger.log_for_audit(env, "action:integration test complete for {}".format(task))
        except Exception as e:
            logger.log_for_error(env, "Problem {}".format(e))
            # message.send_failure_slack_message(event, start)
        finally:
            database.close_connection(event, db_connection)
    return success

def run_data_checks_for_hk_task(env, task, db_connection):
    """Ensures tests appropriate to task ; returns True if tests pass"""
    checks_pass = None
    logger.log_for_audit(env, "Preparing to test results of {} task".format(task))
    # TODO elif or case :
    if task.lower() == valid_tasks[1].lower():
        checks_pass = symptomgroup.check_symptom_groups_data(env, db_connection)
    # if no code to handle task default to fail
    if (checks_pass is None):
        logger.log_for_audit(env, "No function to handle task {}".format(task))
        checks_pass = False
    return checks_pass


def insert_test_data(env, db_connection):
    """iterate over data set up scripts"""
    for script in data_sql_scripts:
        logger.log_for_audit(env, "Inserting test data from file {}".format(script))
        set_up_test_data(env, db_connection, script)

def set_up_test_data(env, db_connection, sql_file):
    """Runs individual data set up script"""
    logger.log_for_audit(env, "Running SQL script {}".format(sql_file))
    db_connection.execute_script(env, db_connection, sql_file)
    # open(sql_file, "r").read())



def is_valid_task(env, task):
    """validates the task passed in the event"""
    valid_task = False
    for x in valid_tasks:
        if (x.lower() ==  task.lower()):
            valid_task = True
            break
    if valid_task == False:
        logger.log_for_audit(env, "action:unrecognised task {} ".format(task))
    return valid_task
