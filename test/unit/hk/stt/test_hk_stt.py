from unittest.mock import Mock, patch
from moto import mock_s3
import pytest
import string
import psycopg2
import os
import io
import boto3
from utilities import s3


from .. import handler
# from .. import scenario
from utilities import secrets,common

file_path = "application.hk.stt.handler"
env = "unittest"
bucket = "NoSuchBucket"
mock_zip_filename = "mock_env/mock_file.zip"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
start = "20220527"

bundle_id = 4
sample_scenario_file_name = "test-files/Scenario_2.xml"
original_scenario_file_name = "test-files/Scenario 380.xml"
empty_disposition_group_element_scenario_file_name = "test-files/Scenario 596.xml"
alt_scenario_file_name = "test-files/Scenario 1.xml"
malformed_scenario_file_name = "test-files/Scenario_malformed.xml"
# build by running unarchiver against .rar and then removing _MACOSX__ paths from output
sample_bundle_file_name = "test-files/R34.2.0_stt.zip"
malformed_bundle_file_name = "test-files/Scenario_malformed.zip"
expected_symptom_group_id = "1203"
expected_disposition_code = "DX75"
expected_disposition_group_id = "1075"
expected_triage_report_length = 33
expected_number_of_triage_lines = 62
expected_triage_report_last_line = "Remember to take a list of any current medications if you go to the out of hours surgery."
expected_symptom_discriminator_id = '4533'
expected_scenario_id = 2
alt_expected_scenario_id = "1"
expected_gender_id = "2"
expected_age_id = "1"


@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_compressed_file_from_bucket", return_value="zip_file")
@patch(f"{file_path}.process_zipfile", return_value=True)
@patch(f"{file_path}.message.send_start_message")
@patch(f"{file_path}.add_bundle", return_value=4)
def test_handler_pass(mock_add_bundle, mock_send_start_message,
mock_process_zipfile,
mock_retrieve_file_from_bucket,
mock_db_connection,
mock_close_connection,
mock_send_success_slack_message,
mock_send_failure_slack_message,
mock_archive_file):
    """Test top level request calls downstream functions - success"""
    payload = generate_event_payload()
    result = handler.request(event=payload, context=None)
    assert result == "Import STT scenarios execution completed"
    mock_send_start_message.assert_called_once()
    mock_add_bundle.assert_called_once()
    mock_process_zipfile.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()
    mock_close_connection.assert_called_once()
    mock_archive_file.assert_called_once()
    mock_send_success_slack_message.assert_called_once()
    assert mock_send_failure_slack_message.call_count == 0

@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_compressed_file_from_bucket", return_value="zip_file")
@patch(f"{file_path}.process_zipfile", return_value=False)
@patch(f"{file_path}.message.send_start_message")
@patch(f"{file_path}.add_bundle", return_value=4)
def test_handler_fail(mock_add_bundle,mock_send_start_message,
mock_process_zipfile,
mock_retrieve_file_from_bucket,
mock_db_connection,
mock_close_connection,
mock_send_success_slack_message,
mock_send_failure_slack_message,
mock_archive_file):
    """Test top level request calls downstream functions - success"""
    payload = generate_event_payload()
    result = handler.request(event=payload, context=None)
    assert result == "Import STT scenarios execution completed"
    mock_send_start_message.assert_called_once()
    mock_add_bundle.assert_called_once()
    mock_process_zipfile.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()
    mock_close_connection.assert_called_once()
    mock_archive_file.assert_called_once()
    mock_send_failure_slack_message.assert_called_once()
    assert mock_send_success_slack_message.call_count == 0

def test_get_scenario_id_underscore():
    """Test function to extract scenario id from file name"""
    expected_scenario_id = 180
    scenario_id = handler.get_scenario_id("Scenario_180.xml")
    assert scenario_id == expected_scenario_id

def test_get_scenario_id_space():
    """Test function to extract scenario id from file name"""
    expected_scenario_id = 170
    scenario_id = handler.get_scenario_id("Scenario 170.xml")
    assert scenario_id == expected_scenario_id

def test_get_scenario_id_space():
    """Test function to extract scenario id from file name"""
    expected_scenario_id = 170
    scenario_id = handler.get_scenario_id("Scenario 170.xml")
    assert scenario_id == expected_scenario_id

