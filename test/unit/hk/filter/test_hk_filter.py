import pytest
from datetime import datetime
from unittest.mock import patch
from .. import handler

file_path = "application.hk.filter.handler"
mock_event = {'Records': [{'s3': {'bucket': {'name': 'uec-dos-tasks-mock-bucket'}, 'object': {'key': 'unittest/DPTS-001_referralroles.csv'}}}]}
mock_context = ""
start = datetime.utcnow()

@patch(f"{file_path}.send_failure_slack_message")
def test_incorrect_file_extension_returns_error(mock_send_failure_slack_message):
    mock_event = {'Records': [{'s3': {'bucket': {'name': 'uec-dos-tasks-mock-bucket'}, 'object': {'key': 'unittest/DPTS-001_referralroles.py'}}}]}
    with pytest.raises(IOError) as assertion:
        error_message = "Incorrect file extension, found: py, expected: '.csv'"
        handler.process_event(mock_event, start)
    assert str(assertion.value) == error_message
    mock_send_failure_slack_message.assert_called_once()


@patch(f"{file_path}.send_failure_slack_message")
def test_process_event_error_returns_exception(mock_send_failure_slack_message):
    mock_event = {'Records': [{'s3': {'bucket': {'name': 'uec-dos-tasks-mock-bucket'}, 'object': {'key': 'DPTS_001_referralroles.csv'}}}]}
    with pytest.raises(Exception) as assertion:
        handler.process_event(mock_event, start)
    assert str(assertion.value) == "list index out of range"
    mock_send_failure_slack_message.assert_called_once()


def test_archived_file_exits_successfully():
    mock_event = {'Records': [{'s3': {'bucket': {'name': 'uec-dos-tasks-mock-bucket'}, 'object': {'key': 'unittest/archive/DPTS-001_referralroles.csv'}}}]}
    result = handler.process_event(mock_event, start)
    assert result == None


@patch(f"{file_path}.invoke_hk_lambda")
def test_successful_process_event(mock_invoke_hk_lambda):
    result = handler.process_event(mock_event, start)
    assert result == "HK Filter Event processed successfully"
    mock_invoke_hk_lambda.assert_called_once()


@patch(f'{file_path}.process_event')
@patch(f'{file_path}.send_start_message')
def test_request_function(mock_send_start_message, mock_process_event):
    assert handler.request(mock_event, mock_context) == "HK task filtered successfully"
    mock_send_start_message.assert_called_once()
    mock_process_event.assert_called_once()


@patch(f"{file_path}.process_event")
@patch(f"{file_path}.send_start_message")
def test_request_function_for_archive_file(mock_send_start_message, mock_process_event):
    mock_event = {'Records': [{'s3': {'bucket': {'name': 'uec-dos-tasks-mock-bucket'}, 'object': {'key': 'unittest/archive/DPTS-001_referralroles.csv'}}}]}
    assert handler.request(mock_event, mock_context) == "HK task filtered successfully"
    mock_send_start_message.assert_not_called()
    mock_process_event.assert_called_once()


@patch(f"{file_path}.send_success_slack_message")
@patch(f"{file_path}.lambda_client.invoke")
def test_invoke_hk_lambda_success(mock_invoke, mock_send_success_slack_message):
    mock_task = "mock"
    mock_filename = "unittest/DPTS-001_mock.csv"
    mock_env = "unittest"
    mock_bucket = "uec-dos-tasks-mock-bucket"
    mock_start = datetime.utcnow()
    result = handler.invoke_hk_lambda(mock_task, mock_filename, mock_env, mock_bucket, mock_start)
    assert result == "HK mock invoked successfully"
    mock_invoke.assert_called_once()
    mock_send_success_slack_message.assert_called_once()


@patch(f"{file_path}.send_failure_slack_message")
def test_invoke_hk_lambda_error(mock_send_failure_slack_message):
    mock_task = "mock"
    mock_filename = "unittest/DPTS-001_mock.csv"
    mock_env = "unittest"
    mock_bucket = "uec-dos-tasks-mock-bucket"
    mock_start = datetime.utcnow()
    with pytest.raises(Exception):
        _ = handler.invoke_hk_lambda(mock_task, mock_filename, mock_env, mock_bucket, mock_start)
    mock_send_failure_slack_message.assert_called_once()


@patch(f"{file_path}.send_failure_slack_message")
def test_incorrect_file_name_separator_returns_error(mock_send_failure_slack_message):
    mock_event = {'Records': [{'s3': {'bucket': {'name': 'uec-dos-tasks-mock-bucket'}, 'object': {'key': 'unittest/DPTS-001-referralroles.csv'}}}]}
    with pytest.raises(Exception) as assertion:
        error_message = "list index out of range"
        handler.process_event(mock_event, start)
    assert str(assertion.value) == error_message
    mock_send_failure_slack_message.assert_called_once()
