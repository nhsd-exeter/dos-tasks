from application.utilities.common import check_csv_format, valid_action
from .. import common

csv_id = 2001
csv_desc = "Unit Test"

def test_check_csv():
    csv_line = "col1,col2,col3"
    assert check_csv_format(csv_line,3)

def test_check_csv():
    csv_line = "col1,col2,col3"
    assert not check_csv_format(csv_line,4)

def test_valid_create_action():
    """Test valid condition for create action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert valid_action(False,csv_dict)

def test_invalid_create_action():
    """Test invalid condition for create action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "CREATE"
    assert not valid_action(True,csv_dict)

def test_valid_update_action():
    """Test valid condition for update action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "UPDATE"
    assert valid_action(True,csv_dict)

def test_invalid_update_action():
    """Test invalid condition for update action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "UPDATE"
    assert not valid_action(False,csv_dict)

def test_valid_delete_action():
    """Test valid condition for delete action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert valid_action(True,csv_dict)

def test_invalid_delete_action():
    """Test invalid condition for delete action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "DELETE"
    assert not valid_action(False,csv_dict)

def test_invalid_action():
    """Test validation of unrecognized action"""
    csv_dict = {}
    csv_dict["id"] = csv_id
    csv_dict["action"] = "NOSUCH"
    assert not valid_action(True,csv_dict)