def test_get_scenario_id_no_int():
    """Test function to extract scenario id from file name"""
    with pytest.raises(ValueError) as raised_exception:
        handler.get_scenario_id("Scenario abc.xml")
    assert str(raised_exception.value) == "Can't convert abc to int for storing as scenario id"

def test_get_bundle_name_release_number():
    """Test function to extract bundle name from zip file provided"""
    expected_bundle_name = "33.2.0"
    bundle_name = handler.get_bundle_name("teamb/R33.2.0_STT_Bundle_stt.zip")
    assert expected_bundle_name == bundle_name

def test_get_bundle_name_repeat_prescription():
    """Test function to extract bundle name from zip file with lead R but not release number"""
    expected_bundle_name = "Repeat-Prescription"
    bundle_name = handler.get_bundle_name("teamb/Repeat-Prescription_stt.zip")
    assert expected_bundle_name == bundle_name

def test_get_bundle_name_no_release_number():
    """Test function to extract bundle name from zip file provided"""
    expected_bundle_name = "Dental"
    bundle_name = handler.get_bundle_name("teamb/Dental_stt.zip")
    assert expected_bundle_name == bundle_name


def test_get_gender_id():
    """Test function to extract symptomgroup from xml"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    gender_id = handler.get_gender_id(scenario_dict)
    assert gender_id == expected_gender_id

def test_get_age_id():
    """Test function to extract symptomgroup from xml"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    age_id = handler.get_age_id(scenario_dict)
    assert age_id == expected_age_id

def test_get_symptom_group_id():
    """Test function to extract symptomgroup from xml"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    symptom_group = handler.get_symptom_group_id(scenario_dict)
    assert symptom_group == expected_symptom_group_id

def test_get_disposition_id_query():
    """Test function to build query to look up disposition id from code"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    disposition_code = handler.get_disposition_code(scenario_dict)
    query, data = handler.get_disposition_id_query(disposition_code)
    assert query == """select id from pathwaysdos.dispositions where upper(dxcode) = %s"""
    assert data == (disposition_code,)

def test_get_disposition_group_id_query():
    """Test function to build query to look up disposition group id from uid"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    disposition_group_uid = handler.get_disposition_group_uid(scenario_dict)
    query, data = handler.get_disposition_group_id_query(disposition_group_uid)
    assert query == """select id from pathwaysdos.dispositiongroups where uid = %s"""
    assert data == (disposition_group_uid,)

def test_get_disposition_group_id_query_missing_element():
    """Test function to build query to look up disposition group id from uid"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(original_scenario_file_name))
    disposition_group_uid = handler.get_disposition_group_uid(scenario_dict)
    query, data = handler.get_disposition_group_id_query(disposition_group_uid)
    assert query == """select id from pathwaysdos.dispositiongroups where uid = %s"""
    assert data == (disposition_group_uid,)
    assert disposition_group_uid == None

def test_get_disposition_group_id_query_empty_element():
    """Test function to build query to look up disposition group id from uid"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(empty_disposition_group_element_scenario_file_name))
    disposition_group_uid = handler.get_disposition_group_uid(scenario_dict)
    query, data = handler.get_disposition_group_id_query(disposition_group_uid)
    assert query == """select id from pathwaysdos.dispositiongroups where uid = %s"""
    assert data == (disposition_group_uid,)
    assert disposition_group_uid == None


#
@patch("psycopg2.connect")
@patch(f"{file_path}.get_disposition_code", return_value="DX20")
@patch(f"{file_path}.get_disposition_id_query",side_effect=[{1:'',2:''}])
@patch(f"{file_path}.database.execute_resultset_query",return_value=[{"id":1}])
def test_get_valid_disposition_id(mock_execute, mock_query, mock_code, mock_db_connect):
    """Test function to derive id of disposition from db based on code"""
    scenario_dict = {}
    disposition_id = handler.get_disposition_id(scenario_dict, mock_db_connect)
    assert disposition_id == 1
    mock_code.assert_called_once()
    mock_query.assert_called_once()
    mock_execute.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.get_disposition_code", return_value="DX20")
@patch(f"{file_path}.get_disposition_id_query",side_effect=[{1:'',2:''}])
@patch(f"{file_path}.database.execute_resultset_query",return_value=[])
def test_get_invalid_disposition_id(mock_execute, mock_query, mock_code, mock_db_connect):
    """Test function to derive id of disposition from db based on code"""
    scenario_dict = {}
    disposition_id = handler.get_disposition_id(scenario_dict, mock_db_connect)
    assert disposition_id is None
    mock_code.assert_called_once()
    mock_query.assert_called_once()
    mock_execute.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.get_disposition_group_uid", return_value="1002")
@patch(f"{file_path}.get_disposition_group_id_query",side_effect=[{1:'',2:''}])
@patch(f"{file_path}.database.execute_resultset_query",return_value=[{"id":6}])
def test_get_valid_disposition_group_id(mock_execute, mock_query, mock_code, mock_db_connect):
    """Test function to derive id of disposition from db based on code"""
    scenario_dict = {}
    disposition_group_id = handler.get_disposition_group_id(scenario_dict, mock_db_connect)
    assert disposition_group_id == 6
    mock_code.assert_called_once()
    mock_query.assert_called_once()
    mock_execute.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.get_disposition_group_uid", return_value="1002")
@patch(f"{file_path}.get_disposition_group_id_query",side_effect=[{1:'',2:''}])
@patch(f"{file_path}.database.execute_resultset_query",return_value=[])
def test_get_invalid_disposition_group_id(mock_execute, mock_query, mock_code, mock_db_connect):
    """Test function to derive id of disposition from db based on code"""
    scenario_dict = {}
    disposition_group_id = handler.get_disposition_group_id(scenario_dict, mock_db_connect)
    assert disposition_group_id is None
    mock_code.assert_called_once()
    mock_query.assert_called_once()
    mock_execute.assert_called_once()


def test_get_disposition_code():
    """Test function to extract triage disposition uid from xml"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    disposition_code = handler.get_disposition_code(scenario_dict)
    assert disposition_code == expected_disposition_code

