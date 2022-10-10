from unittest.mock import Mock, patch
import psycopg2
import pytest
from .. import handler

file_path = "application.hk.symptomgroupdiscriminators.handler"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
mock_bucket = "NoSuchBucket"
start = ""
mock_filename = "test/sgd.csv"


# example 2001,"Symptom discriminator description","DELETE"
csv_sgd_sgid = 2001
csv_sgd_sdid = 11009
csv_sgd_action = "INSERT"



@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
@patch(f"{file_path}.message.send_start_message", return_value = None)
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value = None)
def test_handler_exception(mock_db,mock_failure_message,mock_message_start,mock_s3):
    """Test clean up function handling exceptions from downstream functions"""
    payload = generate_event_payload()
    with pytest.raises(Exception):
        handler.request(event=payload, context=None)

@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
@patch(f"{file_path}.message.send_start_message", return_value = None)
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value = None)
@patch(f"{file_path}.common_file_processing.process_ids_file", return_value = {})
def test_handler_empty_file(mock_db,mock_failure_message,mock_message_start,mock_s3, mock_csv_file):
    """Test clean up function handling exceptions from downstream functions"""
    payload = generate_event_payload()
    with pytest.raises(Exception):
        handler.request(event=payload, context=None)
    mock_failure_message.assert_called_once()

@patch(f"{file_path}.common.initialise_summary_count")
@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.common_file_processing.process_ids_file", return_value={"1": {"id1": "00001", "id2": "100001", "action": "CREATE"}, "2": {"id1": "00002", "sgid": "110001", "action": "DELETE"}})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="SGD updated: 0, inserted: 1, deleted: 1")
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
    assert result == "Symptom group symptom discriminators execution completed"
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
                "id1": 10,
                "id2": 123,
                "action": "CREATE"
    }
    query, data = handler.create_query(test_values)
    assert query == """
        insert into pathwaysdos.symptomgroupsymptomdiscriminators
        (symptomgroupid, symptomdiscriminatorid) values (%s, %s)
        returning symptomgroupid, symptomdiscriminatorid;
    """
    assert data == (10, 123)


def test_delete_query():
    test_values = {
        "id1": 10,
        "id2": 123,
        "action": "DELETE"
    }
    query, data = handler.delete_query(test_values)
    assert query == """
        delete from pathwaysdos.symptomgroupsymptomdiscriminators
        where symptomgroupid = (%s) and symptomdiscriminatorid = (%s)
    """
    assert data == (10, 123)


def test_record_exists_query():
    test_values = {
        "id1": 10,
        "id2": 123,
        "actid2ion": "DELETE"
    }
    query, data = handler.record_exists_query(test_values)
    assert query == """
        select * from pathwaysdos.symptomgroupsymptomdiscriminators
        where symptomgroupid = (%s) and symptomdiscriminatorid = (%s)
    """
    assert data == (10, 123)


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_create(mock_delete_query,  mock_create_query):
    mock_row_values = {"id1": "00001", "id2": "100001", "action": "CREATE"}
    result = handler.generate_db_query(mock_row_values,mock_env)
    assert result == "Create Query"
    mock_delete_query.assert_not_called()
    mock_create_query.assert_called_once_with(mock_row_values)



@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_delete(mock_delete_query,  mock_create_query):
    mock_row_values = {"id1": "00001", "id2": "100001", "action": "DELETE"}
    result = handler.generate_db_query(mock_row_values,mock_env)
    assert result == "Delete Query"
    mock_delete_query.assert_called_once_with(mock_row_values)
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_raises_error(mock_delete_query, mock_create_query):
    mock_row_values = {"id1": "00001", "id2": "100001", "action": "UPDATE"}
    with pytest.raises(psycopg2.DatabaseError) as assertion:
        result = handler.generate_db_query(mock_row_values,mock_env)
    assert str(assertion.value) == "Database Action UPDATE is invalid"
    mock_delete_query.assert_not_called()
    mock_create_query.assert_not_called()

