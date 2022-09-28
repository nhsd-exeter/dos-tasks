# import psycopg2
# import psycopg2.extras
from utilities import logger, message, common, database
from datetime import datetime
import os
import boto3
from botocore.exceptions import ClientError
# from run_update_check import run_check
import psycopg2
import json

# See test-data.sql and test/integration/test-files/int_symptomgroups.csv
# Will test
# That a new record exists with id of 2000 and description of "Integration Test Create"
# That an existing record with id of 2001 has updated description of "Integration Test Update"
# That an existing record with id of 2002 has been deleted

deleted_record_id = 2002
updated_record_id = 2001
updated_record_name = "Integration Test Update"
created_record_id = 2000
created_record_name = "Integration Test Create"
expected_zcode_exists = None

def get_symptom_groups_data(env, db_connection):
    """Returns symptomgroups under test"""
    result_set = {}
    symptom_group_ids = '(2000,2001,2002)'
    try:
        query, data = create_symptom_group_query(symptom_group_ids)
        result_set = database.execute_resultset_query(env, db_connection, query, data)
    except Exception as e:
        logger.log_for_error(env,
            "Error checking results for {0} => {1}".format("symptomgroups", str(e)),
        )
    return result_set

def create_symptom_group_query(row_values):
    query = """
        select id, name, zcodeexists from pathwaysdos.symptomgroups where id in (%s) order by id asc;
    """
    data = (
        row_values["id"],
    )
    return query, data

# That a new record exists with id of 2000 and description of "Integration Test Create"
# That an existing record with id of 2001 has updated description of "Integration Test Update"
# That an existing record with id of 2002 has been deleted

def check_symptom_groups_data(env, db_connection):
    """Returns True if all checks pass ; otherwise returns False"""
    delete_pass = True
    create_pass = False
    update_pass = False
    result_set = get_symptom_groups_data(env, db_connection)
    for symptom_group in result_set:
        sg_id = symptom_group["id"]
        if sg_id == deleted_record_id:
            delete_pass = False
            logger.log_for_audit(env,
            "Record with id {0} not deleted".format(sg_id),
        )
        if sg_id == created_record_id:
            create_pass = check_symptom_group_record(symptom_group, created_record_name, expected_zcode_exists)
        if sg_id == updated_record_id:
            update_pass = check_symptom_group_record(symptom_group, updated_record_name, expected_zcode_exists)
    all_pass = delete_pass and update_pass and create_pass
    return all_pass

def check_symptom_group_record(symptom_group, expected_name, expected_zcode_exists):
    """Returns true if data persisted is as expected"""
    if symptom_group["name"] == expected_name and symptom_group['zcodeexists'] == expected_zcode_exists:
        return True
    else:
        return False
