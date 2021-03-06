from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from .. import handler
from utilities import secrets,common

file_path = "application.hk.symptomgroups.handler"
filename = "test/sg.csv"
bucket = "NoSuchBucket"
env = "unittest"

# example 2001,"Symptom group description","DELETE"
csv_sg_id = 2001
csv_sg_desc = "Automated Test"
csv_sg_action = "REMOVE"

def test_csv_line():
    """Test data extracted from valid csv"""
    csv_rows = {}
    csv_rows["1"]={"id": csv_sg_id, "name": csv_sg_desc, "action": csv_sg_action}
    csv_dict = handler.extract_query_data_from_csv(csv_rows, 'env')
    assert len(csv_dict) == 1
    assert len(csv_dict["1"]) == 4
    assert csv_dict["1"]["id"] == csv_sg_id
    assert csv_dict["1"]["name"] == str(csv_sg_desc)
    assert csv_dict["1"]["action"] == str(csv_sg_action).upper()
    assert csv_dict["1"]["zcode"] is False


def test_csv_line_lc():
    """Test lower case action in csv is converted to u/c"""
    csv_rows = {}
    csv_sg_action = "remove"
    csv_rows["1"]={"id": csv_sg_id, "name": csv_sg_desc, "action": csv_sg_action}
    csv_dict = handler.extract_query_data_from_csv(csv_rows, 'env')
    assert len(csv_dict) == 1
    assert len(csv_dict["1"]) == 4
    assert csv_dict["1"]["id"] == csv_sg_id
    assert csv_dict["1"]["name"] == str(csv_sg_desc)
    assert csv_dict["1"]["action"] == str(csv_sg_action).upper()
    assert csv_dict["1"]["zcode"] is False


def test_zcode_sgdesc_csv_line():
    """Test extract correctly recognises zcodes"""
    csv_rows = {}
    csv_rows["1"]={"id": csv_sg_id, "name": "z2.0 - test", "action": csv_sg_action}
    csv_dict = handler.extract_query_data_from_csv(csv_rows, 'env')
    assert len(csv_dict) == 1
    assert len(csv_dict["1"]) == 4
    assert csv_dict["1"]["zcode"] is True



def test_csv_line_exception():
    """Test exception handling by deliberately setting action to NOT a string"""
    csv_rows = {}
    csv_rows["1"]={"id": csv_sg_id, "name": "z2.0 - test", "action": 1}
    with pytest.raises(Exception):
        handler.extract_query_data_from_csv(csv_rows, 'env')

def test_generating_create_query():
    """Test creation of insert query and data arguments"""
    create_query_string = """insert into pathwaysdos.symptomgroups(id,name,zcodeexists)
        values (%s, %s, %s)
        returning
        id,
        name,
        zcodeexists;"""
    remove = string.punctuation + string.whitespace

    csv_dict = {}
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "CREATE"
    query, data = handler.generate_db_query(csv_dict, 'test')
    mapping = {ord(c): None for c in remove}
    assert query.translate(mapping) == create_query_string.translate(mapping),"Query syntax mismatched"
    assert data[0] == csv_dict["id"]
    assert data[1] == csv_dict["name"]

def test_generating_update_query():
    """Test creation of update query and data arguments"""
    update_query_string = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
        where id = (%s);"""
    remove = string.punctuation + string.whitespace

    csv_dict = {}
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "UPDATE"
    query, data = handler.generate_db_query(csv_dict, 'test')
    mapping = {ord(c): None for c in remove}
    assert query.translate(mapping) == update_query_string.translate(mapping),"Query syntax mismatched"
    assert data[0] == csv_dict["name"]
    assert data[1] == csv_dict["zcode"]
    assert data[2] == csv_dict["id"]

def test_generating_delete_query():
    """Test creation of delete query and data argument"""
    delete_query_string = """delete from pathwaysdos.symptomgroups where id = (%s)"""
    remove = string.punctuation + string.whitespace
    csv_dict = {}
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "DELETE"
    query, data = handler.generate_db_query(csv_dict, 'test')
    mapping = {ord(c): None for c in remove}
    assert query.translate(mapping) == delete_query_string.translate(mapping),"Query syntax mismatched"
    assert data[0] == csv_dict["id"]

def test_generating_query_with_invalid_action():
    """Test creation of query and data arguments for unrecognized action"""
    csv_dict = {}
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "REMOVE"
    with pytest.raises(psycopg2.DatabaseError):
        query, data = handler.generate_db_query(csv_dict, 'test')


@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_db_query")
@patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@patch(f"{file_path}.common.valid_action", return_value=True)
@patch(f"{file_path}.database.does_record_exist", return_value=True)
def test_process_extracted_data_single_record(mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for one record"""
    row_data = {}
    csv_dict={}
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "DELETE"
    row_data[0]=csv_dict
    summary_count = {}
    event = generate_event_payload()
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, event)
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
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "DELETE"
    row_data[0]=csv_dict
    row_data[1]=csv_dict
    summary_count = {}
    event = generate_event_payload()
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, event)
    assert mock_valid_action.call_count == 2
    assert mock_exist.call_count == 2
    assert mock_generate.call_count == 2
    assert mock_execute.call_count == 2