def test_get_disposition_group_uid():
    """Test function to extract final disposition cmsid from xml"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    disposition_group_id = handler.get_disposition_group_uid(scenario_dict)
    assert disposition_group_id == expected_disposition_group_id

def test_get_disposition_group_uid_missing_element():
    """Test function to extract final disposition cmsid from xml"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(original_scenario_file_name))
    disposition_group_id = handler.get_disposition_group_uid(scenario_dict)
    assert disposition_group_id == None

def test_get_triage_lines():
    """Test function to extract all triage lines from xml"""
    triage_lines = []
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    triage_lines = handler.get_triage_lines(scenario_dict)
    assert len(triage_lines) == expected_number_of_triage_lines

def test_get_triage_line_data():
    """Test function to extract last symptom discriminator from xml"""
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    triage_report, symptom_discriminator_id = handler.get_triage_line_data(scenario_dict)
    assert len(triage_report) == expected_triage_report_length
    assert triage_report[expected_triage_report_length-1] == expected_triage_report_last_line
    assert symptom_discriminator_id == expected_symptom_discriminator_id

@patch("psycopg2.connect")
@patch(f"{file_path}.get_disposition_group_id",return_value=5)
@patch(f"{file_path}.get_disposition_id",return_value=6)
def test_process_scenario(mock_disposition, mock_disposition_group, mock_db_connect):
    scenario = handler.process_scenario_file(sample_scenario_file_name, convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    assert scenario.bundle_id == bundle_id
    assert scenario.scenario_id == expected_scenario_id
    assert scenario.symptom_group_id == expected_symptom_group_id
    assert scenario.disposition_id == 6
    assert scenario.disposition_group_id == 5
    assert len(scenario.triage_report) == expected_triage_report_length
    assert scenario.symptom_discriminator_id == expected_symptom_discriminator_id
    assert scenario.gender_id == expected_gender_id
    assert scenario.age_id == expected_age_id

def test_process_malformed_scenario():
    with pytest.raises(Exception):
        handler.process_scenario_file(malformed_scenario_file_name,convert_file_to_stream(malformed_scenario_file_name), bundle_id)

@patch("psycopg2.connect")
@patch(f"{file_path}.get_disposition_group_id",return_value=5)
@patch(f"{file_path}.get_disposition_id",return_value=5)
def test_process_zipfile(mock_disposition, mock_disposition_group, mock_db_connect):
    bundle = get_compressed_object(sample_bundle_file_name)
    processed = handler.process_zipfile(env, mock_db_connect, bundle,mock_zip_filename, bundle_id)
    assert processed == True
    assert mock_disposition.call_count == 3
    assert mock_disposition_group.call_count == 3

@patch("psycopg2.connect")
def test_process_non_zipfile(mock_db_connect):
    processed = handler.process_zipfile(env, mock_db_connect, sample_scenario_file_name, alt_scenario_file_name, bundle_id)
    assert processed == False

@patch("psycopg2.connect")
def test_process_malformed_xml_in_zipfile(mock_db_connect):
    bundle = get_compressed_object(malformed_bundle_file_name)
    processed = handler.process_zipfile(env, mock_db_connect,bundle,malformed_bundle_file_name, bundle_id)
    assert processed == False

@patch("psycopg2.connect")
@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.get_disposition_group_id",return_value=5)
@patch(f"{file_path}.get_disposition_id",return_value=5)
@patch(f"{file_path}.validate_template_scenario",return_value=False)
def test_process_zipfile_invalid_template(mock_validator, mock_disposition, mock_disposition_group, mock_logger, mock_db_connect):
    bundle = get_compressed_object(sample_bundle_file_name)
    processed = handler.process_zipfile(env, mock_db_connect, bundle,mock_zip_filename, bundle_id)
    assert processed == True
    assert mock_disposition.call_count == 3
    assert mock_disposition_group.call_count == 3
    assert mock_logger.call_count == 6

@patch("psycopg2.connect")
@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.get_disposition_group_id",return_value=5)
@patch(f"{file_path}.get_disposition_id",return_value=5)
@patch(f"{file_path}.validate_template_scenario",return_value=True)
def test_process_zipfile_valid_template(mock_validator, mock_disposition, mock_disposition_group, mock_logger, mock_db_connect):
    bundle = get_compressed_object(sample_bundle_file_name)
    processed = handler.process_zipfile(env, mock_db_connect, bundle,mock_zip_filename, bundle_id)
    assert processed == True
    assert mock_disposition.call_count == 3
    assert mock_disposition_group.call_count == 3
    assert mock_logger.call_count == 6

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value=([{"id": 3}]))
@patch(f"{file_path}.get_bundle_insert_query",return_value=("query", "data"))
@patch(f"{file_path}.is_new_bundle", return_value=None)
def test_add_bundle(mock_new_bundle, mock_query, mock_execute, mock_db_connect):
    """Test function to add bundle to database"""
    bundle_file_name = "teamb/R32.2.3_stt.zip"
    inserted_bundle_id = handler.add_bundle(env, mock_db_connect, bundle_file_name)
    assert inserted_bundle_id == 3
    assert mock_new_bundle.call_count == 1

