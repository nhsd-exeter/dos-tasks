from unittest.mock import Mock, patch
import psycopg2
import pytest
from .. import common, message, logger

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
    assert common.check_csv_format(csv_line,3, 'env',1)

def test_check_csv():
    csv_line = "col1,col2,col3"
    assert not common.check_csv_format(csv_line,4, 'env',1)

def test_valid_create_action():
    """Test valid condition for create action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert common.valid_action(False,csv_dict, 'test')

def test_invalid_create_action():
    """Test invalid condition for create action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert not common.valid_action(True,csv_dict, 'test')

def test_valid_update_action():
    """Test valid condition for update action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "UPDATE"
    assert common.valid_action(True,csv_dict, 'test')

def test_invalid_update_action():
    """Test invalid condition for update action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "UPDATE"
    assert not common.valid_action(False,csv_dict, 'test')

def test_valid_delete_action():
    """Test valid condition for delete action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert common.valid_action(True,csv_dict, 'test')

def test_invalid_delete_action():
    """Test invalid condition for delete action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert not common.valid_action(False,csv_dict, 'test')

def test_invalid_action():
    """Test validation of unrecognized action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "NOSUCH"
    assert not common.valid_action(True,csv_dict, 'test')

def test_invalid_action_lower_case():
    """Test validation of lower case action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "delete"
    assert not common.valid_action(True,csv_dict, 'test')

def test_invalid_action_parameter():
    """Test validation of additional parameter that sets invalid action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert not common.valid_action(True,csv_dict, 'test', "DELETE")

def test_invalid_action_parameter_lowercase():
    """Test validation of additional parameter that sets invalid action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "delete"
    assert not common.valid_action(True,csv_dict, 'test', "delete")

def test_valid_create_action_parameter_set():
    """Test valid condition for create action with invalid action parameter set"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert common.valid_action(False,csv_dict, 'test', "UPDATE")

def test_valid_delete_action_parameter_set():
    """Test valid condition for create action with invalid action parameter set"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert common.valid_action(True,csv_dict, 'test', "UPDATE")

@patch(f"{file_path}.utilities.s3.S3")
@patch(f"{file_path}.utilities.logger")
def test_archive_file_success(mock_logger,mock_s3_object):
    mock_s3_object().copy_object = Mock(return_value="Object copied")
    mock_s3_object().delete_object = Mock(return_value="Object deleted")
    mock_bucket = ""
    mock_filename = "local/DPTS-001_symptomdiscriminators.csv"
    result = common.archive_file(mock_bucket, mock_filename, mock_event, start)
    assert result == "File Archive Successful"



@patch(f"{file_path}.utilities.s3.S3")
def test_retrieve_file_from_bucket(mock_s3_object):
    mock_s3_object().get_object = Mock(return_value="Object returned")
    mock_bucket = ""
    mock_filename = ""
    result = common.retrieve_file_from_bucket(mock_bucket, mock_filename, mock_event, start)
    assert result == "Object returned"
    mock_s3_object().get_object.assert_called_once()

@patch(f"{file_path}.utilities.s3.S3")
def test_retrieve_compressed_file_from_bucket(mock_s3_object):
    mock_s3_object().get_compressed_object = Mock(return_value="Object returned")
    mock_bucket = ""
    mock_filename = ""
    result = common.retrieve_compressed_file_from_bucket(mock_bucket, mock_filename, mock_event, start)
    assert result == "Object returned"
    mock_s3_object().get_compressed_object.assert_called_once()



def test_check_for_not_null_values():
    """Checks key values not null"""
    csv_line = [2001,"Not null Id","UPDATE"]
    assert common.check_csv_values(csv_line,'env')

def test_check_for_null_id():
    """Checks if id is null/empty string"""
    csv_line = ["","Null Id","UPDATE"]
    assert not common.check_csv_values(csv_line,'env')

def test_check_for_null_name():
    """Checks is name/description is null/empty string"""
    csv_line = [2001,"","UPDATE"]
    assert not common.check_csv_values(csv_line,'env')

def test_check_for_alpha_id():
    """Checks is name/description is null/empty string"""
    csv_line = ["abc","","UPDATE"]
    assert not common.check_csv_values(csv_line,'env')

def test_uninitialized_summary_count():
    """Test summary counts uninitialized correctly"""
    summary_count = {}
    assert(len(summary_count) == 0)
    values = "UPDATE"
    with pytest.raises(KeyError):
        common.increment_summary_count(summary_count,values, 'test')

def test_initialise_summary_count():
    """Test summary counts initialized correctly"""
    summary_count = common.initialise_summary_count()
    assert(len(summary_count) == 5)
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0

def test_increment_summary_count_create():
    """Test only create count incremented for create action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0
    values = "CREATE"
    common.increment_summary_count(summary_count,values, 'test')
    assert summary_count[common.create_action] == 1
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0

def test_increment_summary_count_update():
    """Test only update count incremented for update action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0
    values = "UPDATE"
    common.increment_summary_count(summary_count,values, 'test')
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 1
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0

