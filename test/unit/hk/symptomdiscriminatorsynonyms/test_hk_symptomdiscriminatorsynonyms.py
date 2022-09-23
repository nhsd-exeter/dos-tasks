from unittest.mock import Mock, patch
import psycopg2
import pytest
from .. import handler

file_path = "application.hk.symptomdiscriminatorsynonyms.handler"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
mock_bucket = "NoSuchBucket"
start = ""
mock_filename = "test/sds.csv"


# example 2001,"Symptom discriminator description","DELETE"
csv_sds_id = 2001
csv_sds_desc = "SDS Automated Test"
csv_sds_action = "INSERT"



@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
@patch(f"{file_path}.message.send_start_message", return_value = None)
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value = None)
def test_handler_exception(mock_db,mock_failure_message,mock_message_start,mock_s3):
    """Test clean up function handling exceptions from downstream functions"""
    payload = generate_event_payload()
    with pytest.raises(Exception):
        handler.request(event=payload, context=None)


@patch(f"{file_path}.common.initialise_summary_count")
@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.common.process_file", return_value={"1": {"id": "00001", "description": "Mock Create SDS", "action": "CREATE"}, "2": {"id": "00002", "description": "Mock Update SDS", "action": "UPDATE"}, "3": {"id": "00003", "description": "Mock Delete SDS", "action": "DELETE"}})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="SDS updated: 1, inserted: 1, deleted: 1")
@patch(f"{file_path}.message.send_start_message")
def test_handler_pass(mock_send_start_message,
mock_report_summary_count ,
mock_process_extracted_data,
mock_process_file,
mock_retrieve_file_from_bucket,
mock_db_connection,
mock_close_connection,
mock_send_success_slack_message,
mock_send_failure_slack_message,
mock_archive_file,
mock_summary_count):
    """Test top level request calls downstream functions - success"""
    payload = generate_event_payload()
    result = handler.request(event=payload, context=None)
    assert result == "Symptom discriminator synonyms execution completed"
    mock_send_start_message.assert_called_once()
    mock_process_extracted_data.assert_called_once()
    mock_summary_count.assert_called_once()
    mock_report_summary_count.assert_called_once()
    mock_process_file.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()
    mock_close_connection.assert_called_once()
    mock_archive_file.assert_called_once()
    mock_send_success_slack_message.assert_called_once()
    assert mock_send_failure_slack_message.call_count == 0

def test_create_query():
    test_values = {
                "id": 10,
                "name": "Test Data",
                "action": "CREATE"
    }
    query, data = handler.create_query(test_values)
    assert query == """
        insert into pathwaysdos.symptomdiscriminatorsynonyms (symptomdiscriminatorid, name) values (%s, %s)
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
        update pathwaysdos.symptomdiscriminatorsynonyms set name = (%s) where symptomdiscriminatorid = (%s);
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
        delete from pathwaysdos.symptomdiscriminatorsynonyms where symptomdiscriminatorid = (%s)
    """
    assert data == (10,)


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_create(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00001", "description": "Mock Create SDS", "action": "CREATE"}
    result = handler.generate_db_query(mock_row_values,mock_env)
    assert result == "Create Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_called_once_with(mock_row_values)

@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_update(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00002", "description": "Mock Update SDS", "action": "UPDATE"}
    result = handler.generate_db_query(mock_row_values,mock_env)
    assert result == "Update Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_called_once_with(mock_row_values)
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_delete(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00003", "description": "Mock Delete SDS", "action": "DELETE"}
    result = handler.generate_db_query(mock_row_values,mock_env)
    assert result == "Delete Query"
    mock_delete_query.assert_called_once_with(mock_row_values)
    mock_update_query.assert_not_called()
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_raises_error(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00001", "description": "Mock Create SDS", "action": "UNKNOWN"}
    with pytest.raises(psycopg2.DatabaseError) as assertion:
        result = handler.generate_db_query(mock_row_values,mock_env)
    assert str(assertion.value) == "Database Action UNKNOWN is invalid"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_not_called()



@patch("psycopg2.connect")
def test_process_extracted_data_error_check_exists_fails(mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict={csv_sds_id,csv_sds_desc,"DELETE"}
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {}
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_env,mock_db_connect, row_data, summary_count)

@patch("psycopg2.connect")
@patch(f"{file_path}.database.does_record_exist", return_value=True)
def test_process_extracted_data_error_check_exists_passes(mock_exists,mock_db_connect):
    """Test error handling when extracting data and record exist check passes"""
    row_data = {}
    csv_dict = {}
    csv_dict={csv_sds_id,csv_sds_desc,"DELETE"}
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {}
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_env,mock_db_connect, row_data, summary_count, mock_event, start)
    assert mock_exists.call_count == 1

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_db_query")
@patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@patch(f"{file_path}.common.valid_action", return_value=True)
@patch(f"{file_path}.database.does_record_exist", return_value=True)
def test_process_extracted_data_single_record(mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for one record"""
    row_data = {}
    csv_dict={csv_sds_id,csv_sds_desc,"DELETE"}
    row_data[0]=csv_dict
    summary_count = {}
    summary_count = {}
    handler.process_extracted_data(mock_env,mock_db_connect, row_data, summary_count, mock_event, start)
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
    csv_dict={csv_sds_id,csv_sds_desc,"DELETE"}
    row_data[0]=csv_dict
    csv_dict={csv_sds_id,csv_sds_desc,"CREATE"}
    row_data[1]=csv_dict
    print(row_data[1])
    summary_count = {}
    handler.process_extracted_data(mock_env,mock_db_connect, row_data, summary_count, mock_event, start)
    assert mock_valid_action.call_count == 2
    assert mock_exist.call_count == 2
    assert mock_generate.call_count == 2
    assert mock_execute.call_count == 2


def generate_event_payload():
    """Utility function to generate dummy event data"""
    return {"filename": mock_filename, "env": mock_env, "bucket": mock_bucket}
