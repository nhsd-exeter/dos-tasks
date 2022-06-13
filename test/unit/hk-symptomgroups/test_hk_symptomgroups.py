import pytest
from moto import mock_s3
import mock
import sys
import json
import string
import psycopg2
from datetime import datetime

# sys.path.append(".")
from .. import handler
from utilities import database, message, s3, secrets

file_path = "application.hk.symptomgroups.handler"

filename = "test/sg.csv"

db_secrets = '{"DB_HOST": "localhost","DB_NAME": "pathwaysdos_dev","DB_USER": "postgres","DB_USER_PASSWORD": "postgres"}'

secret_name = "placeholder-secret"
bucket = "NoSuchBucket"
env = "unittest"

# example 2001,"Symptom group description","DELETE"
csv_sg_id = 2001
csv_sg_desc = "Automated Test"
csv_sg_action = "REMOVE"

def test_csv_line():
    """Test data extracted from valid csv"""
    csv_row = [str(csv_sg_id), csv_sg_desc, csv_sg_action]
    csv_dict = handler.extract_query_data_from_csv(csv_row)
    assert len(csv_dict) == 4
    assert str(csv_dict["csv_sgid"]) == str(csv_sg_id)
    assert csv_dict["csv_name"] == str(csv_sg_desc)
    assert csv_dict["action"] == str(csv_sg_action).upper()
    assert csv_dict["csv_zcode"] is False


def test_csv_line_lc():
    """Test lower case action in csv is converted to u/c"""
    csv_sg_action = "remove"
    csv_row = [str(csv_sg_id), csv_sg_desc, csv_sg_action]
    csv_dict = handler.extract_query_data_from_csv(csv_row)
    assert len(csv_dict) == 4
    assert str(csv_dict["csv_sgid"]) == str(csv_sg_id)
    assert csv_dict["csv_name"] == str(csv_sg_desc)
    assert csv_dict["action"] == str(csv_sg_action).upper()
    assert csv_dict["csv_zcode"] is False


def test_invalid_csv_line():
    """Test invalid csv results in no data extracted"""
    csv_row = [str(csv_sg_id), csv_sg_desc]
    csv_dict = handler.extract_query_data_from_csv(csv_row)
    assert len(csv_dict) == 0


def test_no_sgid_csv_line():
    """Test no id in csv extract sets id to None"""
    csv_row = ["", csv_sg_desc, csv_sg_action]
    csv_dict = handler.extract_query_data_from_csv(csv_row)
    assert len(csv_dict) == 4
    assert str(csv_dict["csv_sgid"]) == "None"


def test_no_sgdesc_csv_line():
    """Test if no name in csv extract sets name to None and zcode to False"""
    csv_row = [str(csv_sg_id), "", csv_sg_action]
    csv_dict = handler.extract_query_data_from_csv(csv_row)
    assert len(csv_dict) == 4
    assert str(csv_dict["csv_name"]) == "None"
    assert csv_dict["csv_zcode"] is False


def test_zcode_sgdesc_csv_line():
    """Test extract correctly recognises zcodes"""
    csv_row = [str(csv_sg_id), "z2.0 - test", csv_sg_action]
    csv_dict = handler.extract_query_data_from_csv(csv_row)
    assert len(csv_dict) == 4
    assert csv_dict["csv_zcode"] is True


def test_csv_line_exception():
    """Test exception handling by deliberately setting action to NOT a string"""
    csv_row = [str(csv_sg_id), csv_sg_desc, 1]
    with pytest.raises(Exception):
        handler.extract_query_data_from_csv(csv_row)

def test_valid_create_action():
    """Test valid condition for create action"""
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "CREATE"
    assert handler.valid_action(False,csv_dict)

def test_invalid_create_action():
    """Test invalid condition for create action"""
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "CREATE"
    assert not handler.valid_action(True,csv_dict)

def test_valid_update_action():
    """Test valid condition for update action"""
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "UPDATE"
    assert handler.valid_action(True,csv_dict)

def test_invalid_update_action():
    """Test invalid condition for update action"""
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "UPDATE"
    assert not handler.valid_action(False,csv_dict)

def test_valid_delete_action():
    """Test valid condition for delete action"""
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "DELETE"
    assert handler.valid_action(True,csv_dict)

def test_invalid_delete_action():
    """Test invalid condition for delete action"""
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "DELETE"
    assert not handler.valid_action(False,csv_dict)

