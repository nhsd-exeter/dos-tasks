from unittest.mock import  patch
import psycopg2
import pytest
from .. import handler

file_path = "application.hk.servicetypes.handler"
mock_filename = "test/st.csv"
mock_bucket = "NoSuchBucket"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
start = ""

v_searchcapacitystatus = True
v_capacitymodel = "n/a"
v_capacityreset = "interval"

# example 55,"Service type description", 1, "INSERT"
csv_st_id = 55
csv_st_name = "ST Automated Test"
csv_st_rank = 1
csv_st_action = "CREATE"

def test_csv_line():
    """Test data extracted from valid csv"""
    csv_rows = {}
    csv_rows["1"]={"id": csv_st_id, "name": csv_st_name, "nationalranking": csv_st_rank, "action": csv_st_action}
    csv_dict = handler.extract_query_data_from_csv(csv_rows)
    assert len(csv_dict) == 1
    assert len(csv_dict["1"]) == 7
    assert csv_dict["1"]["id"] == csv_st_id
    assert csv_dict["1"]["name"] == str(csv_st_name)
    assert csv_dict["1"]["nationalranking"] == csv_st_rank
    assert csv_dict["1"]["searchcapacitystatus"] == v_searchcapacitystatus
    assert csv_dict["1"]["capacitymodel"] == str(v_capacitymodel)
    assert csv_dict["1"]["capacityreset"] == str(v_capacityreset)
    assert csv_dict["1"]["action"] == str(csv_st_action).upper()

def test_csv_line():
    """Test data extracted from valid csv"""
    csv_rows = {}
    csv_rows["1"]={"id": csv_st_id, "name": csv_st_name, "nationalranking": csv_st_rank, "action": csv_st_action}
    csv_dict = handler.extract_query_data_from_csv(csv_rows,mock_env)
    assert len(csv_dict) == 1
    assert len(csv_dict["1"]) == 7
    assert csv_dict["1"]["id"] == csv_st_id
    assert csv_dict["1"]["name"] == str(csv_st_name)
    assert csv_dict["1"]["nationalranking"] == csv_st_rank
    assert csv_dict["1"]["action"] == str(csv_st_action)
    assert csv_dict["1"]["searchcapacitystatus"] == v_searchcapacitystatus
    assert csv_dict["1"]["capacitymodel"] == str(v_capacitymodel)
    assert csv_dict["1"]["capacityreset"] == str(v_capacityreset)

def test_csv_line_lc():
    """Test lower case action in csv is converted to u/c"""
    csv_rows = {}
    csv_st_action = "remove"
    csv_rows["1"]={"id": csv_st_id, "name": csv_st_name, "nationalranking": csv_st_rank, "action": csv_st_action}
    csv_dict = handler.extract_query_data_from_csv(csv_rows, mock_env)
    assert len(csv_dict) == 1
    assert len(csv_dict["1"]) == 7
    assert csv_dict["1"]["id"] == csv_st_id
    assert csv_dict["1"]["name"] == str(csv_st_name)
    assert csv_dict["1"]["nationalranking"] == csv_st_rank
    assert csv_dict["1"]["action"] == str(csv_st_action).upper()
    assert csv_dict["1"]["searchcapacitystatus"] == v_searchcapacitystatus
    assert csv_dict["1"]["capacitymodel"] == str(v_capacitymodel)
    assert csv_dict["1"]["capacityreset"] == str(v_capacityreset)


def test_csv_line_exception():
    """Test exception handling by deliberately setting action to NOT a string"""
    csv_rows = {}
    csv_rows["1"]={"id": csv_st_id, "name": csv_st_name, "nationalranking": csv_st_rank, "action": 1}
    with pytest.raises(Exception):
        handler.extract_query_data_from_csv(csv_rows, mock_env)


@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.process_servicetypes_file", return_value={})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Service types updated: 1, inserted: 1, deleted: 1")
@patch(f"{file_path}.message.send_start_message")
def test_request_empty_file(mock_send_start_message,
mock_report_summary_count ,
mock_process_extracted_data,
mock_process_file,
mock_retrieve_file_from_bucket,
mock_db_connection,
mock_close_connection,
mock_send_success_slack_message,
mock_send_failure_slack_message,
mock_archive_file):
    result = handler.request(mock_event, mock_context)
    assert result == "Service types execution completed"
    mock_send_start_message.assert_called_once()
    mock_report_summary_count.assert_called_once()
    mock_process_file.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()
    mock_close_connection.assert_called_once()
    mock_archive_file.assert_called_once()
    mock_send_failure_slack_message.assert_called_once()
    assert mock_send_success_slack_message.call_count == 0
    assert mock_process_extracted_data.call_count == 0


