from unittest.mock import Mock, patch
import psycopg2
import pytest
# from application.utilities.common import check_csv_format, valid_action, cleanup, retrieve_file_from_bucket, connect_to_database
from .. import common

file_path = "application.utilities.common"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
start = ""


csv_id = 2001
csv_desc = "Unit Test"


def test_check_csv():
    csv_line = "col1,col2,col3"
    assert common.check_csv_format(csv_line,3)

def test_check_csv():
    csv_line = "col1,col2,col3"
    assert not common.check_csv_format(csv_line,4)

def test_valid_create_action():
    """Test valid condition for create action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert common.valid_action(False,csv_dict)

def test_invalid_create_action():
    """Test invalid condition for create action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert not common.valid_action(True,csv_dict)

def test_valid_update_action():
    """Test valid condition for update action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "UPDATE"
    assert common.valid_action(True,csv_dict)

def test_invalid_update_action():
    """Test invalid condition for update action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "UPDATE"
    assert not common.valid_action(False,csv_dict)

def test_valid_delete_action():
    """Test valid condition for delete action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert common.valid_action(True,csv_dict)

def test_invalid_delete_action():
    """Test invalid condition for delete action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert not common.valid_action(False,csv_dict)

def test_invalid_action():
    """Test validation of unrecognized action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "NOSUCH"
    assert not common.valid_action(True,csv_dict)

def test_invalid_action_lower_case():
    """Test validation of lower case action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "delete"
    assert not common.valid_action(True,csv_dict)

@patch("psycopg2.connect")
@patch(f"{file_path}.S3")
@patch(f"{file_path}.send_success_slack_message")
def test_cleanup_success(mock_send_success_slack_message, mock_s3_object, mock_db_connect):
    mock_db_connect.close.return_value = "Closed connection"
    mock_s3_object().copy_object = Mock(return_value="Object copied")
    mock_s3_object().delete_object = Mock(return_value="Object deleted")
    mock_bucket = ""
    mock_filename = "local/DPTS-001_symptomdiscriminators.csv"
    result = common.cleanup(mock_db_connect, mock_bucket, mock_filename, mock_event, start)
    assert result == "Cleanup Successful"
    mock_db_connect.close.assert_called_once()
    mock_s3_object().copy_object.assert_called_once_with(mock_bucket, mock_filename, mock_event, start)
    mock_s3_object().delete_object.assert_called_once_with(mock_bucket, mock_filename, mock_event, start)
    mock_send_success_slack_message.assert_called_once_with(mock_event, start)


@patch(f"{file_path}.send_failure_slack_message")
@patch(f"{file_path}.DB")
def test_connect_to_database_returns_error(mock_db_object, mock_send_failure_slack_message):
    mock_db_object().db_set_connection_details = Mock(return_value=False)
    with pytest.raises(ValueError) as assertion:
        result = common.connect_to_database(mock_env, mock_event, start)
    assert str(assertion.value) == "DB Parameter(s) not found in secrets store"
    mock_db_object().db_set_connection_details.assert_called_once()
    mock_send_failure_slack_message.assert_called_once()


@patch(f"{file_path}.S3")
def test_retrieve_file_from_bucket(mock_s3_object):
    mock_s3_object().get_object = Mock(return_value="Object returned")
    mock_bucket = ""
    mock_filename = ""
    result = common.retrieve_file_from_bucket(mock_bucket, mock_filename, mock_event, start)
    assert result == "Object returned"
    mock_s3_object().get_object.assert_called_once()


@patch(f"{file_path}.DB")
def test_connect_to_database_success(mock_db_object):
    mock_db_object().db_set_connection_details = Mock(return_value=True)
    mock_db_object().db_connect = Mock(return_value="Connection Established")
    result = common.connect_to_database(mock_env, mock_event, start)
    assert result == "Connection Established"
    mock_db_object().db_set_connection_details.assert_called_once()
    mock_db_object().db_connect.assert_called_once()