def test_invalid_action():
    """Test validation of unrecognized action"""
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "NOSUCH"
    assert not handler.valid_action(True,csv_dict)

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
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "CREATE"
    query, data = handler.generate_db_query(csv_dict)
    mapping = {ord(c): None for c in remove}
    assert query.translate(mapping) == create_query_string.translate(mapping),"Query syntax mismatched"
    assert data[0] == csv_dict["csv_sgid"]
    assert data[1] == csv_dict["csv_name"]

def test_generating_update_query():
    """Test creation of update query and data arguments"""
    update_query_string = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
        where id = (%s);"""
    remove = string.punctuation + string.whitespace

    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "UPDATE"
    query, data = handler.generate_db_query(csv_dict)
    mapping = {ord(c): None for c in remove}
    assert query.translate(mapping) == update_query_string.translate(mapping),"Query syntax mismatched"
    assert data[0] == csv_dict["csv_name"]
    assert data[1] == csv_dict["csv_zcode"]
    assert data[2] == csv_dict["csv_sgid"]

def test_generating_delete_query():
    """Test creation of delete query and data argument"""
    delete_query_string = """delete from pathwaysdos.symptomgroups where id = (%s)"""
    remove = string.punctuation + string.whitespace
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "DELETE"
    query, data = handler.generate_db_query(csv_dict)
    mapping = {ord(c): None for c in remove}
    assert query.translate(mapping) == delete_query_string.translate(mapping),"Query syntax mismatched"
    assert data[0] == csv_dict["csv_sgid"]

def test_generating_query_with_invalid_action():
    """Test creation of query and data arguments for unrecognized action"""
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "REMOVE"
    with pytest.raises(psycopg2.DatabaseError):
        query, data = handler.generate_db_query(csv_dict)

@mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
@mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = False)
def test_db_connect_fails_to_set_connection_details(mock_db,mock_send_failure_slack_message):
    """Test if db connection details fails"""
    start = datetime.utcnow()
    payload = generate_event_payload()
    with pytest.raises(ValueError, match='One or more DB Parameters not found in secrets store'):
        handler.connect_to_database("unittest",payload,start)
    mock_db.assert_called_once()
    mock_send_failure_slack_message.assert_called_once()

@mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
@mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = True)
def test_db_connect_fail(mock_db,mock_send_failure_slack_message):
    """Test if db connection details set but attempt to connect fails"""
    start = datetime.utcnow()
    payload = generate_event_payload()
    with pytest.raises(psycopg2.InterfaceError):
        handler.connect_to_database("unittest",payload,start)
    mock_send_failure_slack_message.assert_called_once()

@mock.patch(f"{file_path}.database.DB.db_connect", return_value = "db_connection")
@mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = "True")
def test_db_connect_succeeds(mock_db,mock_connection):
    """Test handler code to connect to db where connection succeeds """
    start = datetime.utcnow()
    payload = generate_event_payload()
    handler.connect_to_database("unittest",payload,start)
    assert mock_connection.call_count == 1

def test_extract_data_from_file_valid_length():
    """Test one valid line of csv equals one row of extracted data"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n"""
    start = datetime.utcnow()
    event = generate_event_payload()
    lines = handler.extract_data_from_file(csv_file, event, start)
    assert len(lines) == 1

# @mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
def test_extract_data_from_file_valid_length_multiline():
    """Test two valid lines of csv equals two rows of extracted data"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    start = datetime.utcnow()
    event = generate_event_payload()
    lines = handler.extract_data_from_file(csv_file, event, start)
    assert len(lines) == 2

# @mock.patch(f"{file_path}.message.send_start_message", return_value = None)
def test_extract_data_from_file_empty_second_line():
    """Test data extraction ignores any empty line at end of file"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n"""
    start = datetime.utcnow()
    event = generate_event_payload()
    lines = handler.extract_data_from_file(csv_file, event, start)
    assert len(lines) == 1

def test_extract_data_from_file_empty_first_line():
    """Test data extraction ignores any empty line at start of file"""
    csv_file = """\n2001,"Automated insert SymptomGroup","CREATE"\n"""
    start = datetime.utcnow()
    event = generate_event_payload()
    lines = handler.extract_data_from_file(csv_file, event, start)
    assert len(lines) == 1