def test_get_bundle_insert_query():
    bundle_id = 5
    query,data = handler.get_bundle_insert_query(bundle_id)
    assert query == """insert into pathwaysdos.scenariobundles (name,createdtime) values (%s,now()) returning id"""
    assert data == (bundle_id,)

@patch("psycopg2.connect")
@patch(f"{file_path}.get_disposition_group_id",return_value=7)
@patch(f"{file_path}.get_disposition_id",return_value=8)
def test_get_scenario_insert_query( mock_disposition, mock_disposition_group, mock_db_connect):
    expected_triage_report = "One.Two.Three"
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    template_scenario.triage_report = expected_triage_report
    query, data = handler.get_scenario_insert_query(template_scenario)
    assert query == """insert into pathwaysdos.scenarios(bundleid, scenarioid, symptomgroupid, dispositionid,
dispositiongroupid, symptomdiscriminatorid, ageid, genderid, triagereport, createdtime
)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,now()
    )"""
    assert data == (bundle_id,
        expected_scenario_id,
        expected_symptom_group_id,
        8,
        7,
        expected_symptom_discriminator_id,
        expected_age_id,
        expected_gender_id,
        expected_triage_report,
    )
    mock_disposition.assert_called_once()
    mock_disposition_group.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.get_disposition_group_id",return_value=7)
@patch(f"{file_path}.get_disposition_id",return_value=8)
def test_validate_template_scenario_invalid_disposition(mock_disposition, mock_disposition_group, mock_logger, mock_db_connect):
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    template_scenario.disposition_id = None
    valid_template = handler.validate_template_scenario(env, template_scenario)
    assert valid_template == False
    assert mock_logger.call_count == 1
    mock_disposition.assert_called_once()
    mock_disposition_group.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.get_disposition_group_id",return_value=7)
