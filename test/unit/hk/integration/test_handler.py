from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

# from ..integration import handler
from .. import handler

file_path = "application.hk.integration.handler"
env = 'integration'
valid_tasks = ("data","symptomgroups","referralroles", "servicetypes", "symptomdiscriminators")

@patch(f"{file_path}.logger.log_for_audit")
def test_is_valid_task_invalid_lc(mock_logger):
    invalid_task = 'invalid'
    assert handler.is_valid_task(env,invalid_task) == False
    assert mock_logger.call_count == 1

def test_is_valid_task_invalid_uc():
    invalid_task = 'INVALID'
    assert handler.is_valid_task(env,invalid_task) == False

def test_is_valid_task_invalid_cc():
    invalid_task = 'Invalid'
    assert handler.is_valid_task(env,invalid_task) == False

def test_data_is_valid_task_all_valid_tasks():
    for task in valid_tasks:
        assert handler.is_valid_task(env,task) == True

def test_valid_task_list():
    assert len(handler.valid_tasks) == len(valid_tasks)
    for i in range(len(handler.valid_tasks)):
        assert handler.valid_tasks[i]==valid_tasks[i]

# This may be hard to maintain as nothing in this list can be in its actual position
# add any new task as penultimate in list
def test_invalid_task_list():
    temp_valid_tasks = ("symptomgroups","referralroles","servicetypes","symptomdiscriminators","data")
    assert len(handler.valid_tasks) == len(temp_valid_tasks)
    for i in range(len(handler.valid_tasks)):
        assert handler.valid_tasks[i] != temp_valid_tasks[i]

@patch("psycopg2.connect")
@patch(f"{file_path}.logger.log_for_audit")
def test_insert_test_data_logging( mock_audit_logger, mock_db_connect):
    handler.insert_test_data(env,mock_db_connect)
    assert mock_audit_logger.call_count == 2

@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_hk_task_old(mock_db_connect, mock_audit_logger):
    task = 'symptomgroups'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 2

@patch(f"{file_path}.symptomgroup.get_symptom_groups_data", return_value = ({'id':2000,'name':'Wrong name','zcodeexists':False},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_symptomgroups_created_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'symptomgroups'
    result = handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert result == False
    assert mock_audit_logger.call_count == 3
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.symptomgroup.get_symptom_groups_data", return_value = ({'id':2001,'name':'Integration Test Update','zcodeexists':False},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_symptomgroups_deleted_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'symptomgroups'
    result = handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert result == False
    assert mock_audit_logger.call_count == 2
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.symptomgroup.get_symptom_groups_data", return_value = ({'id':2002,'name':'Int SG','zcodeexists':'None'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_symptomgroups(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'symptomgroups'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 3
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.referralrole.get_referral_roles_data", return_value = ({'id':2000,'name':'Integration Test Create'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_referralroles_created_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'referralroles'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 2
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.referralrole.get_referral_roles_data", return_value = ({'id':2001,'name':'Integration Test Update'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_referralroles_updated_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'referralroles'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 2
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.referralrole.get_referral_roles_data", return_value = ({'id':2002,'name':'Integration Test Update'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_referralroles_deleted_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'referralroles'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 3
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.referralrole.get_referral_roles_data", return_value = ({'id':2001,'name':'Int RR'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_invalid_hk_task(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'nosuch'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 3
    assert mock_get_data.call_count == 0

@patch(f"{file_path}.servicetype.get_service_types_data", return_value = ({'id':2000,'name':'Wrong name','nationalranking':8,'searchcapacitystatus':True, 'capacitymodel':'n/a', 'capacityreset':'interval'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_servicetypes_created_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'servicetypes'
    result = handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert result == False
    assert mock_audit_logger.call_count == 3
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.servicetype.get_service_types_data", return_value = ({'id':2001,'name':'Wrong name','nationalranking':8,'searchcapacitystatus':True, 'capacitymodel':'n/a', 'capacityreset':'interval'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_servicetypes_deleted_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'servicetypes'
    result = handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert result == False
    assert mock_audit_logger.call_count == 3
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.servicetype.get_service_types_data", return_value = ({'id':2002,'name':'Wrong name','nationalranking':8,'searchcapacitystatus':True, 'capacitymodel':'n/a', 'capacityreset':'interval'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_servicetypes(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'servicetypes'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 3
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.symptomdiscriminator.get_symptom_discriminator_data", return_value = ({'id':2000,'description':'Wrong description'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_symptomdiscriminators_created_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'symptomdiscriminators'
    result = handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert result == False
    assert mock_audit_logger.call_count == 2
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.symptomdiscriminator.get_symptom_discriminator_data", return_value = ({'id':2001,'description':'Wrong description'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_symptomdiscriminators_deleted_record(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'symptomdiscriminators'
    result = handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert result == False
    assert mock_audit_logger.call_count == 2
    assert mock_get_data.call_count == 1

@patch(f"{file_path}.symptomdiscriminator.get_symptom_discriminator_data", return_value = ({'id':2002,'description':'Wrong description'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_symptomdiscriminators(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'symptomdiscriminators'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 2
    assert mock_get_data.call_count == 1
def generate_event_payload(task):
    """Utility function to generate dummy event data"""
    return {"task": task,}
