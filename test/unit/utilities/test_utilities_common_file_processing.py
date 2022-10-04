from unittest.mock import Mock, patch
import psycopg2
import pytest
from .. import common_file_processing, common, message, logger

file_path = "application.utilities.common_file_processing"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
mock_context = ""
mock_env = "mock_env"
start = ""


csv_id1 = 2001
csv_id2 = 20001
csv_action = "DELETE"

def test_valid_create_action():
    """Test valid condition for create action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "CREATE"
    assert common_file_processing.ids_valid_action(False,csv_dict, 'test')

def test_invalid_create_action():
    """Test invalid condition for create action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "CREATE"
    assert not common_file_processing.ids_valid_action(True,csv_dict, 'test')

# def test_invalid_create_action():
#     """Test invalid condition for create action"""
#     csv_dict = {}
#     csv_dict["id1"] = csv_id
#     csv_dict["id2"] = csv_id
#     csv_dict["action"] = "INSERT"
#     assert not common_file_processing.ids_valid_action(False,csv_dict, 'test')

def test_valid_update_action():
    """Test valid condition for update action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "UPDATE"
    assert common_file_processing.ids_valid_action(True,csv_dict, 'test')

def test_invalid_update_action():
    """Test invalid condition for update action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "UPDATE"
    assert not common_file_processing.ids_valid_action(False,csv_dict, 'test')

def test_valid_delete_action():
    """Test valid condition for delete action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "DELETE"
    assert common_file_processing.ids_valid_action(True,csv_dict, 'test')

def test_invalid_delete_action():
    """Test invalid condition for delete action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "DELETE"
    assert not common_file_processing.ids_valid_action(False,csv_dict, 'test')

def test_inids_valid_action():
    """Test validation of unrecognized action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "NOSUCH"
    assert not common_file_processing.ids_valid_action(True,csv_dict, 'test')

def test_invalid_action_lower_case():
    """Test validation of lower case action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "delete"
    assert not common_file_processing.ids_valid_action(True,csv_dict, 'test')

def test_invalid_action_parameter():
    """Test validation of additional parameter that sets invalid action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "DELETE"
    assert not common_file_processing.ids_valid_action(True,csv_dict, 'test', "DELETE")

def test_invalid_action_parameter_lowercase():
    """Test validation of additional parameter that sets invalid action"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "delete"
    assert not common_file_processing.ids_valid_action(True,csv_dict, 'test', "delete")

def test_valid_create_action_parameter_set():
    """Test valid condition for create action with invalid action parameter set"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "CREATE"
    assert common_file_processing.ids_valid_action(False,csv_dict, 'test', "UPDATE")

def test_valid_delete_action_parameter_set():
    """Test valid condition for create action with invalid action parameter set"""
    csv_dict = {}
    csv_dict["id1"] = csv_id1
    csv_dict["id2"] = csv_id2
    csv_dict["action"] = "DELETE"
    assert common_file_processing.ids_valid_action(True,csv_dict, 'test', "UPDATE")

def test_check_for_not_null_values():
    """Checks key values not null"""
    csv_line = [2001,20002,"DELETE"]
    assert common_file_processing.check_ids_csv_values(csv_line,'env')

def test_check_for_null_id():
    """Checks if id1 is null/empty string"""
    csv_line = ["",20002,"DELETE"]
    assert not common_file_processing.check_ids_csv_values(csv_line,'env')

def test_check_for_null_name():
    """Checks is id2 is null/empty string"""
    csv_line = [2001,"","DELETE"]
    assert not common_file_processing.check_ids_csv_values(csv_line,'env')

def test_check_for_alpha_id():
    """Checks is id1 is not int"""
    csv_line = ["abc","","UPDATE"]
    assert not common_file_processing.check_ids_csv_values(csv_line,'env')


def test_process_file_success():
    summary_count_dict = {}
    summary_count_dict = {"BLANK": 0, "CREATE": 0,"DELETE": 0, "ERROR": 0,"UPDATE": 0}
    mock_csv_file = """00001,1234,"CREATE"
00002,2345,"CREATE"
00003,12345,"DELETE"""
    lines = common_file_processing.process_ids_file(mock_csv_file, mock_event, 3 , summary_count_dict)
    assert lines == {"1": {"id1": "00001", "id2": "1234", "action": "CREATE"},
                    "2": {"id1": "00002", "id2": "2345", "action": "CREATE"},
                    "3": {"id1": "00003", "id2": "12345", "action": "DELETE"}}


def test_process_file_success_with_empty_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """00001,1234,"CREATE"

00002,2345,"CREATE"
00003,12345,"DELETE"""
    lines = common_file_processing.process_ids_file(mock_csv_file, mock_event, 3, summary_count_dict)
    assert lines == {"1": {"id1": "00001", "id2": "1234", "action": "CREATE"},
                    "3": {"id1": "00002", "id2": "2345", "action": "CREATE"},
                    "4": {"id1": "00003", "id2": "12345", "action": "DELETE"}}


def test_process_file_success_with_incorrect_line_format():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """00001,1234,"CREATE", "EXTRA"
00002,2345,"CREATE"
00003,12345,"DELETE"""
    lines = common_file_processing.process_ids_file(mock_csv_file, mock_event, 3 , summary_count_dict)
    assert lines == {"2": {"id1": "00002", "id2": "2345", "action": "CREATE"},
                    "3": {"id1": "00003", "id2": "12345", "action": "DELETE"}}


def test_process_file_raises_error_with_no_valid_length_lines():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """00001,1234,"CREATE", "EXTRA"

00003,"DELETE"""
    lines = common_file_processing.process_ids_file(mock_csv_file, mock_event, 3 , summary_count_dict)
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
    csv_file = """2001,12334,"CREATE"\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_valid_length_multiline():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test two valid lines of csv equals two rows of extracted data"""
    csv_file = """2001,1234,"CREATE"\n2001,1234,"CREATE"\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_empty_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line at end of file"""
    csv_file = """2001,12345,"CREATE"\n\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_empty_first_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line at start of file"""
    csv_file = """\n2001,3456,"CREATE"\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_three_lines_empty_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line in middle of file"""
    csv_file = """2001,2345,"CREATE"\n\n\n2001,123,"UPDATE"\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_incomplete_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores a line itf it is incomplete"""
    csv_file = """2001,12345,"CREATE"\n123,\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines)==1
    assert lines["1"]["id1"] == "2001"


def test_process_file_incomplete_first_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ingores first line if it is incomplete"""
    csv_file = """2002,\n2001,1234,"CREATE"\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines)==1
    assert lines["2"]["id1"] == "2001"


def test_process_file_call_count():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction calls code to extract data from csv one per non empty line"""
    csv_file = """2001,123,"CREATE"\n2001,456,DELETE\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_call_count_inc_empty_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction calls code to extract data ignores empty line"""
    csv_file = """2001,1234,"CREATE"\n\n2001,12345,"DELETE"\n"""
    lines = common_file_processing.process_ids_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 2
