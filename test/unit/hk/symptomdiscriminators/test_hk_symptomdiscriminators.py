from unittest.mock import Mock, patch
import psycopg2
import pytest
from .. import handler

file_path = "application.hk.symptomdiscriminators.handler"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
start = ""


@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.common.process_file", return_value={"1": {"id": "00001", "description": "Mock Create SD", "action": "CREATE"}, "2": {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"}, "3": {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}})
@patch(f"{file_path}.extract_query_data_from_csv", return_value=("query", "data"))
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts")
@patch(f"{file_path}.common.cleanup")
@patch(f"{file_path}.message.send_start_message")
def test_request_success_with_check_table_for_id_is_true(mock_send_start_message, mock_cleanup, mock_report_summary_count ,mock_process_extracted_data, mock_extract_query_data_from_csv, mock_process_file, mock_retrieve_file_from_bucket, mock_db_connection):
    result = handler.request(mock_event, mock_context)
    assert result == "Symptom discriminators execution successful"
    mock_send_start_message.assert_called_once()
    mock_cleanup.assert_called_once()
    mock_process_extracted_data.assert_called_once()
    mock_extract_query_data_from_csv.assert_called_once()
    mock_report_summary_count.assert_called_once()
    mock_process_file.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()

@pytest.mark.skip
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.common.process_file", return_value={"1": {"id": "00001", "description": "Mock Create Role", "action": "CREATE"}, "2": {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"}, "3": {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}})
@patch(f"{file_path}.database.does_record_exist", return_value=False)
@patch(f"{file_path}.generate_db_query", return_value=("query", "data"))
@patch(f"{file_path}.database.execute_db_query")
@patch(f"{file_path}.common.cleanup")
@patch(f"{file_path}.message.send_start_message")
def test_request_success_with_check_table_for_id_is_false(mock_send_start_message, mock_cleanup, mock_execute_db_query, mock_generate_db_query, mock_check_table_for_id, mock_process_file, mock_retrieve_file_from_bucket, mock_db_connection):
    result = handler.request(mock_event, mock_context)
    assert result == "Symptom discriminators execution successful"
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
                "description": "Test Data",
                "action": "CREATE"
    }
    query, data = handler.create_query(test_values)
    assert query == """
        insert into pathwaysdos.symptomdiscriminators (id, description) values (%s, %s)
        returning id, description;
    """
    assert data == (10, "Test Data")


def test_update_query():
    test_values = {
        "id": 10,
        "description": "Test Data",
        "action": "UPDATE"
    }
    query, data = handler.update_query(test_values)
    assert query == """
        update pathwaysdos.symptomdiscriminators set description = (%s) where id = (%s);
    """
    assert data == ("Test Data", 10)


def test_delete_query():
    test_values = {
        "id": 10,
        "description": "Test Data",
        "action": "DELETE"
    }
    query, data = handler.delete_query(test_values)
    assert query == """
        delete from pathwaysdos.symptomdiscriminators where id = (%s)
    """
    assert data == (10,)


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_create(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00001", "description": "Mock Create SD", "action": "CREATE"}
    result = handler.generate_db_query(mock_row_values, mock_event, start)
    assert result == "Create Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_called_once_with(mock_row_values)

@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_update(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"}
    result = handler.generate_db_query(mock_row_values, mock_event, start)
    assert result == "Update Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_called_once_with(mock_row_values)
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_delete(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}
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
    mock_row_values = {"id": "00001", "description": "Mock Create SD", "action": "UNKNOWN"}
    with pytest.raises(psycopg2.DatabaseError) as assertion:
        result = handler.generate_db_query(mock_row_values, mock_event, start)
    assert str(assertion.value) == "Database Action UNKNOWN is invalid"
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_not_called()


# # @patch(f"{file_path}.database.DB")
# @patch("psycopg2.connect")
# def test_check_table_for_id_create_success(mock_db_connect):
#     mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
#     mock_line = "1"
#     mock_values = {"id": "00001", "description": "Mock Create SD", "action": "CREATE"}
#     mock_filename = ""
#     result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
#     assert result == True
#     mock_db_connect.cursor().__enter__().execute.assert_called_once()


# @patch("psycopg2.connect")
# def test_check_table_for_id_update_success(mock_db_connect):
#     mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
#     mock_line = "2"
#     mock_values = {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"}
#     mock_filename = ""
#     result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
#     assert result == True
#     mock_db_connect.cursor().__enter__().execute.assert_called_once()


# @patch("psycopg2.connect")
# def test_check_table_for_id_delete_success(mock_db_connect):
#     mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
#     mock_line = "3"
#     mock_values = {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}
#     mock_filename = ""
#     result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
#     assert result == True
#     mock_db_connect.cursor().__enter__().execute.assert_called_once()


# @patch("psycopg2.connect")
# def test_check_table_for_id_record_exists_returns_false_when_action_create(mock_db_connect):
#     mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
#     mock_line = "1"
#     mock_values = {"id": "00001", "description": "Mock Create SD", "action": "CREATE"}
#     mock_filename = ""
#     result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
#     assert result == False
#     mock_db_connect.cursor().__enter__().execute.assert_called_once()


# @patch("psycopg2.connect")
# def test_check_table_for_id_not_record_exists_returns_false_when_action_delete(mock_db_connect):
#     mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
#     mock_line = "3"
#     mock_values = {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}
#     mock_filename = ""
#     result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
#     assert result == False
#     mock_db_connect.cursor().__enter__().execute.assert_called_once()


# @patch(f"{file_path}.message.send_failure_slack_message")
# def test_check_table_for_id_raises_error(mock_send_failure_slack_message):
#     mock_db_connect = "mock connection"
#     mock_line = "1"
#     mock_values = {"id": "00001", "description": "Mock Create SD", "action": "CREATE"}
#     mock_filename = ""
#     with pytest.raises(Exception):
#         result = handler.check_table_for_id(mock_db_connect, mock_line, mock_values, mock_filename, mock_event, start)
#     mock_send_failure_slack_message.assert_called_once_with(mock_event, start)