def test_increment_summary_count_delete():
    """Test only delete count incremented for delete action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0
    values = "DELETE"
    common.increment_summary_count(summary_count, values, 'test')
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 1
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0

def test_increment_summary_count_blank():
    """Test only delete count incremented for blank action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0
    values = "BLANK"
    common.increment_summary_count(summary_count, values, 'test')
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == 0
    assert summary_count[common.error_lines] == 0

def test_increment_summary_count_error():
    """Test only delete count incremented for error action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0
    values = "ERROR"
    common.increment_summary_count(summary_count, values, 'test')
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 1

def test_increment_summary_count_nosuch():
    """Test NO count incremented for invalid action """
    summary_count = common.initialise_summary_count()
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0
    values = "NOSUCH"
    common.increment_summary_count(summary_count, values, 'test')
    assert summary_count[common.create_action] == 0
    assert summary_count[common.update_action] == 0
    assert summary_count[common.delete_action] == 0
    assert summary_count[common.blank_lines] == -1
    assert summary_count[common.error_lines] == 0




def test_process_file_success():
    summary_count_dict = {}
    summary_count_dict = {"BLANK": 0, "CREATE": 0,"DELETE": 0, "ERROR": 0,"UPDATE": 0}
    mock_csv_file = """00001,"Mock Create SD","CREATE"
00002,"Mock Update SD","UPDATE"
00003,"Mock Delete SD","DELETE"""
    lines = common.process_file(mock_csv_file, mock_event, 3 , summary_count_dict)
    assert lines == {"1": {"id": "00001", "name": "Mock Create SD", "action": "CREATE"},
                    "2": {"id": "00002", "name": "Mock Update SD", "action": "UPDATE"},
                    "3": {"id": "00003", "name": "Mock Delete SD", "action": "DELETE"}}


def test_process_file_success_with_empty_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """
00001,"Mock Create SD","CREATE"

00002,"Mock Update SD","UPDATE"
00003,"Mock Delete SD","DELETE"
"""
    lines = common.process_file(mock_csv_file, mock_event, 3, summary_count_dict)
    assert lines == {"2": {"id": "00001", "name": "Mock Create SD", "action": "CREATE"},
                    "4": {"id": "00002", "name": "Mock Update SD", "action": "UPDATE"},
                    "5": {"id": "00003", "name": "Mock Delete SD", "action": "DELETE"}}


def test_process_file_success_with_incorrect_line_format():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """00001,"Mock Create SD","CREATE","Unexpected Data"
00002,"Mock Update SD","UPDATE"
00003,"Mock Delete SD","DELETE"""
    lines = common.process_file(mock_csv_file, mock_event, 3 , summary_count_dict)
    assert lines == {"2": {"id": "00002", "name": "Mock Update SD", "action": "UPDATE"},
                    "3": {"id": "00003", "name": "Mock Delete SD", "action": "DELETE"}}


def test_process_file_raises_error_with_no_valid_length_lines():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    mock_csv_file = """00001,"Mock Create SD","CREATE","Unexpected Data"

00003,"Mock Delete SD","UPDATE","EXTRA"""
    lines = common.process_file(mock_csv_file, mock_event, 3 , summary_count_dict)
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
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_valid_length_multiline():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test two valid lines of csv equals two rows of extracted data"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_empty_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line at end of file"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_empty_first_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line at start of file"""
    csv_file = """\n2001,"Automated insert SymptomGroup","CREATE"\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 1


def test_process_file_three_lines_empty_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores any empty line in middle of file"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_incomplete_second_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction ignores a line itf it is incomplete"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2002,\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
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
    csv_file = """2002,\n2001,"Automated insert SymptomGroup","CREATE"\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
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
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 2


def test_process_file_call_count_inc_empty_line():
    summary_count_dict = {}
    summary_count_dict["CREATE"] = 0
    summary_count_dict["UPDATE"] = 0
    summary_count_dict["DELETE"] = 0
    summary_count_dict["BLANK"] = 0
    summary_count_dict["ERROR"] = 0
    """Test data extraction calls code to extract data ignores empty line"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    lines = common.process_file(csv_file, mock_event, 3 , summary_count_dict)
    assert len(lines) == 2


def test_slack_summary_count():
    """Test slack report log output of summary count """
    summary_count = {}
    summary_count={"BLANK": 3, "CREATE": 2,"DELETE": 8, "ERROR": 1,"UPDATE": 4}
    report=common.slack_summary_counts(summary_count)
    assert report ==  "updated:4, inserted:2, deleted:8, blank:3, errored:1"

def test_slack_summary_count_blank_lines_negative():
    """Test slack report log output of summary count """
    summary_count = {}
    summary_count={"blank": -1, "create": 2,"delete": 8, "error": 1,"update": 4}
    report=common.slack_summary_counts(summary_count)
    assert report ==  "blank:0, create:2, delete:8, error:1, update:4"

def test_slack_summary_count():
    """Test slack report log output of null summary count """
    report=common.slack_summary_counts(None)
    assert report ==  ""
