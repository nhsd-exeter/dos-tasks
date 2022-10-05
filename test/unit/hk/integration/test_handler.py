from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from application.hk.integration import handler

file_path = "application.hk.integration.handler"
env = 'integration'
valid_tasks = ("data","symptomgroups")

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

def test_invalid_task_list():
    temp_valid_tasks = ("symptomgroups","data")
    assert len(handler.valid_tasks) == len(temp_valid_tasks)
    for i in range(len(handler.valid_tasks)):
        assert handler.valid_tasks[i] != temp_valid_tasks[i]

@patch("psycopg2.connect")
@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.set_up_test_data", return_value = None)
def test_insert_test_data(mock_set_up_data, mock_audit_logger, mock_db_connect):
    handler.insert_test_data(env,mock_db_connect)
    assert mock_audit_logger.call_count == 1
    assert mock_set_up_data.call_count == 1

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
    assert mock_audit_logger.call_count == 1

# @patch(f"{file_path}.symptomgroup.get_symptom_groups_data", return_value = ({'id':2002,'name':'Integration Test Update','zcodeexists':None},))
# @patch(f"{file_path}.logger.log_for_audit")
# @patch("psycopg2.connect")
# def test_run_data_checks_for_hk_deleted_true(mock_db_connect, mock_audit_logger, mock_get_data):
#     task = 'symptomgroups'
#     handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
#     assert mock_audit_logger.call_count == 2
#     assert mock_get_data.call_count == 1

# @patch(f"{file_path}.symptomgroup.get_symptom_groups_data", return_value = ({'id':2002,'name':'Integration Test Updat','zcodeexists':None},))
# @patch(f"{file_path}.logger.log_for_audit")
# @patch("psycopg2.connect")
# def test_run_data_checks_for_hk_deleted_false(mock_db_connect, mock_audit_logger, mock_get_data):
#     task = 'symptomgroups'
#     handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
#     assert mock_audit_logger.call_count == 2
#     assert mock_get_data.call_count == 1

# @patch(f"{file_path}.symptomgroup.check_symptom_group_record", return_value = True)
@patch(f"{file_path}.symptomgroup.get_symptom_groups_data", return_value = ({'id':2000,'name':'Integration Test Update','zcodeexists':'None'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_hk_updated(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'symptomgroups'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 1
    assert mock_get_data.call_count == 1
    # assert mock_check_data.call_count == 1

# @patch(f"{file_path}.symptomgroup.check_symptom_group_record", return_value = False)
@patch(f"{file_path}.symptomgroup.get_symptom_groups_data", return_value = ({'id':2001,'name':'Int SG','zcodeexists':'None'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_hk_created(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'symptomgroups'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 1
    assert mock_get_data.call_count == 1
    # assert mock_check_data.call_count == 1

# @patch(f"{file_path}.symptomgroup.check_symptom_group_record", return_value = False)
@patch(f"{file_path}.symptomgroup.get_symptom_groups_data", return_value = ({'id':2001,'name':'Int SG','zcodeexists':'None'},))
@patch(f"{file_path}.logger.log_for_audit")
@patch("psycopg2.connect")
def test_run_data_checks_for_invalid_hk_task(mock_db_connect, mock_audit_logger, mock_get_data):
    task = 'referralroles'
    handler.run_data_checks_for_hk_task(env, task, mock_db_connect)
    assert mock_audit_logger.call_count == 2
    assert mock_get_data.call_count == 0
    # assert mock_check_data.call_count == 1

@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.insert_test_data", return_value="")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
def test_request_valid_data_task(mock_db_connect, mock_db_close, mock_insert, mock_audit):
    payload = generate_event_payload('data')
    result = handler.request(event=payload, context=None)
    assert mock_db_connect.call_count == 1
    assert mock_db_close.call_count == 1
    assert mock_insert.call_count == 1
    assert mock_audit.call_count == 1


@patch(f"{file_path}.symptomgroup.check_symptom_groups_data", return_value=True)
@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.run_data_checks_for_hk_task", return_value=True)
@patch(f"{file_path}.insert_test_data", return_value="")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
def test_request_valid_hk_task(mock_db_connect, mock_db_close, mock_insert, mock_data_checks, mock_audit, mock_check):
    payload = generate_event_payload('symptomgroups')
    result = handler.request(event=payload, context=None)
    assert mock_db_connect.call_count == 1
    assert mock_db_close.call_count == 1
    assert mock_insert.call_count == 0
    assert mock_data_checks.call_count == 1
    assert mock_audit.call_count == 2
    # assert mock_check.call_count == 1

@patch(f"{file_path}.insert_test_data", return_value="")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
def test_request_invalid_task(mock_db_connect, mock_db_close, mock_insert):
    payload = generate_event_payload('nosuch')
    result = handler.request(event=payload, context=None)
    assert mock_db_connect.call_count == 0
    assert mock_db_close.call_count == 0
    assert mock_insert.call_count == 0


def generate_event_payload(task):
    """Utility function to generate dummy event data"""
    return {"task": task,}
