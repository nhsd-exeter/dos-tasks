# import psycopg2
# import psycopg2.extras
# from tkinter import E
from utilities import logger, message, common, database
from datetime import datetime
import os
import boto3
from botocore.exceptions import ClientError
# from run_update_check import run_check
import psycopg2
import json
# from .. import symptomgroup
from . import model
#  subprocess import only needed if i can get psql sub process example to work from here
# https://gist.github.com/valferon/4d6ebfa8a7f3d4e84085183609d10f14
# import subprocess

# Handler to
# create database with name passed in as a parameter eg DB_NAME=integration
# run data set up sql script - one for all hk jobs
# Checks result of individual hk job against expected results - eg should be a new record with id of x
# Currently call individually per hk job to check results
# Need to pass db_name as per cron
# Need function per hk job
# Needs to know the database

# USERNAME = os.environ.get("USERNAME")
# PORT = os.environ.get("PORT")
# # REGION = os.environ.get("REGION")
# INTEGRATION_TEST_ENDPOINT = os.environ.get("INTEGRATION_TEST_ENDPOINT")
# SECRET_NAME = os.environ.get("SECRET_NAME")
# SECRET_KEY = os.environ.get("SECRET_KEY")

# List of data set up scripts to be run if task is data
data_sql_scripts = ("test-data.sql")
# List of tasks handled by this code DO NOT change the order
valid_tasks = ("data","symptomgroups")
def request(event, context):
    success = False
    start = datetime.utcnow()
    env = os.getenv("DB_NAME")
    # sql_file = event['sql-file']
    # where task could be data or name of hk job eg symptomgroup
    task = event['task']
    # database_name = event['database_name']
    db_connection = None
    logger.log_for_audit(env, "action:task started")
    if is_valid_task(env, task):
        try:
            db_connection = database.connect_to_database(env, event)
            if task.lower == valid_tasks[0]:
                insert_test_data(env, db_connection)
            else:
                outcome = run_data_checks_for_hk_task(env, task, db_connection)
                logger.log_for_audit(env, "action:integration test complete for {}".format(task))
        except Exception as e:
            logger.log_for_error(env, "Problem {}".format(e))
            message.send_failure_slack_message(event, start)
        finally:
            database.close_connection(event, db_connection)
    return success

# TODO can be removed when other unit tests are ready
def set_up_data_conditions():
    return True
# TODO add sql scripts to test results of each hk job

def run_data_checks_for_hk_task(env, task, db_connection):
    """Ensures tests appropriate to task ; returns True if tests pass"""
    checks_pass = False
    try:
        logger.log_for_audit(env, "Preparing to test results of {} task".format(task))
        # TODO elif or case :
        if task.lower == valid_tasks[1]:
            checks_pass = symptomgroup.check_symptom_groups_data(env, db_connection)
        else:
            logger.log_for_audit(env, "No function to handle task {}".format(task))
    except Exception as e:
        logger.log_for_audit(env, "SQL script {} failed due to {}".format(sql_file, e))
        return False
    return checks_pass


def insert_test_data(env, db_connection):
    """iterate over data set up scripts"""
    try:
        for script in data_sql_scripts:
            logger.log_for_audit(env, "Inserting test data from file {}".format(script))
            set_up_test_data(env, db_connection, script)
    except Exception as e:
        logger.log_for_error(env, "SQL script {} failed due to {}".format(sql_file, e))
        raise e

def set_up_test_data(env, db_connection, sql_file):
    """Runs individual data set up script"""
    logger.log_for_audit(env, "Running SQL script {}".format(sql_file))
    db_connection.execute(open(sql_file, "r").read())



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
