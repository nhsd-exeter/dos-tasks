import os
import psycopg2
import pytest
import boto3
from unittest.mock import patch
from .. import database

file_path = "application.utilities.database"

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


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_name_set_correctly_with_performance_env(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "performance"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env, mock_event, start)
    assert connection_details_set == True
    assert db.db_host == "mock_host"
    assert db.db_name == "pathwaysdos"
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