@mock.patch(f"{file_path}.extract_query_data_from_csv", return_value={"csv_sgid": "2001", "csv_name": "Automated insert SymptomGroup","csv_zcode":"None", "action": "CREATE"})
def test_extract_data_from_file_three_lines_empty_second_line(mock_extract):
    """Test data extraction ignores any empty line in middle of file"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    start = datetime.utcnow()
    event = generate_event_payload()
    lines = handler.extract_data_from_file(csv_file, event, start)
    assert len(lines) == 2
    assert mock_extract.call_count == 2

@mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
def test_extract_data_from_file_incomplete_second_line(mock_message):
    """Test data extraction raises error if any line is incomplete or invalid"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2002,\n"""
    start = datetime.utcnow()
    event = generate_event_payload()
    with pytest.raises(IndexError, match="Unexpected data in csv file"):
        handler.extract_data_from_file(csv_file, event, start)

@mock.patch(f"{file_path}.extract_query_data_from_csv", return_value={"csv_sgid": "2001", "csv_name": "Automated insert SymptomGroup","csv_zcode":"None", "action": "CREATE"})
def test_extract_data_from_file_call_count(mock_extract):
    """Test data extraction calls code to extract data from csv one per non empty line"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    start = datetime.utcnow()
    event = generate_event_payload()
    lines = handler.extract_data_from_file(csv_file, event, start)
    assert len(lines) == 2
    assert mock_extract.call_count == len(lines)

@mock.patch(f"{file_path}.extract_query_data_from_csv", return_value={"csv_sgid": "2001", "csv_name": "Automated insert SymptomGroup","csv_zcode":"None", "action": "CREATE"})
def test_extract_data_from_file_call_count_inc_empty_line(mock_extract):
    """Test data extraction calls code to extract data ignores empty line"""
    csv_file = """2001,"Automated insert SymptomGroup","CREATE"\n\n2001,"Automated update SymptomGroup","UPDATE"\n"""
    start = datetime.utcnow()
    event = generate_event_payload()
    lines = handler.extract_data_from_file(csv_file, event, start)
    assert len(lines) == 2
    assert mock_extract.call_count == len(lines)

@mock.patch("psycopg2.connect")
def test_execute_db_query_success(mock_db_connect):
    """Test code to execute query successfully"""
    line = """2001,"New Symptom Group","CREATE"\n"""
    data = ("New Symptom Group", "None", 2001)
    values = {}
    values["action"] = "CREATE"
    values['id'] = 2001
    values['name'] = "New Symptom Group"
    mock_db_connect.cursor.return_value.__enter__.return_value = "Success"
    query = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
        where id = (%s);"""
    #
    handler.initialise_summary_count()
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0
    handler.execute_db_query(mock_db_connect, query, data, line, values)
    mock_db_connect.commit.assert_called_once()
    mock_db_connect.cursor().close.assert_called_once()
    assert handler.summary_count_dict[handler.create_action] == 1
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0

@mock.patch("psycopg2.connect")
def test_execute_db_query_failure(mock_db_connect):
    """Test code to handle exception and rollback when executing query"""
    line = """2001,"New Symptom Group","CREATE"\n"""
    data = ("New Symptom Group", "None", 2001)
    values = {"action":"CREATE","id":2001,"Name":"New Symptom Group"}
    mock_db_connect.cursor.return_value.__enter__.return_value = Exception
    query = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
        where id = (%s);"""
    handler.execute_db_query(mock_db_connect, query, data, line, values)
    mock_db_connect.rollback.assert_called_once()
    mock_db_connect.cursor().close.assert_called_once()

@mock.patch("psycopg2.connect")
@mock.patch(f"{file_path}.execute_db_query")
@mock.patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@mock.patch(f"{file_path}.valid_action", return_value=True)
@mock.patch(f"{file_path}.does_record_exist", return_value=True)
def test_process_extracted_data_single_record(mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for one record"""
    row_data = {}
    csv_dict={}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "DELETE"
    row_data[0]=csv_dict
    handler.process_extracted_data(mock_db_connect, row_data)
    mock_valid_action.assert_called_once()
    mock_exist.assert_called_once()
    mock_generate.assert_called_once()
    mock_execute.assert_called_once()