def test_create_query():
    test_values = {
                "id": 1000,
                "name": "Test Data",
                "nationalranking": 1,
                "searchcapacitystatus": "true",
                "capacitymodel": "n/a",
                "capacityreset": "interval",
                "action": "CREATE"
    }
    query, data = handler.create_query(test_values)
    assert query == """
        insert into pathwaysdos.servicetypes
        (id, name, nationalranking, searchcapacitystatus, capacitymodel, capacityreset)
        values (%s, %s, %s, %s, %s, %s)
        returning id, name, nationalranking, searchcapacitystatus, capacitymodel, capacityreset;
    """
    assert data == (1000, "Test Data", 1, "true", "n/a", "interval")


def test_update_query():
    test_values = {
        "id": 1000,
        "name": "Test Data",
        "nationalranking": 1,
        "searchcapacitystatus": "true",
        "capacitymodel": "n/a",
        "capacityreset": "interval",
        "action": "UPDATE"
    }
    query, data = handler.update_query(test_values)
    assert query == """
        update pathwaysdos.servicetypes
        set name = (%s),
        nationalranking = (%s),
        searchcapacitystatus = (%s),
        capacitymodel = (%s),
        capacityreset = (%s)
        where id = (%s);
    """
    assert data == ("Test Data", 1, "true", "n/a", "interval", 1000)


def test_delete_query():
    test_values = {
        "id": 1000,
        "name": "Test Data",
        "action": "DELETE"
    }
    query, data = handler.delete_query(test_values)
    assert query == """
        delete from pathwaysdos.servicetypes where id = (%s)
    """
    assert data == (1000,)


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_create(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00001", "name": "Mock Create ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "CREATE"}
    result = handler.generate_db_query(mock_row_values,mock_event)
    assert result == "Create Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_called_once_with(mock_row_values)


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_update(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00002", "name": "Mock Update ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "UPDATE"}
    result = handler.generate_db_query(mock_row_values,mock_event)
    assert result == "Update Query"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_called_once_with(mock_row_values)
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_delete(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00003", "name": "Mock Delete ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "DELETE"}
    result = handler.generate_db_query(mock_row_values,mock_event)
    assert result == "Delete Query"
    mock_delete_query.assert_called_once_with(mock_row_values)
    mock_update_query.assert_not_called()
    mock_create_query.assert_not_called()


