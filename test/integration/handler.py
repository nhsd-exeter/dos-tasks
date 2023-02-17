from utilities import logger, database
import os
import json

from models import symptomgroup, referralrole, servicetype, symptomdiscriminator, symptomgroupsymptomdiscriminator, symptomdiscriminatorsynonyms, stt

data_sql_scripts = ("./data-files/test-data.sql",)
# List of tasks handled by this code DO NOT change the order add any new task to end
valid_tasks = ("data", "symptomgroups", "referralroles", "servicetypes", "symptomdiscriminators", "symptomgroupdiscriminators", "symptomdiscriminatorsynonyms", "stt")


def request(event, context):
    success = False
    env = os.getenv("TASK")
    # where task could be data or name of hk job eg symptomgroup
    task = event["task"]
    db_connection = None
    logger.log_for_audit(env, "action=task started")
    if is_valid_task(env, task):
        try:
            db_connection = database.connect_to_database(env)
            if task.lower() == valid_tasks[0]:
                success = insert_test_data(env, db_connection)
            else:
                success = run_data_checks_for_hk_task(env, task, db_connection)
                logger.log_for_audit(env, "action=integration test complete for {}".format(task))
        except Exception as e:
            logger.log_for_error(env, "Problem {}".format(e))
        finally:
            database.close_connection(event, db_connection)

    status_code = 200 if success else 500
    logger.log_for_audit(env, "status code={}".format(status_code))

    return {"success":str(success)}


def run_data_checks_for_hk_task(env, task, db_connection):
    """Ensures tests appropriate to task ; returns True if tests pass"""
    checks_pass = None
    logger.log_for_audit(env, "Preparing to test results of {} task".format(task))
    # TODO elif or case :
    if task.lower() == valid_tasks[1].lower():
        checks_pass = symptomgroup.check_symptom_groups_data(env, db_connection)
    if task.lower() == valid_tasks[2].lower():
        checks_pass = referralrole.check_referral_roles_data(env, db_connection)
    if task.lower() == valid_tasks[3].lower():
        checks_pass = servicetype.check_service_types_data(env, db_connection)
    if task.lower() == valid_tasks[4].lower():
        checks_pass = symptomdiscriminator.check_symptom_discriminator_data(env, db_connection)
    if task.lower() == valid_tasks[5].lower():
        checks_pass = symptomgroupsymptomdiscriminator.check_symptom_group_symptom_discriminators_data(env, db_connection)
    if task.lower() == valid_tasks[6].lower():
        checks_pass = symptomdiscriminatorsynonyms.check_symptom_discriminator_synonyms_data(env, db_connection)
    if task.lower() == valid_tasks[7].lower():
        checks_pass = stt.check_stt_scenario_data(env, db_connection)
    # if no code to handle task default to fail
    if checks_pass is None:
        logger.log_for_audit(env, "No function to handle task {}".format(task))
        checks_pass = False
    logger.log_for_audit(env, "Checks for {} passed {}".format(task, checks_pass))
    return checks_pass


def insert_test_data(env, db_connection):
    """iterate over data set up scripts"""
    script_run = False
    for script in data_sql_scripts:
        script_run = True
        logger.log_for_audit(env, "Inserting test data from file {}".format(script))
        set_up_test_data(env, db_connection, script)
    return script_run


def set_up_test_data(env, db_connection, sql_file):
    """Runs individual data set up script"""
    logger.log_for_audit(env, "Running SQL script {}".format(sql_file))
    database.execute_script(env, db_connection, sql_file)
    # open(sql_file, "r").read())


def is_valid_task(env, task):
    """validates the task passed in the event"""
    valid_task = False
    for x in valid_tasks:
        if x.lower() == task.lower():
            valid_task = True
            break
    if valid_task is False:
        logger.log_for_audit(env, "action=unrecognised task {} ".format(task))
    return valid_task