@patch(f"{file_path}.get_disposition_id",return_value=8)
def test_validate_template_scenario_invalid_disposition_group(mock_disposition, mock_disposition_group, mock_logger, mock_db_connect):
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    template_scenario.disposition_group_id = None
    valid_template = handler.validate_template_scenario(env, template_scenario)
    assert valid_template == True
    assert mock_logger.call_count == 1
    mock_disposition.assert_called_once()
    mock_disposition_group.assert_called_once()

@patch("psycopg2.connect")
@patch(f"{file_path}.get_disposition_group_id_query")
@patch(f"{file_path}.database.execute_resultset_query")
def test_get_disposition_group_id(mock_execute, mock_query, mock_db_connect):
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(original_scenario_file_name))
    disposition_group_id = handler.get_disposition_group_id(scenario_dict,mock_db_connect)
    assert disposition_group_id == None
    assert mock_execute.call_count == 0
    assert mock_query.call_count == 0

@patch("psycopg2.connect")
def test_get_existing_scenario_check_query(mock_db_connect):
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    query, data = handler.get_existing_scenario_check_query(template_scenario)
    assert query == """select s.id from pathwaysdos.scenarios s where s.bundleid = %s and
    s.scenarioid = %s"""
    assert data == (bundle_id,expected_scenario_id,)

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",return_value=([{"id": 3}]))
def test_is_not_new_scenario(mock_execute, mock_db_connect):
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    is_new_scenario = handler.is_new_scenario(mock_db_connect, template_scenario)
    assert is_new_scenario == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",return_value=[])
def test_is_new_scenario(mock_execute, mock_db_connect):
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    is_new_scenario = handler.is_new_scenario(mock_db_connect, template_scenario)
    assert is_new_scenario == True
# -----
@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",return_value=([{"id": 3}]))
@patch(f"{file_path}.get_existing_bundle_check_query", return_value=("query", "data"))
def test_is_not_new_bundle(mock_query, mock_execute, mock_db_connect):
    is_new_bundle = handler.is_new_bundle(mock_db_connect, "Dental")
    assert is_new_bundle == 3
    assert mock_query.call_count == 1

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",return_value=([]))
@patch(f"{file_path}.get_existing_bundle_check_query", return_value=("query", "data"))
def test_is_new_bundle(mock_query, mock_execute, mock_db_connect):
    is_new_bundle = handler.is_new_bundle(mock_db_connect, "Dental")
    assert is_new_bundle == None
    assert mock_query.call_count == 1

@patch("psycopg2.connect")
def test_get_existing_bundle_check_query(mock_db_connect):
    bundle_name = "Dental"
    query, data = handler.get_existing_bundle_check_query(bundle_name)
    assert query == """select sb.id from pathwaysdos.scenariobundles sb where sb.name = %s"""
    assert data == (bundle_name,)
# ------
@patch("psycopg2.connect")
@patch(f"{file_path}.is_new_scenario",return_value=True)
@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.database.execute_query")
@patch(f"{file_path}.get_scenario_insert_query",return_value=("query", "data"))
def test_insert_template_scenario(mock_insert, mock_execute, mock_logger, mock_is_new, mock_db_connect):
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    handler.insert_template_scenario(env, mock_db_connect, template_scenario)
    assert mock_logger.call_count == 1
    assert mock_insert.call_count == 1
    assert mock_execute.call_count == 1
    assert mock_is_new.call_count == 1


@patch("psycopg2.connect")
@patch(f"{file_path}.is_new_scenario",return_value=False)
@patch(f"{file_path}.logger.log_for_audit")
@patch(f"{file_path}.database.execute_query")
@patch(f"{file_path}.get_scenario_insert_query",return_value=("query", "data"))
def test_insert_duplicate_template_scenario(mock_insert, mock_execute, mock_logger, mock_is_new, mock_db_connect):
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name),bundle_id, mock_db_connect)
    handler.insert_template_scenario(env, mock_db_connect, template_scenario)
    assert mock_logger.call_count == 1
    assert mock_insert.call_count == 0
    assert mock_execute.call_count == 0
    assert mock_is_new.call_count == 1

def generate_event_payload():
    """Utility function to generate dummy event data"""
    return {"filename": sample_scenario_file_name, "env": env, "bucket": bucket}

def convert_file_to_stream(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return data

@mock_s3
def get_compressed_object(file_to_upload):

    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    s3_client.upload_file(Filename=file_to_upload, Bucket=bucket, Key=mock_zip_filename)
    response_body = s3.S3().get_compressed_object(bucket, mock_zip_filename, mock_event, start)
    return response_body