@patch("psycopg2.connect")
@patch(f"{file_path}.common.increment_summary_count")
@patch(f"{file_path}.does_sgd_record_exist", return_value=True)
@patch(f"{file_path}.common.valid_action", return_value=False)
def test_process_extracted_data_valid_action_fails(mock_valid_action,mock_exists,mock_increment,mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict = {}
    csv_dict["id1"] = csv_sgd_sgid
    csv_dict["id2"] = csv_sgd_sdid
    csv_dict["action"] = "INVALID"
    row_data[0]=csv_dict
    summary_count = {}
    event = generate_event_payload()
    handler.process_extracted_data(mock_db_connect, row_data, summary_count,event)
    assert mock_exists.call_count == 1
    assert mock_valid_action.call_count == 1
    assert mock_increment.call_count == 1

@patch("psycopg2.connect")
def test_process_extracted_data_error_check_exists_fails(mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict={csv_sgd_sgid,csv_sgd_sdid,"DELETE"}
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {}
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_env,mock_db_connect, row_data, summary_count)

@patch("psycopg2.connect")
@patch(f"{file_path}.does_sgd_record_exist", return_value=True)
def test_process_extracted_data_error_check_exists_passes(mock_exists,mock_db_connect):
    """Test error handling when extracting data and record exist check passes"""
    row_data = {}
    csv_dict = {}
    csv_dict={csv_sgd_sgid,csv_sgd_sdid,"DELETE"}
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {}
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event)
    assert mock_exists.call_count == 1

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_db_query")
@patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@patch(f"{file_path}.common.valid_action", return_value=True)
@patch(f"{file_path}.does_sgd_record_exist", return_value=True)
def test_process_extracted_data_single_record(mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for one record"""
    row_data = {}
    csv_dict={csv_sgd_sgid,csv_sgd_sdid,"DELETE"}
    row_data[0]=csv_dict
    summary_count = {}
    summary_count = {}
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event)
    mock_valid_action.assert_called_once()
    mock_exist.assert_called_once()
    mock_generate.assert_called_once()
    mock_execute.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_db_query")
@patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@patch(f"{file_path}.common.valid_action", return_value=True)
@patch(f"{file_path}.does_sgd_record_exist", return_value=True)
def test_process_extracted_data_multiple_records(mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for each record"""
    row_data = {}
    csv_dict={}
    csv_dict={csv_sgd_sgid,csv_sgd_sdid,"DELETE"}
    row_data[0]=csv_dict
    csv_dict={csv_sgd_sgid,csv_sgd_sdid,"CREATE"}
    row_data[1]=csv_dict
    summary_count = {}
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event)
    assert mock_valid_action.call_count == 2
    assert mock_exist.call_count == 2
    assert mock_generate.call_count == 2
    assert mock_execute.call_count == 2



@patch("psycopg2.connect")
def test_sgd_record_exists_true(mock_db_connect):
    """Test correct data passed to check record exists - returning true"""
    csv_dict = {}
    csv_dict["id1"] = csv_sgd_sgid
    csv_dict["id2"] = csv_sgd_sdid
    csv_dict["action"] = "DELETE"
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
    assert handler.does_sgd_record_exist(mock_db_connect,csv_dict,'test')

@patch("psycopg2.connect")
def test_does_sgd_record_exist_false(mock_db_connect):
    """Test correct data passed to check record exists - returning false"""
    csv_dict = {}
    csv_dict["id1"] = csv_sgd_sgid
    csv_dict["id2"] = csv_sgd_sdid
    csv_dict["action"] = "DELETE"
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
    assert not handler.does_sgd_record_exist(mock_db_connect,csv_dict,'test')

@patch("psycopg2.connect")
def test_does_sgd_record_exist_exception(mock_db_connect):
    """Test throwing of exception """
    csv_dict = {}
    csv_dict["id1"] = csv_sgd_sgid
    csv_dict["id2"] = csv_sgd_sdid
    csv_dict["action"] = "DELETE"
    mock_db_connect = ""
    with pytest.raises(Exception):
        handler.does_sgd_record_exist(mock_db_connect,csv_dict,'test')


def generate_event_payload():
    """Utility function to generate dummy event data"""
    return {"filename": mock_filename, "env": mock_env, "bucket": mock_bucket}
