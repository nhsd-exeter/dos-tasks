from unittest.mock import Mock, patch
import psycopg2
import pytest
from .. import handler

file_path = "application.hk.symptomdiscriminators.handler"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
start = ""

# example 2001,"Symptom discriminator description","DELETE"
csv_sd_id = 2001
csv_sd_desc = "SD Automated Test"
csv_sd_action = "INSERT"


@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.common.process_file", return_value={"1": {"id": "00001", "description": "Mock Create SD", "action": "CREATE"}, "2": {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"}, "3": {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Symptom discriminators updated: 1, inserted: 1, deleted: 1")
@patch(f"{file_path}.common.cleanup")
@patch(f"{file_path}.message.send_start_message")
def test_request_success_with_check_table_for_id_is_true(mock_send_start_message, mock_cleanup,  mock_report_summary_count , mock_process_extracted_data, mock_process_file, mock_retrieve_file_from_bucket, mock_db_connection):
    result = handler.request(mock_event, mock_context)
    assert result == "Symptom discriminators execution successful"
    mock_send_start_message.assert_called_once()
    mock_cleanup.assert_called_once()
    mock_process_extracted_data.assert_called_once()
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
                "name": "Test Data",
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
        "name": "Test Data",
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
        "name": "Test Data",
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
    result = handler.generate_db_query(mock_row_values,mock_event, start)
    assert result == "Create Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_called_once_with(mock_row_values)

@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_update(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"}
    result = handler.generate_db_query(mock_row_values,mock_event, start)
    assert result == "Update Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_called_once_with(mock_row_values)
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_delete(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}
    result = handler.generate_db_query(mock_row_values,mock_event, start)
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
        result = handler.generate_db_query(mock_row_values,mock_event, start)
    assert str(assertion.value) == "Database Action UNKNOWN is invalid"
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_not_called()



@patch("psycopg2.connect")
def test_process_extracted_data_error_check_exists_fails(mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict={csv_sd_id,csv_sd_desc,"DELETE"}
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {}
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data, summary_count)

@patch("psycopg2.connect")
@patch(f"{file_path}.database.does_record_exist", return_value=True)
def test_process_extracted_data_error_check_exists_passes(mock_exists,mock_db_connect):
    """Test error handling when extracting data and record exist check passes"""
    row_data = {}
    csv_dict = {}
    csv_dict={csv_sd_id,csv_sd_desc,"DELETE"}
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {}
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event, start)
    assert mock_exists.call_count == 1

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_db_query")
@patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@patch(f"{file_path}.common.valid_action", return_value=True)
@patch(f"{file_path}.database.does_record_exist", return_value=True)
def test_process_extracted_data_single_record(mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for one record"""
    row_data = {}
    csv_dict={csv_sd_id,csv_sd_desc,"DELETE"}
    row_data[0]=csv_dict
    summary_count = {}
    summary_count = {}
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event, start)
    mock_valid_action.assert_called_once()
    mock_exist.assert_called_once()
    mock_generate.assert_called_once()
    mock_execute.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_db_query")
@patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@patch(f"{file_path}.common.valid_action", return_value=True)
@patch(f"{file_path}.database.does_record_exist", return_value=True)
def test_process_extracted_data_multiple_records(mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for each record"""
    row_data = {}
    csv_dict={}
    csv_dict={csv_sd_id,csv_sd_desc,"DELETE"}
    row_data[0]=csv_dict
    csv_dict={csv_sd_id,csv_sd_desc,"CREATE"}
    row_data[1]=csv_dict
    print(row_data[1])
    summary_count = {}
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event, start)
    assert mock_valid_action.call_count == 2
    assert mock_exist.call_count == 2
    assert mock_generate.call_count == 2
    assert mock_execute.call_count == 2
