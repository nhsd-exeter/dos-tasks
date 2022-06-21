import psycopg2
import pytest
from unittest.mock import Mock, patch
from .. import database

file_path = "application.utilities.database"
table_name = "referralroles"
csv_id = 2001
csv_desc = "Unit Test"
csv_action = "DELETE"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
start = ""


@patch("psycopg2.connect")
def test_db_connect(mock_connect):
    mock_event = "user=mock_user password=xxx dbname=mock_name host=mock_host"
    start = ""
    db = database.DB()
    db.db_host = "mock_host"
    db.db_name = "mock_name"
    db.db_user = "mock_user"
    db.db_password = "mock_password"
    result = db.db_connect(mock_event, start)
    assert result != None
    mock_connect.assert_called_with(host="mock_host", dbname="mock_name", user="mock_user", password="mock_password")


@patch(f"{file_path}.message.send_failure_slack_message")
def test_db_connect_error(mock_send_failure_slack_message):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    db = database.DB()
    db.db_host = "mock_host"
    db.db_name = "mock_name"
    db.db_user = "mock_user"
    db.db_password = "mock_password"
    with pytest.raises(psycopg2.InterfaceError) as assertion:
        _ = db.db_connect(mock_event, start)
    mock_send_failure_slack_message.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_success(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == True
    assert db.db_host == "mock_host"
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == "mock_user"
    assert db.db_password == "mock_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOSTER\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_host_key_not_set(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == False
    assert db.db_host == ""
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == "mock_user"
    assert db.db_password == "mock_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USERNAME\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_user_key_not_set(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == False
    assert db.db_host == "mock_host"
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == ""
    assert db.db_password == "mock_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_password_key_not_set(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == False
    assert db.db_host == "mock_host"
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == "mock_user"
    assert db.db_password == ""
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="null")
def test_db_set_connection_details_secrets_not_set(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == False
    assert db.db_host == ""
    assert db.db_name == ""
    assert db.db_user == ""
    assert db.db_password == ""
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\", \"DB_PERFORMANCE_PASSWORD\": \"mock_performance_password\", \"DB_PERFORMANCE_HOST\": \"mock_performance_host\"}")
def test_db_set_connection_details_name_set_correctly_with_performance_env(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "performance"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == True
    assert db.db_host == "mock_performance_host"
    assert db.db_name == "pathwaysdos"
    assert db.db_user == "mock_user"
    assert db.db_password == "mock_performance_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\", \"DB_REGRESSION_HOST\": \"mock_regression_host\"}")
def test_db_set_connection_details_name_set_correctly_with_regression_env(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "regression"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == True
    assert db.db_host == "mock_regression_host"
    assert db.db_name == "pathwaysdos_regression"
    assert db.db_user == "mock_user"
    assert db.db_password == "mock_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOSTER\": \"mock_host\", \"DB_USERNAME\": \"mock_user\", \"DB_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_all_keys_incorrect(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == False
    assert db.db_host == ""
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == ""
    assert db.db_password == ""
    mock_get_secrets_value.assert_called_once()

@patch("psycopg2.connect")
def test_record_exists_true(mock_db_connect):
    """Test correct data passed to check record exists - returning true"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["name"] = csv_desc
    csv_dict["action"] = csv_action
    csv_dict["zcode"] = None
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
    assert database.does_record_exist(mock_db_connect,csv_dict,table_name)

@patch("psycopg2.connect")
def test_does_record_exist_false(mock_db_connect):
    """Test correct data passed to check record exists - returning false"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["name"] = csv_desc
    csv_dict["action"] = "DELETE"
    csv_dict["zcode"] = None
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
    assert not database.does_record_exist(mock_db_connect,csv_dict,table_name)

@patch("psycopg2.connect")
def test_does_record_exist_exception(mock_db_connect):
    """Test throwing of exception """
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["name"] = csv_desc
    csv_dict["action"] = csv_action
    csv_dict["zcode"] = None
    mock_db_connect = ""
    with pytest.raises(Exception):
        database.does_record_exist(mock_db_connect,csv_dict,table_name)


# TODO move inside class later
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.DB")
def test_connect_to_database_returns_error(mock_db_object, mock_send_failure_slack_message):
    mock_db_object().db_set_connection_details = Mock(return_value=False)
    with pytest.raises(ValueError) as assertion:
        database.connect_to_database(mock_env, mock_event, start)
    assert str(assertion.value) == "DB Parameter(s) not found in secrets store"
    mock_db_object().db_set_connection_details.assert_called_once()
    mock_send_failure_slack_message.assert_called_once()


# TODO move inside class later
@patch(f"{file_path}.DB")
def test_connect_to_database_success(mock_db_object):
    mock_db_object().db_set_connection_details = Mock(return_value=True)
    mock_db_object().db_connect = Mock(return_value="Connection Established")
    result = database.connect_to_database(mock_env, mock_event, start)
    assert result == "Connection Established"
    mock_db_object().db_set_connection_details.assert_called_once()
    mock_db_object().db_connect.assert_called_once()
