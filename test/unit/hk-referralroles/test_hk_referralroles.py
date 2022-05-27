from unittest.mock import Mock, patch
import psycopg2
import pytest
# from .. import handler
from application.hk.referralroles import handler
# from _pytest.monkeypatch import MonkeyPatch

file_path = "application.hk.referralroles.handler"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
start = ""


@patch(f"{file_path}.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.process_file", return_value={"1": {"id": "001", "name": "Mock Create Role", "action": "CREATE"}, "2": {"id": "002", "name": "Mock Update Role", "action": "UPDATE"}, "3": {"id": "003", "name": "Mock Delete Role", "action": "DELETE"}})
@patch(f"{file_path}.check_table_for_id", return_value=True)
@patch(f"{file_path}.generate_db_query", return_value=("query", "data"))
@patch(f"{file_path}.execute_db_query")
@patch(f"{file_path}.cleanup")
@patch(f"{file_path}.message.send_start_message")
def test_request_success_with_check_table_for_id_is_true(mock_send_start_message, mock_cleanup, mock_execute_db_query, mock_generate_db_query, mock_check_table_for_id, mock_process_file, mock_retrieve_file_from_bucket, mock_db_connection):
    result = handler.request(mock_event, mock_context)
    assert result == "Referral Roles execution successful"
    mock_send_start_message.assert_called_once()
    mock_cleanup.assert_called_once()
    assert mock_execute_db_query.call_count == 3
    assert mock_generate_db_query.call_count == 3
    assert mock_check_table_for_id.call_count == 3
    mock_process_file.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()


@patch(f"{file_path}.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.process_file", return_value={"1": {"id": "001", "name": "Mock Create Role", "action": "CREATE"}, "2": {"id": "002", "name": "Mock Update Role", "action": "UPDATE"}, "3": {"id": "003", "name": "Mock Delete Role", "action": "DELETE"}})
@patch(f"{file_path}.check_table_for_id", return_value=False)
@patch(f"{file_path}.generate_db_query", return_value=("query", "data"))
@patch(f"{file_path}.execute_db_query")
@patch(f"{file_path}.cleanup")
@patch(f"{file_path}.message.send_start_message")
def test_request_success_with_check_table_for_id_is_false(mock_send_start_message, mock_cleanup, mock_execute_db_query, mock_generate_db_query, mock_check_table_for_id, mock_process_file, mock_retrieve_file_from_bucket, mock_db_connection):
    result = handler.request(mock_event, mock_context)
    assert result == "Referral Roles execution successful"
    mock_send_start_message.assert_called_once()
    mock_cleanup.assert_called_once()
    mock_execute_db_query.assert_not_called()
    mock_generate_db_query.assert_not_called()
    assert mock_check_table_for_id.call_count == 3
    mock_process_file.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()


def test_create_query():
    test_values = {
                "id": 10,
                "name": "Test Data",
                "action": "CREATE"
    }
    query, data = handler.create_query(test_values)
    assert query == """
        insert into pathwaysdos.referralroles (id, name) values (%s, %s)
        returning id, name;
    """
    assert data == (10, "Test Data")


def test_update_query():
    test_values = {
        "id": 10,
        "name": "Test Data",
        "action": "UPDATE"
    }
    query, data = handler.update_query(test_values)
    assert query == """
        update pathwaysdos.referralroles set name = (%s) where id = (%s);
    """
    assert data == ("Test Data", 10)


def test_delete_query():
    test_values = {
        "id": 10,
        "name": "Test Data",
        "action": "DELETE"
    }
    query, data = handler.delete_query(test_values)
    assert query == """
        delete from pathwaysdos.referralroles where id = (%s)
    """
    assert data == (10,)


@patch(f"{file_path}.database.DB")
def test_connect_to_database_success(mock_db_object):
    mock_db_object().db_set_connection_details = Mock(return_value=True)
    mock_db_object().db_connect = Mock(return_value="Connection Established")
    result = handler.connect_to_database(mock_env, mock_event, start)
    assert result == "Connection Established"
    mock_db_object().db_set_connection_details.assert_called_once()
    mock_db_object().db_connect.assert_called_once()