@patch("psycopg2.connect")
@patch(f"{file_path}.common.increment_summary_count")
def test_process_extracted_data_error_check_exists_fails(mock_increment_count,mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict = {}
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "DELETE"
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {}
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data, summary_count)
    mock_increment_count.called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.logger.log_for_error")
@patch(f"{file_path}.database.does_record_exist", return_value=True)
def test_process_extracted_data_error_check_exists_passes(mock_exists,mock_logger,mock_db_connect):
    """Test error handling when extracting data and record exist check passes"""
    row_data = {}
    csv_dict = {}
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "DELETE"
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {"BLANK": 0, "CREATE": 0,"DELETE": 0, "ERROR": 0,"UPDATE": 0}
    event = generate_event_payload()
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data, summary_count, event)
    assert mock_logger.call_count == 1
    assert mock_exists.call_count == 1

@patch("psycopg2.connect")
@patch(f"{file_path}.common.increment_summary_count")
@patch(f"{file_path}.database.does_record_exist", return_value=True)
@patch(f"{file_path}.common.valid_action", return_value=False)
def test_process_extracted_data_valid_action_fails(mock_valid_action,mock_exists,mock_increment,mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict = {}
    csv_dict["id"] = csv_sg_id
    csv_dict["name"] = csv_sg_desc
    csv_dict["zcode"] = False
    csv_dict["action"] = "INVALID"
    row_data[0]=csv_dict
    summary_count = {}
    event = generate_event_payload()
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, event)
    assert mock_exists.call_count == 1
    assert mock_valid_action.call_count == 1
    assert mock_increment.call_count == 1

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
@patch(f"{file_path}.common.process_file", return_value={"1": {"id": "00001", "name": "Mock Create SD", "action": "CREATE"}, "2": {"id": "00002", "name": "Mock Update SD", "action": "UPDATE"}, "3": {"id": "00003", "name": "Mock Delete SD", "action": "DELETE"}})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Referral roles updated: 1, inserted: 1, deleted: 1")
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
    assert result == "Symptom Groups execution completed"
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


@patch(f"{file_path}.common.initialise_summary_count")
@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.common.process_file", return_value={})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Referral roles updated: 1, inserted: 1, deleted: 1")
@patch(f"{file_path}.message.send_start_message")
def test_handler_empty_file(mock_send_start_message,
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
    assert result == "Symptom Groups execution completed"
    mock_send_start_message.assert_called_once()
    mock_summary_count.assert_called_once()
    mock_report_summary_count.assert_called_once()
    mock_process_file.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()
    mock_close_connection.assert_called_once()
    mock_archive_file.assert_called_once()
    assert mock_process_extracted_data.call_count == 0
    assert mock_send_success_slack_message.call_count == 0
    mock_send_failure_slack_message.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.common.cleanup")
@patch(f"{file_path}.database.does_record_exist", return_value=False)
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.message.send_start_message")
def test_handler_fail(mock_send_start_message,mock_db_details,mock_get_object,
mock_does_record_exist,mock_cleanup,mock_db_connect):
    """Test top level function handles errors thrown by downstream functions"""
    payload = generate_event_payload()
    handler.request(event=payload, context=None)
    assert mock_send_start_message.call_count == 1
    mock_get_object.assert_called_once()
    mock_cleanup.assert_called_once()
    mock_does_record_exist.assert_called_once()

@patch(f"{file_path}.common.initialise_summary_count")
@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file", side_effect=ValueError)
@patch(f"{file_path}.common.process_file", return_value={"1": {"id": "00001", "name": "Mock Create SD", "action": "CREATE"}, "2": {"id": "00002", "name": "Mock Update SD", "action": "UPDATE"}, "3": {"id": "00003", "name": "Mock Delete SD", "action": "DELETE"}})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Referral roles updated: 1, inserted: 1, deleted: 1")
@patch(f"{file_path}.message.send_start_message")
def test_handler_fail(mock_send_start_message,
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
    assert result == "Symptom Groups execution completed"
    assert mock_send_start_message.call_count == 1
    assert mock_process_extracted_data.call_count == 0
    assert mock_report_summary_count.call_count == 0
    assert mock_process_file.call_count == 0
    assert mock_retrieve_file_from_bucket.call_count == 1
    assert mock_db_connection.call_count == 1
    mock_close_connection.assert_called_once()
    mock_archive_file.assert_called_once()
    assert mock_send_success_slack_message.call_count == 0
    mock_send_failure_slack_message.assert_called_once()


def generate_event_payload():
    """Utility function to generate dummy event data"""
    return {"filename": filename, "env": env, "bucket": bucket}