@mock.patch("psycopg2.connect")
@mock.patch(f"{file_path}.execute_db_query")
@mock.patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
@mock.patch(f"{file_path}.valid_action", return_value=True)
@mock.patch(f"{file_path}.does_record_exist", return_value=True)
def test_process_extracted_data_multiple_records(mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
    """Test extracting data calls each downstream functions once for each record"""
    row_data = {}
    csv_dict={}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "DELETE"
    row_data[0]=csv_dict
    row_data[1]=csv_dict
    handler.process_extracted_data(mock_db_connect, row_data)
    assert mock_valid_action.call_count == 2
    assert mock_exist.call_count == 2
    assert mock_generate.call_count == 2
    assert mock_execute.call_count == 2

@mock.patch("psycopg2.connect")
def test_process_extracted_data_error_check_exists_fails(mock_db_connect):
    """Test error handling when extracting data and record exist check fails"""
    row_data = {}
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "DELETE"
    row_data[0]=csv_dict
    mock_db_connect = ""
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data)

@mock.patch("psycopg2.connect")
@mock.patch(f"{file_path}.does_record_exist", return_value=True)
def test_process_extracted_data_error_check_exists_passes(mock_exists,mock_db_connect):
    """Test error handling when extracting data and record exist check passes"""
    row_data = {}
    csv_dict = {}
    csv_dict["csv_sgid"] = csv_sg_id
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["csv_zcode"] = False
    csv_dict["action"] = "DELETE"
    row_data[0]=csv_dict
    mock_db_connect = ""
    with pytest.raises(Exception):
        handler.process_extracted_data(mock_db_connect, row_data)
    assert mock_exists.call_count == 1

@mock.patch(f"{file_path}.s3.S3.get_object", return_value = None)
def test_get_csv_from_s3(mock_s3):
    """Test handle of error retrieving file from s3 bucket"""
    start = datetime.utcnow()
    event = generate_event_payload()
    csv_file = handler.retrieve_file_from_bucket(bucket, filename,event,start)
    assert csv_file == None

@mock.patch("psycopg2.connect")
def test_record_exists_true(mock_db_connect):
    """Test correct data passed to check record exists - returning true"""
    csv_dict = {}
    csv_dict["csv_sgid"] = str(csv_sg_id)
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["action"] = "DELETE"
    csv_dict["csv_zcode"] = None
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
    assert handler.does_record_exist(mock_db_connect,csv_dict)

@mock.patch("psycopg2.connect")
def test_does_record_exist_false(mock_db_connect):
    """Test correct data passed to check record exists - returning false"""
    csv_dict = {}
    csv_dict["csv_sgid"] = str(csv_sg_id)
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["action"] = "DELETE"
    csv_dict["csv_zcode"] = None
    mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
    assert not handler.does_record_exist(mock_db_connect,csv_dict)

@mock.patch("psycopg2.connect")
def test_does_record_exist_exception(mock_db_connect):
    """Test throwing of exception """
    csv_dict = {}
    csv_dict["csv_sgid"] = str(csv_sg_id)
    csv_dict["csv_name"] = csv_sg_desc
    csv_dict["action"] = "DELETE"
    csv_dict["csv_zcode"] = None
    mock_db_connect = ""
    with pytest.raises(Exception):
        handler.does_record_exist(mock_db_connect,csv_dict)

@mock.patch(f"{file_path}.message.send_success_slack_message", return_value = None)
@mock.patch(f"{file_path}.s3.S3.delete_object", return_value = None)
@mock.patch(f"{file_path}.s3.S3.copy_object", return_value = None)
@mock.patch("psycopg2.connect")
def test_cleanup(mock_db_connect,mock_s3_copy,mock_s3_delete,mock_message):
    """Test handler's successful clean up function calls downstream functions"""
    start = datetime.utcnow()
    event = generate_event_payload()
    handler.cleanup(mock_db_connect, bucket, filename, event, start)
    mock_s3_copy.assert_called_once()
    mock_s3_delete.assert_called_once()
    mock_message.assert_called_once()
    mock_db_connect.close.assert_called_once()

@mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = True)
@mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
@mock.patch(f"{file_path}.message.send_start_message", return_value = None)
@mock.patch(f"{file_path}.s3.S3.get_object", return_value = None)
def test_handler_exception(mock_db,mock_failure_message,mock_message_start,mock_s3):
    """Test clean up function handling exceptions from downstream functions"""
    payload = generate_event_payload()
    with pytest.raises(Exception):
        with mock.patch(secrets.__name__ + '.SECRETS.get_secret_value', return_value = json.dumps(db_secrets)):
            handler.request(event=payload, context=None)

