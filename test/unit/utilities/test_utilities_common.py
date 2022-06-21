from unittest.mock import Mock, patch
import psycopg2
import pytest
# from application.utilities.common import check_csv_format, valid_action, cleanup, retrieve_file_from_bucket, connect_to_database
from .. import common, message

file_path = "application.utilities.common"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
start = ""


csv_id = 2001
csv_desc = "Unit Test"
csv_action = "DELETE"



def test_check_csv():
    csv_line = "col1,col2,col3"
    assert common.check_csv_format(csv_line,3)

def test_check_csv():
    csv_line = "col1,col2,col3"
    assert not common.check_csv_format(csv_line,4)

def test_valid_create_action():
    """Test valid condition for create action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert common.valid_action(False,csv_dict)

def test_invalid_create_action():
    """Test invalid condition for create action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert not common.valid_action(True,csv_dict)

def test_valid_update_action():
    """Test valid condition for update action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "UPDATE"
    assert common.valid_action(True,csv_dict)

def test_invalid_update_action():
    """Test invalid condition for update action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "UPDATE"
    assert not common.valid_action(False,csv_dict)

def test_valid_delete_action():
    """Test valid condition for delete action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert common.valid_action(True,csv_dict)

def test_invalid_delete_action():
    """Test invalid condition for delete action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert not common.valid_action(False,csv_dict)

def test_invalid_action():
    """Test validation of unrecognized action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "NOSUCH"
    assert not common.valid_action(True,csv_dict)

def test_invalid_action_lower_case():
    """Test validation of lower case action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "delete"
    assert not common.valid_action(True,csv_dict)

@patch("psycopg2.connect")
@patch(f"{file_path}.S3")
@patch(f"{file_path}.send_success_slack_message")
def test_cleanup_success(mock_send_success_slack_message, mock_s3_object, mock_db_connect):
    mock_db_connect.close.return_value = "Closed connection"
    mock_s3_object().copy_object = Mock(return_value="Object copied")
    mock_s3_object().delete_object = Mock(return_value="Object deleted")
    mock_bucket = ""
    mock_filename = "local/DPTS-001_symptomdiscriminators.csv"
    result = common.cleanup(mock_db_connect, mock_bucket, mock_filename, mock_event, start)
    assert result == "Cleanup Successful"
    mock_db_connect.close.assert_called_once()
    mock_s3_object().copy_object.assert_called_once_with(mock_bucket, mock_filename, mock_event, start)
    mock_s3_object().delete_object.assert_called_once_with(mock_bucket, mock_filename, mock_event, start)
    mock_send_success_slack_message.assert_called_once_with(mock_event, start)

# TODO moved to database test
# @patch(f"{file_path}.send_failure_slack_message")
# @patch(f"{file_path}.DB")
# def test_connect_to_database_returns_error(mock_db_object, mock_send_failure_slack_message):
#     mock_db_object().db_set_connection_details = Mock(return_value=False)
#     with pytest.raises(ValueError) as assertion:
#         result = common.connect_to_database(mock_env, mock_event, start)
#     assert str(assertion.value) == "DB Parameter(s) not found in secrets store"
#     mock_db_object().db_set_connection_details.assert_called_once()
#     mock_send_failure_slack_message.assert_called_once()


@patch(f"{file_path}.S3")
def test_retrieve_file_from_bucket(mock_s3_object):
    mock_s3_object().get_object = Mock(return_value="Object returned")
    mock_bucket = ""
    mock_filename = ""
    result = common.retrieve_file_from_bucket(mock_bucket, mock_filename, mock_event, start)
    assert result == "Object returned"
    mock_s3_object().get_object.assert_called_once()

#  Moved to database test
# @patch(f"{file_path}.DB")
# def test_connect_to_database_success(mock_db_object):
#     mock_db_object().db_set_connection_details = Mock(return_value=True)
#     mock_db_object().db_connect = Mock(return_value="Connection Established")
#     result = common.connect_to_database(mock_env, mock_event, start)
#     assert result == "Connection Established"
#     mock_db_object().db_set_connection_details.assert_called_once()
#     mock_db_object().db_connect.assert_called_once()

def test_check_for_not_null_values():
    """Checks key values not null"""
    csv_line = [2001,"Not null Id","UPDATE"]
    assert common.check_csv_values(csv_line)

def test_check_for_null_id():
    """Checks if id is null/empty string"""
    csv_line = ["","Null Id","UPDATE"]
    assert not common.check_csv_values(csv_line)

def test_check_for_null_name():
    """Checks is name/description is null/empty string"""
    csv_line = [2001,"","UPDATE"]
    assert not common.check_csv_values(csv_line)

def test_check_for_alpha_id():
    """Checks is name/description is null/empty string"""
    csv_line = ["abc","","UPDATE"]
    assert not common.check_csv_values(csv_line)


# @patch("psycopg2.connect")
# def test_record_exists_true(mock_db_connect):
#     """Test correct data passed to check record exists - returning true"""
#     csv_dict = {}
#     csv_dict["id"] = csv_id
#     csv_dict["name"] = csv_desc
#     csv_dict["action"] = csv_action
#     csv_dict["zcode"] = None
#     mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
#     assert common.does_record_exist(mock_db_connect,csv_dict,table_name)