@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.database.DB")
def test_connect_to_database_returns_error(mock_db_object, mock_send_failure_slack_message):
    mock_db_object().db_set_connection_details = Mock(return_value=False)
    with pytest.raises(ValueError) as assertion:
        result = handler.connect_to_database(mock_env, mock_event, start)
    assert str(assertion.value) == "DB Parameter(s) not found in secrets store"
    mock_db_object().db_set_connection_details.assert_called_once()
    mock_send_failure_slack_message.assert_called_once()


@patch(f"{file_path}.s3.S3")
def test_retrieve_file_from_bucket(mock_s3_object):
    mock_s3_object().get_object = Mock(return_value="Object returned")
    mock_bucket = ""
    mock_filename = ""
    result = handler.retrieve_file_from_bucket(mock_bucket, mock_filename, mock_event, start)
    assert result == "Object returned"
    mock_s3_object().get_object.assert_called_once()


def test_process_file_success():
    mock_csv_file = """001,"Mock Create Role","CREATE"
002,"Mock Update Role","UPDATE"
003,"Mock Delete Role","DELETE"""
    lines = handler.process_file(mock_csv_file, mock_event, start)
    assert lines == {"1": {"id": "001", "name": "Mock Create Role", "action": "CREATE"},
                    "2": {"id": "002", "name": "Mock Update Role", "action": "UPDATE"},
                    "3": {"id": "003", "name": "Mock Delete Role", "action": "DELETE"}}


def test_process_file_success_with_empty_line():
    mock_csv_file = """
001,"Mock Create Role","CREATE"

002,"Mock Update Role","UPDATE"
003,"Mock Delete Role","DELETE"
"""
    lines = handler.process_file(mock_csv_file, mock_event, start)
    assert lines == {"2": {"id": "001", "name": "Mock Create Role", "action": "CREATE"},
                    "4": {"id": "002", "name": "Mock Update Role", "action": "UPDATE"},
                    "5": {"id": "003", "name": "Mock Delete Role", "action": "DELETE"}}


@patch(f"{file_path}.message.send_failure_slack_message")
def test_process_file_raises_error_with_incorrect_line_format(mock_send_failure_slack_message):
    mock_csv_file = """
001,"Mock Create Role","CREATE","Unexpected Data"
002,"Mock Update Role","UPDATE"
003,"Mock Delete Role","DELETE"
    """
    with pytest.raises(IndexError) as assertion:
        lines = handler.process_file(mock_csv_file, mock_event, start)
    assert str(assertion.value) == "Unexpected data in csv file"
    mock_send_failure_slack_message.assert_called_once()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_create(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "001", "name": "Mock Create Role", "action": "CREATE"}
    result = handler.generate_db_query(mock_row_values, mock_event, start)
    assert result == "Create Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_called_once_with(mock_row_values)

@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_update(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "002", "name": "Mock Update Role", "action": "UPDATE"}
    result = handler.generate_db_query(mock_row_values, mock_event, start)
    assert result == "Update Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_called_once_with(mock_row_values)
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_delete(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "003", "name": "Mock Delete Role", "action": "DELETE"}
    result = handler.generate_db_query(mock_row_values, mock_event, start)
    assert result == "Delete Query"
    mock_delete_query.assert_called_once_with(mock_row_values)
    mock_update_query.assert_not_called()
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
@patch(f"{file_path}.message.send_failure_slack_message")
def test_generate_db_query_raises_error(mock_send_failure_slack_message, mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "001", "name": "Mock Create Role", "action": "UNKNOWN"}
    with pytest.raises(psycopg2.DatabaseError) as assertion:
        result = handler.generate_db_query(mock_row_values, mock_event, start)
    assert str(assertion.value) == "Database Action UNKNOWN is invalid"
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_not_called()


