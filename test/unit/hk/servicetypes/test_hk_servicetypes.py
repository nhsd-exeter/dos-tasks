from unittest.mock import  patch
import psycopg2
import pytest
from .. import handler

file_path = "application.hk.servicetypes.handler"
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
csv_st_action = "INSERT"

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


def test_csv_line_lc():
    """Test lower case action in csv is converted to u/c"""
    csv_rows = {}
    csv_st_action = "remove"
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


def test_csv_line_exception():
    """Test exception handling by deliberately setting action to NOT a string"""
    csv_rows = {}
    csv_rows["1"]={"id": csv_st_id, "name": csv_st_name, "nationalranking": csv_st_rank, "action": 1}
    with pytest.raises(Exception):
        handler.extract_query_data_from_csv(csv_rows)


@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_file_from_bucket", return_value="csv_file")
@patch(f"{file_path}.common.process_file", return_value={})
@patch(f"{file_path}.process_extracted_data")
@patch(f"{file_path}.common.report_summary_counts", return_value="Symptom discriminators updated: 1, inserted: 1, deleted: 1")
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
        values (%s, %s, %s, %s, %s, %s, %s)
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
def test_process_extracted_data_error_check_exists_fails(mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict={csv_st_id,csv_st_name,csv_st_rank,"DELETE"}
    row_data[0]=csv_dict
    mock_db_connect = ""
    summary_count = {}
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data, summary_count)

@patch("psycopg2.connect")
@patch(f"{file_path}.database.does_record_exist", return_value=False)
@patch(f"{file_path}.common.increment_summary_count")
def test_process_extracted_data_error_check_exists_passes(mock_increment_count,mock_exists,mock_db_connect):
    """Test error handling when extracting data and record exist check passes"""
    row_data = {}
    csv_dict = {}
    csv_dict={csv_st_id,csv_st_name,csv_st_rank,"DELETE"}
    row_data[0]=csv_dict
    summary_count = {}
    mock_db_connect=""
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data, summary_count, mock_event)
    assert mock_exists.call_count == 1
    mock_increment_count.called_once()



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