# @patch("psycopg2.connect")
# def test_does_record_exist_false(mock_db_connect):
#     """Test correct data passed to check record exists - returning false"""
#     csv_dict = {}
#     csv_dict["id"] = csv_id
#     csv_dict["name"] = csv_desc
#     csv_dict["action"] = "DELETE"
#     csv_dict["zcode"] = None
#     mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
#     assert not common.does_record_exist(mock_db_connect,csv_dict,table_name)

# @patch("psycopg2.connect")
# def test_does_record_exist_exception(mock_db_connect):
#     """Test throwing of exception """
#     csv_dict = {}
#     csv_dict["id"] = csv_id
#     csv_dict["name"] = csv_desc
#     csv_dict["action"] = csv_action
#     csv_dict["zcode"] = None
#     mock_db_connect = ""
#     with pytest.raises(Exception):
#         common.does_record_exist(mock_db_connect,csv_dict,table_name)


def test_initialise_summary_count():
    """Test summary counts initialised correctly"""
    summary_count = common.initialise_summary_count()
    assert(len(summary_count) == 3)
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0

def test_increment_summary_count_create():
    """Test only create count incremented for create action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    values = {"action":"CREATE"}
    common.increment_summary_count(summary_count,values)
    assert summary_count[common.create_action] == 1
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0

def test_increment_summary_count_update():
    """Test only update count incremented for update action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    values = {"action":"UPDATE"}
    common.increment_summary_count(summary_count,values)
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 1
    assert summary_count[common.delete_action] == 0

def test_increment_summary_count_delete():
    """Test only delete count incremented for delete action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    values = {"action":"DELETE"}
    common.increment_summary_count(summary_count, values)
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 1

def test_increment_summary_count_nosuch():
    """Test NO count incremented for invalid action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    values = {"action":"NOSUCH"}
    common.increment_summary_count(summary_count, values)
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0

def test_process_file_success():
    mock_csv_file = """00001,"Mock Create SD","CREATE"
00002,"Mock Update SD","UPDATE"
00003,"Mock Delete SD","DELETE"""
    lines = common.process_file(mock_csv_file, mock_event, start, 3)
    assert lines == {"1": {"id": "00001", "description": "Mock Create SD", "action": "CREATE"},
                    "2": {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"},
                    "3": {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}}


def test_process_file_success_with_empty_line():
    mock_csv_file = """
00001,"Mock Create SD","CREATE"

00002,"Mock Update SD","UPDATE"
00003,"Mock Delete SD","DELETE"
"""
    lines = common.process_file(mock_csv_file, mock_event, start, 3)
    assert lines == {"2": {"id": "00001", "description": "Mock Create SD", "action": "CREATE"},
                    "4": {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"},
                    "5": {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}}


# @patch(f"{file_path}.message.send_failure_slack_message")
def test_process_file_success_with_incorrect_line_format():
    mock_csv_file = """00001,"Mock Create SD","CREATE","Unexpected Data"
00002,"Mock Update SD","UPDATE"
00003,"Mock Delete SD","DELETE"""
    lines = common.process_file(mock_csv_file, mock_event, start, 3)
    assert lines == {"2": {"id": "00002", "description": "Mock Update SD", "action": "UPDATE"},
                    "3": {"id": "00003", "description": "Mock Delete SD", "action": "DELETE"}}


@patch(f"{file_path}.send_failure_slack_message")
def test_process_file_raises_error_with_no_valid_length_lines(mock_send_failure_slack_message):
    mock_csv_file = """00001,"Mock Create SD","CREATE","Unexpected Data"

00003,"Mock Delete SD","UPDATE","EXTRA"""
    lines = common.process_file(mock_csv_file, mock_event, start, 3)
    assert lines == {}
    mock_send_failure_slack_message.assert_called_once()

# Possible duplicated test cases
def test_process_file_valid_length():
    """Test one valid line of csv equals one row of extracted data"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines) == 1

def test_process_file_valid_length_multiline():
    """Test two valid lines of csv equals two rows of extracted data"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines) == 2

def test_process_file_empty_second_line():
    """Test data extraction ignores any empty line at end of file"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines) == 1

def test_process_file_empty_first_line():
    """Test data extraction ignores any empty line at start of file"""
    csv_file = """\n2001,"Automated insert SymptomGroup","CREATE"\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines) == 1

def test_process_file_three_lines_empty_second_line():
    """Test data extraction ignores any empty line in middle of file"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines) == 2

def test_process_file_incomplete_second_line():
    """Test data extraction ignores a line itf it is incomplete"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2002,\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines)==1
    assert lines["1"]["id"] == "2001"

def test_process_file_incomplete_first_line():
    """Test data extraction ingores first line if it is incomplete"""
    csv_file = """2002,\n2001,"Automated insert SymptomGroup","CREATE"\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines)==1
    assert lines["2"]["id"] == "2001"

def test_process_file_call_count():
    """Test data extraction calls code to extract data from csv one per non empty line"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines) == 2

def test_process_file_call_count_inc_empty_line():
    """Test data extraction calls code to extract data ignores empty line"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    lines = common.process_file(csv_file, mock_event, start, 3)
    assert len(lines) == 2
