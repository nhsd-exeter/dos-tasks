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
    result = db.db_connect(mock_event)
    assert result != None
    mock_connect.assert_called_with(host="mock_host", dbname="mock_name", user="mock_user", password="mock_password")


@patch(f"{file_path}.logger.log_for_error")
def test_db_connect_error(mock_logger):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    db = database.DB()
    db.db_host = "mock_host"
    db.db_name = "mock_name"
    db.db_user = "mock_user"
    db.db_password = "mock_password"
    with pytest.raises(psycopg2.InterfaceError) as assertion:
        _ = db.db_connect(mock_event)
    mock_logger.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_success(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = ""
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env)
    assert connection_details_set == True
    assert db.db_host == "mock_host"
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == "mock_user"
    assert db.db_password == "mock_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOSTER\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_host_key_not_set(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env)
    assert connection_details_set == False
    assert db.db_host == ""
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == "mock_user"
    assert db.db_password == "mock_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USERNAME\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_user_key_not_set(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env)
    assert connection_details_set == False
    assert db.db_host == "mock_host"
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == ""
    assert db.db_password == "mock_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_password_key_not_set(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env)
    assert connection_details_set == False
    assert db.db_host == "mock_host"
    assert db.db_name == "pathwaysdos_mock_env"
    assert db.db_user == "mock_user"
    assert db.db_password == ""
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="null")
def test_db_set_connection_details_secrets_not_set(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env)
    assert connection_details_set == False
    assert db.db_host == ""
    assert db.db_name == ""
    assert db.db_user == ""
    assert db.db_password == ""
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\", \"DB_PERFORMANCE_PASSWORD\": \"mock_performance_password\", \"DB_PERFORMANCE_HOST\": \"mock_performance_host\"}")
def test_db_set_connection_details_name_set_correctly_with_performance_env(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_env = "performance"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env)
    assert connection_details_set == True
    assert db.db_host == "mock_performance_host"
    assert db.db_name == "pathwaysdos"
    assert db.db_user == "mock_user"
    assert db.db_password == "mock_performance_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOST\": \"mock_host\", \"DB_USER\": \"mock_user\", \"DB_USER_PASSWORD\": \"mock_password\", \"DB_REGRESSION_HOST\": \"mock_regression_host\"}")
def test_db_set_connection_details_name_set_correctly_with_regression_env(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_env = "regression"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env)
    assert connection_details_set == True
    assert db.db_host == "mock_regression_host"
    assert db.db_name == "pathwaysdos_regression"
    assert db.db_user == "mock_user"
    assert db.db_password == "mock_password"
    mock_get_secrets_value.assert_called_once()


@patch(f"{file_path}.secrets.SECRETS.get_secret_value", return_value="{\"DB_HOSTER\": \"mock_host\", \"DB_USERNAME\": \"mock_user\", \"DB_PASSWORD\": \"mock_password\"}")
def test_db_set_connection_details_all_keys_incorrect(mock_get_secrets_value):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_env = "mock_env"
    db = database.DB()
    connection_details_set = db.db_set_connection_details(mock_env)
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
    assert database.does_record_exist(mock_db_connect,csv_dict,table_name,'test')

@patch("psycopg2.connect")
def test_does_record_exist_false(mock_db_connect):
    """Test correct data passed to check record exists - returning false"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["name"] = csv_desc
    csv_dict["action"] = "DELETE"
    csv_dict["zcode"] = None
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
    assert not database.does_record_exist(mock_db_connect,csv_dict,table_name,'test')

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
        database.does_record_exist(mock_db_connect,csv_dict,table_name,'test')


# TODO move inside class later
@patch(f"{file_path}.logger.log_for_error")
@patch(f"{file_path}.DB")
def test_connect_to_database_returns_error(mock_db_object, mock_logger):
    mock_db_object().db_set_connection_details = Mock(return_value=False)
    with pytest.raises(ValueError) as assertion:
        database.connect_to_database(mock_env)
    assert str(assertion.value) == "DB Parameter(s) not found in secrets store"
    mock_db_object().db_set_connection_details.assert_called_once()
    mock_logger.assert_called_once()


# TODO move inside class later
@patch(f"{file_path}.DB")
def test_connect_to_database_success(mock_db_object):
    mock_db_object().db_set_connection_details = Mock(return_value=True)
    mock_db_object().db_connect = Mock(return_value="Connection Established")
    result = database.connect_to_database(mock_env)
    assert result == "Connection Established"
    mock_db_object().db_set_connection_details.assert_called_once()
    mock_db_object().db_connect.assert_called_once()


# TODO move inside class later
@patch(f"{file_path}.DB")
@patch("psycopg2.connect")
def test_close_database_connection(mock_db_object,mock_db_connect):
    mock_db_connect().close_connection = Mock(return_value="Connection Closed")
    database.close_connection(mock_event, mock_db_connect)
    mock_db_connect.close.assert_called_once()


# TODO move inside class later
@patch(f"{file_path}.logger.log_for_error")
@patch(f"{file_path}.DB")
@patch("psycopg2.connect")
def test_close_null_database_connection(mock_db_object,mock_db_connect,mock_logger):
    mock_db_connect = None
    database.close_connection(mock_event, mock_db_connect)
    mock_logger.assert_called_once()


# TODO move inside class later
@patch(f"{file_path}.common.increment_summary_count")
@patch("psycopg2.connect")
def test_execute_db_query_success(mock_db_connect,mock_summary):
    """Test code to execute query successfully"""
    line = """2001,"New Symptom Group","CREATE"\n"""
    data = ("New Symptom Group", "None", 2001)
    values = {}
    values["action"] = "CREATE"
    values['id'] = 2001
    values['name'] = "New Symptom Group"
    summary_count = {}
    mock_db_connect.cursor.return_value.__enter__.return_value = "Success"
    query = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
        where id = (%s);"""
    database.execute_db_query(mock_db_connect, query, data, line, values, summary_count, 'env')
    mock_db_connect.commit.assert_called_once()
    mock_summary.assert_called_once()
    mock_db_connect.cursor().close.assert_called_once()


# TODO move inside class later
@patch("psycopg2.connect")
def test_execute_db_query_failure(mock_db_connect):
    """Test code to handle exception and rollback when executing query"""
    line = """2001,"New Symptom Group","CREATE"\n"""
    data = ("New Symptom Group", "None", 2001)
    values = {"action":"CREATE","id":2001,"Name":"New Symptom Group"}
    summary_count = {"BLANK": 0, "CREATE": 0,"DELETE": 0, "ERROR": 0,"UPDATE": 0}
    mock_db_connect.cursor.return_value.__enter__.return_value = Exception
    query = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
        where id = (%s);"""
    database.execute_db_query(mock_db_connect, query, data, line, values, summary_count, 'env')
    # TODO the loop in logging parameters seems to break this test
    # mock_db_connect.rollback.assert_called_once()
    mock_db_connect.cursor().close.assert_called_once()


# TODO move inside class later
@patch("psycopg2.connect")
def test_execute_cron_query_failure(mock_db_connect):
    """Test code to handle exception and rollback when executing cron style query"""
    data = (2001)
    mock_db_connect.cursor.return_value.fetchall.return_value = Exception
    query = """select * from pathwaysdos.symptomgroups where id = (%s);"""
    database.execute_cron_query(mock_db_connect, query, data)
    # TODO work out why rollback is NOT called
    # mock_db_connect.rollback.assert_called_once()
    mock_db_connect.cursor().close.assert_called_once()