@mock.patch("psycopg2.connect")
@mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
@mock.patch(f"{file_path}.message.send_success_slack_message", return_value = None)
@mock.patch(f"{file_path}.s3.S3.delete_object", return_value = None)
@mock.patch(f"{file_path}.s3.S3.copy_object", return_value = None)
@mock.patch(f"{file_path}.execute_db_query")
@mock.patch(f"{file_path}.does_record_exist", return_value=True)
@mock.patch(f"{file_path}.s3.S3.get_object", return_value="""2001,"New Symptom Group","UPDATE"\n""")
@mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = True)
@mock.patch(f"{file_path}.message.send_start_message")
def test_handler_pass(mock_send_start_message,mock_db_details,mock_get_object,
mock_does_record_exist,mock_execute_db_query,mock_copy_object,mock_delete_object,mock_send_success_slack_message,mock_send_failure_slack_message,mock_db_connect):
    """Test top level request calls downstream functions - success"""
    payload = generate_event_payload()
    with mock.patch(secrets.__name__ + '.SECRETS.get_secret_value', return_value = 'SecretString=' + json.dumps(db_secrets)):
        handler.request(event=payload, context=None)
        mock_send_start_message.assert_called_once()
        mock_get_object.assert_called_once()
        mock_copy_object.assert_called_once()
        mock_delete_object.assert_called_once()
        mock_send_success_slack_message.assert_called_once()
        mock_does_record_exist.assert_called_once()
        mock_execute_db_query.assert_called_once
        mock_send_failure_slack_message.assert_not_called()

@mock.patch("psycopg2.connect")
@mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
@mock.patch(f"{file_path}.message.send_success_slack_message", return_value = None)
@mock.patch(f"{file_path}.s3.S3.delete_object", return_value = None)
@mock.patch(f"{file_path}.s3.S3.copy_object", return_value = None)
@mock.patch(f"{file_path}.does_record_exist", return_value=False)
@mock.patch(f"{file_path}.s3.S3.get_object", return_value="""2001,"New Symptom Group","UPDATE"\n""")
@mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = True)
@mock.patch(f"{file_path}.message.send_start_message")
def test_handler_fail(mock_send_start_message,mock_db_details,mock_get_object,
mock_does_record_exist,mock_copy_object,mock_delete_object,mock_send_failure_slack_message,mock_send_success_slack_message,mock_db_connect):
    """Test top level function handles errors thrown by downstream functions"""
    payload = generate_event_payload()
    with mock.patch(secrets.__name__ + '.SECRETS.get_secret_value', return_value = 'SecretString=' + json.dumps(db_secrets)):
        handler.request(event=payload, context=None)
        assert mock_send_start_message.call_count == 1
        mock_get_object.assert_called_once()
        mock_send_failure_slack_message.assert_called_once()
        mock_copy_object.assert_called_once()
        mock_delete_object.assert_called_once()
        mock_send_success_slack_message.assert_not_called()
        mock_does_record_exist.assert_called_once()

def test_initialise_summary_count():
    """Test summary counts initialised correctly"""
    handler.initialise_summary_count()
    assert(len(handler.summary_count_dict) == 3)
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0

def test_increment_summary_count_create():
    """Test only create count incremented for create action """
    handler.initialise_summary_count()
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0
    values = {"action":"CREATE"}
    handler.increment_summary_count(values)
    assert handler.summary_count_dict[handler.create_action] == 1
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0

def test_increment_summary_count_update():
    """Test only update count incremented for update action """
    handler.initialise_summary_count()
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0
    values = {"action":"UPDATE"}
    handler.increment_summary_count(values)
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 1
    assert handler.summary_count_dict[handler.delete_action] == 0

def test_increment_summary_count_delete():
    """Test only delete count incremented for delete action """
    handler.initialise_summary_count()
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0
    values = {"action":"DELETE"}
    handler.increment_summary_count(values)
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 1

def test_increment_summary_count_nosuch():
    """Test NO count incremented for invalid action """
    handler.initialise_summary_count()
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0
    values = {"action":"NOSUCH"}
    handler.increment_summary_count(values)
    assert handler.summary_count_dict[handler.create_action] == 0
    assert handler.summary_count_dict[handler.update_action] == 0
    assert handler.summary_count_dict[handler.delete_action] == 0

def generate_event_payload():
    """Utility function to generate dummy event data"""
    return {"filename": filename, "env": env, "bucket": bucket}