@patch(f"{file_path}.create_query", return_value="Create Query")
@patch(f"{file_path}.update_query", return_value="Update Query")
@patch(f"{file_path}.delete_query", return_value="Delete Query")
def test_generate_db_query_raises_error(mock_delete_query, mock_update_query, mock_create_query):
    mock_row_values = {"id": "00001", "description": "Mock Create ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "UNKNOWN"}
    with pytest.raises(psycopg2.DatabaseError) as assertion:
        handler.generate_db_query(mock_row_values,mock_event)
    assert str(assertion.value) == "Database Action UNKNOWN is invalid"
    mock_delete_query.assert_not_called()
    mock_update_query.assert_not_called()
    mock_create_query.assert_not_called()

@patch("psycopg2.connect")
@patch(f"{file_path}.common.increment_summary_count")
def test_process_extracted_data_error_check_exists_fails(mock_increment_count,mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict={csv_st_id,csv_st_name,csv_st_rank,"DELETE"}
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
    csv_dict["id"] = csv_st_id
    csv_dict["name"] = csv_st_name
    csv_dict["nationalranking"] = csv_st_rank
    csv_dict["searchcapacitystatus"] = v_searchcapacitystatus
    csv_dict["capacitymodel"] = v_capacitymodel
    csv_dict["capacityreset"] = v_capacityreset
    csv_dict["action"] = "UPDATE"
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {"BLANK": 0, "CREATE": 0,"DELETE": 0, "ERROR": 0,"UPDATE": 0}
    event = generate_event_payload()
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data, summary_count, event)
    assert mock_logger.call_count == 1
    assert mock_exists.call_count == 1



@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_db_query")
@patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@patch(f"{file_path}.common.valid_action", return_value=True)
@patch(f"{file_path}.database.does_record_exist", return_value=True)
@patch(f"{file_path}.common.increment_summary_count")
def test_process_extracted_data_single_record(mock_increment_count,mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for one record"""
    row_data = {}
    csv_dict={csv_st_id,csv_st_name,csv_st_rank,"DELETE"}
    row_data[0]=csv_dict
    summary_count = {}
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event)
    mock_increment_count.assert_not_called()
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
    csv_dict={csv_st_id,csv_st_name,csv_st_rank,"DELETE"}
    row_data[0]=csv_dict
    csv_dict={csv_st_id,csv_st_name,csv_st_rank,"CREATE"}
    row_data[1]=csv_dict
    summary_count = {}
    handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event)
    assert mock_valid_action.call_count == 2
    assert mock_exist.call_count == 2
    assert mock_generate.call_count == 2
    assert mock_execute.call_count == 2



@patch("psycopg2.connect")
@patch(f"{file_path}.common.increment_summary_count")
@patch(f"{file_path}.database.does_record_exist", return_value=True)
@patch(f"{file_path}.common.valid_action", return_value=False)
def test_process_extracted_data_valid_action_fails(mock_valid_action,mock_exists,mock_increment,mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict={}
    csv_dict={csv_st_id,csv_st_name,csv_st_rank,"INVALID"}
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
@patch(f"{file_path}.process_servicetypes_file", return_value={"1": {"id": "00001", "name": "Mock Delete ST", "nationalranking":1 , "action": "DELETE"}, "2": {"id": "00002", "name": "Mock Delete ST", "nationalranking":1,  "action": "UPDATE"}, "3": {"id": "00003", "name": "Mock Delete ST", "nationalranking":1, "action": "DELETE"}})
@patch(f"{file_path}.extract_query_data_from_csv", return_value={"1": {"id": "00001", "name": "Mock Delete ST", "nationalranking":1 ,"searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval",  "action": "DELETE"}, "2": {"id": "00002", "name": "Mock Delete ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "UPDATE"}, "3": {"id": "00003", "name": "Mock Delete ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "DELETE"}})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Service types updated: 1, inserted: 1, deleted: 1")
@patch(f"{file_path}.message.send_start_message")
def test_handler_pass(mock_send_start_message,
mock_report_summary_count ,
mock_process_extracted_data,
mock_extra_query_data_from_file,
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
    assert result == "Service types execution completed"
    mock_send_start_message.assert_called_once()
    mock_process_extracted_data.assert_called_once()
    mock_extra_query_data_from_file.assert_called_once()
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
@patch(f"{file_path}.process_servicetypes_file", return_value={})
@patch(f"{file_path}.extract_query_data_from_csv", return_value={})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Service types updated: 1, inserted: 1, deleted: 1")
@patch(f"{file_path}.message.send_start_message")
def test_handler_empty_file(mock_send_start_message,
mock_report_summary_count ,
mock_process_extracted_data,
mock_extract_query_data_from_csv,
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
    assert result == "Service types execution completed"
    mock_send_start_message.assert_called_once()
    mock_summary_count.assert_called_once()
    mock_report_summary_count.assert_called_once()
    mock_process_file.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()
    mock_close_connection.assert_called_once()
    mock_archive_file.assert_called_once()
    assert mock_extract_query_data_from_csv.call_count == 0
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
@patch(f"{file_path}.process_servicetypes_file", return_value={"1": {"id": "00001", "name": "Mock Delete ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "DELETE"}, "2": {"id": "00002", "name": "Mock Delete ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "UPDATE"}, "3": {"id": "00003", "name": "Mock Delete ST", "nationalranking":1, "searchcapacitystatus":"true", "capacitymodel":"n/a", "capacityreset":"interval", "action": "DELETE"}})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Service types updated: 1, inserted: 1, deleted: 1")
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
    assert result == "Service types execution completed"
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


def test_process_file_success():
    summary_count_dict = {}
    summary_count_dict = {"BLANK": 0, "CREATE": 0,"DELETE": 0, "ERROR": 0,"UPDATE": 0}
    mock_csv_file = """00001,"Mock Create ST",4,CREATE
00002,"Mock Update ST",4,UPDATE
00003,"Mock Delete ST",4,DELETE"""
    lines = handler.process_servicetypes_file(mock_csv_file, mock_event, 4 , summary_count_dict)
    assert lines == {"1": {"id": "00001", "name": "Mock Create ST", "nationalranking": "4", "action": "CREATE"},
                    "2": {"id": "00002", "name": "Mock Update ST", "nationalranking": "4", "action": "UPDATE"},
                    "3": {"id": "00003", "name": "Mock Delete ST", "nationalranking": "4", "action": "DELETE"}}


def test_process_file_success_with_empty_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """
00001,"Mock Create ST",4,"CREATE"

00002,"Mock Update ST",4,"UPDATE"
00003,"Mock Delete ST",4,"DELETE"
"""
    lines = handler.process_servicetypes_file(mock_csv_file, mock_event, 4, summary_count_dict)
    assert lines == {"2": {"id": "00001", "name": "Mock Create ST", "nationalranking": "4","action": "CREATE"},
                    "4": {"id": "00002", "name": "Mock Update ST", "nationalranking": "4","action": "UPDATE"},
                    "5": {"id": "00003", "name": "Mock Delete ST", "nationalranking": "4","action": "DELETE"}}


def test_process_file_success_with_incorrect_line_format():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """00001,"Mock Create ST",4,"CREATE","Unexpected Data"
00002,"Mock Update ST",4,"UPDATE"
00003,"Mock Delete ST",4,"DELETE"""
    lines = handler.process_servicetypes_file(mock_csv_file, mock_event, 4 , summary_count_dict)
    assert lines == {"2": {"id": "00002", "name": "Mock Update ST", "nationalranking": "4","action": "UPDATE"},
                    "3": {"id": "00003", "name": "Mock Delete ST", "nationalranking": "4","action": "DELETE"}}


def test_process_file_raises_error_with_no_valid_length_lines():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """00001,"Mock Create ST",4, "CREATE","Unexpected Data"

00003,"Mock Delete ST",4,"UPDATE","EXTRA"""
    lines = handler.process_servicetypes_file(mock_csv_file, mock_event, 4 , summary_count_dict)
    assert lines == {}


# Possible duplicated test cases
def test_process_file_valid_length():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test one valid line of csv equals one row of extracted data"""
    csv_file = """2001,"Automated insert ServiceType",1,"CREATE"\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_valid_length_multiline():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test two valid lines of csv equals two rows of extracted data"""
    csv_file = """2001,"Automated insert ServiceType",1,"CREATE"\n2001,"Automated update ServiceType",1,"UPDATE"\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_empty_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line at end of file"""
    csv_file = """2001,"Automated insert ServiceType",1,"CREATE"\n\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_empty_first_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line at start of file"""
    csv_file = """\n2001,"Automated insert ServiceType",1,"CREATE"\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_three_lines_empty_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line in middle of file"""
    csv_file = """2001,"Automated insert ServiceType",1,"CREATE"\n\n\n2001,"Automated update ServiceType",1,"UPDATE"\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_incomplete_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores a line itf it is incomplete"""
    csv_file = """2001,"Automated insert ServiceType",1,"CREATE"\n2002,\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines)==1
    assert lines["1"]["id"] == "2001"


def test_process_file_incomplete_first_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ingores first line if it is incomplete"""
    csv_file = """2002,\n2001,"Automated insert ServiceType",1,"CREATE"\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines)==1
    assert lines["2"]["id"] == "2001"


def test_process_file_call_count():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction calls code to extract data from csv one per non empty line"""
    csv_file = """2001,"Automated insert ServiceType",1,"CREATE"\n2001,"Automated update ServiceType",1,"UPDATE"\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_call_count_inc_empty_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction calls code to extract data ignores empty line"""
    csv_file = """2001,"Automated insert ServiceType",1,"CREATE"\n\n2001,"Automated update ServiceType",1,"UPDATE"\n"""
    lines = handler.process_servicetypes_file(csv_file, mock_event, 4 , summary_count_dict)
    assert len(lines) == 2





def generate_event_payload():
    """Utility function to generate dummy event data"""
    return {"filename": mock_filename, "env": mock_env, "bucket": mock_bucket}