# @patch(f"{file_path}.database.DB")
@patch("psycopg2.connect")
def test_check_table_for_id_create_success(mock_db_connect):
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
    mock_line = "1"
    mock_values = {"id": "001", "name": "Mock Create Role", "action": "CREATE"}
    mock_filename = ""
    result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
    assert result == True
    mock_db_connect.cursor().__enter__().execute.assert_called_once()


@patch("psycopg2.connect")
def test_check_table_for_id_update_success(mock_db_connect):
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
    mock_line = "2"
    mock_values = {"id": "002", "name": "Mock Update Role", "action": "UPDATE"}
    mock_filename = ""
    result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
    assert result == True
    mock_db_connect.cursor().__enter__().execute.assert_called_once()


@patch("psycopg2.connect")
def test_check_table_for_id_delete_success(mock_db_connect):
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
    mock_line = "3"
    mock_values = {"id": "003", "name": "Mock Delete Role", "action": "DELETE"}
    mock_filename = ""
    result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
    assert result == True
    mock_db_connect.cursor().__enter__().execute.assert_called_once()


@patch("psycopg2.connect")
def test_check_table_for_id_record_exists_returns_false_when_action_create(mock_db_connect):
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
    mock_line = "1"
    mock_values = {"id": "001", "name": "Mock Create Role", "action": "CREATE"}
    mock_filename = ""
    result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
    assert result == False
    mock_db_connect.cursor().__enter__().execute.assert_called_once()


@patch("psycopg2.connect")
def test_check_table_for_id_not_record_exists_returns_false_when_action_delete(mock_db_connect):
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
    mock_line = "3"
    mock_values = {"id": "003", "name": "Mock Delete Role", "action": "DELETE"}
    mock_filename = ""
    result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
    assert result == False
    mock_db_connect.cursor().__enter__().execute.assert_called_once()


@patch(f"{file_path}.message.send_failure_slack_message")
def test_check_table_for_id_raises_error(mock_send_failure_slack_message):
    mock_db_connect = "mock connection"
    mock_line = "1"
    mock_values = {"id": "001", "name": "Mock Create Role", "action": "CREATE"}
    mock_filename = ""
    with pytest.raises(Exception):
        result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)


@patch("psycopg2.connect")
def test_execute_db_query_success(mock_db_connect):
    mock_db_connect.cursor.return_value.__enter__.return_value = "Success"
    mock_query = ""
    mock_data = ""
    mock_line = ""
    mock_values = ""
    result = handler.execute_db_query(mock_db_connect, mock_query, mock_data, mock_line, mock_values)
    mock_db_connect.commit.assert_called_once()
    mock_db_connect.cursor().close.assert_called_once()


@patch("psycopg2.connect")
def test_execute_db_query_rollback(mock_db_connect):
    mock_db_connect.cursor.return_value.__enter__.return_value = Exception
    mock_query = ""
    mock_data = ""
    mock_line = ""
    mock_values = ""
    result = handler.execute_db_query(mock_db_connect, mock_query, mock_data, mock_line, mock_values)
    mock_db_connect.rollback.assert_called_once()
    mock_db_connect.cursor().close.assert_called_once()


@patch("psycopg2.connect")
@patch(f"{file_path}.s3.S3")
@patch(f"{file_path}.message.send_success_slack_message")
def test_cleanup_success(mock_send_success_slack_message, mock_s3_object, mock_db_connect):
    mock_db_connect.close.return_value = "Closed connection"
    mock_s3_object().copy_object = Mock(return_value="Object copied")
    mock_s3_object().delete_object = Mock(return_value="Object deleted")
    mock_bucket = ""
    mock_filename = "local/DPTS-001_referralroles.csv"
    result = handler.cleanup(mock_db_connect, mock_bucket, mock_filename, mock_event, start)
    assert result == "Cleanup Successful"
    mock_db_connect.close.assert_called_once()
    mock_s3_object().copy_object.assert_called_once_with(mock_bucket, mock_filename, mock_event, start)
    mock_s3_object().delete_object.assert_called_once_with(mock_bucket, mock_filename, mock_event, start)
    mock_send_success_slack_message.assert_called_once_with(mock_event, start)
