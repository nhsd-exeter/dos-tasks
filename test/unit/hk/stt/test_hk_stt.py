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

sample_scenario_file_name = "test-files/Scenario_2.xml"
alt_scenario_file_name = "test-files/Scenario 1.xml"
malformed_scenario_file_name = "test-files/Scenario_malformed.xml"
sample_bundle_file_name = "test-files/19.0.zip"
malformed_bundle_file_name = "test-files/Scenario_malformed.zip"
expected_symptom_group = "1203"
expected_triage_disposition_uid = "Dx75"
expected_triage_disposition_description = "MUST contact own GP Practice within 3 working days"
expected_final_disposition_group_cmsid = "1075"
expected_final_disposition_code = "Dx75"
expected_report_text_length = 33
expected_number_of_triage_lines = 62
expected_last_report_text = "Remember to take a list of any current medications if you go to the out of hours surgery."
expected_symptom_discriminator_uid = '4533'
expected_symptom_discriminator_desc_text = 'Improving Access to Psychological Therapies service'
expected_pathways_release_id = "25.2.0"
expected_scenario_id = "2"
alt_expected_scenario_id = "1"
#  TODO get root once


@patch(f"{file_path}.common.archive_file")
@patch(f"{file_path}.message.send_failure_slack_message")
@patch(f"{file_path}.message.send_success_slack_message")
@patch(f"{file_path}.database.close_connection", return_value="")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
@patch(f"{file_path}.common.retrieve_compressed_file_from_bucket", return_value="zip_file")
@patch(f"{file_path}.process_zipfile", return_value=True)
@patch(f"{file_path}.message.send_start_message")
def test_handler_pass(mock_send_start_message,
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
def test_handler_fail(mock_send_start_message,
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
    mock_process_zipfile.assert_called_once()
    mock_retrieve_file_from_bucket.assert_called_once()
    mock_db_connection.assert_called_once()
    mock_close_connection.assert_called_once()
    mock_archive_file.assert_called_once()
    mock_send_failure_slack_message.assert_called_once()
    assert mock_send_success_slack_message.call_count == 0

def test_get_pathways_release_id():
    """Test function to extract bundle/pathways release version from xml"""
    # root = handler.get_root(convert_file_to_stream(sample_scenario_file_name))
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    pathways_release_id = handler.get_pathways_release_id(scenario_dict)
    assert pathways_release_id == expected_pathways_release_id

def test_get_symptom_group():
    """Test function to extract symptomgroup from xml"""
    # root = handler.get_root(convert_file_to_stream(sample_scenario_file_name))
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    symptom_group = handler.get_symptom_group(scenario_dict)
    assert symptom_group == expected_symptom_group

def test_get_triage_disposition_uid():
    """Test function to extract triage disposition uid from xml"""
    # root = handler.get_root(convert_file_to_stream(sample_scenario_file_name))
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    disposition_uid = handler.get_triage_disposition_uid(scenario_dict)
    assert disposition_uid == expected_triage_disposition_uid

def test_get_triage_disposition_description():
    """Test function to extract triage disposition description from xml"""
    # root = handler.get_root(convert_file_to_stream(sample_scenario_file_name))
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    disposition_description = handler.get_triage_disposition_description(scenario_dict)
    assert disposition_description == expected_triage_disposition_description

def test_get_final_disposition_group_cmsid():
    """Test function to extract final disposition cmsid from xml"""
    # root = handler.get_root(convert_file_to_stream(sample_scenario_file_name))
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    final_disposition_cmsid = handler.get_final_disposition_group_cmsid(scenario_dict)
    assert final_disposition_cmsid == expected_final_disposition_group_cmsid

def test_get_final_disposition_code():
    """Test function to extract final disposition code from xml"""
    # root = handler.get_root(convert_file_to_stream(sample_scenario_file_name))
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    final_disposition_code = handler.get_final_disposition_code(scenario_dict)
    assert final_disposition_code == expected_final_disposition_code

def test_get_triage_lines():
    """Test function to extract all triage lines from xml"""
    triage_lines = []
    # root = handler.get_root(convert_file_to_stream(sample_scenario_file_name))
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    triage_lines = handler.get_triage_lines(scenario_dict)
    assert len(triage_lines) == expected_number_of_triage_lines

def test_get_triage_line_data():
    """Test function to extract last symptom discriminator from xml"""
    # root = handler.get_root(convert_file_to_stream(sample_scenario_file_name))
    scenario_dict = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
    report_texts, symptom_discriminator_uid, symptom_discriminator_desc = handler.get_triage_line_data(scenario_dict)
    assert len(report_texts) == expected_report_text_length
    assert report_texts[expected_report_text_length-1] == expected_last_report_text
    assert symptom_discriminator_uid == expected_symptom_discriminator_uid
    assert symptom_discriminator_desc == expected_symptom_discriminator_desc_text

def test_process_scenario():
    scenario = handler.process_scenario_file(sample_scenario_file_name, convert_file_to_stream(sample_scenario_file_name))
    assert scenario.file_name == sample_scenario_file_name
    assert scenario.pathways_release_id == expected_pathways_release_id
    assert scenario.symptom_group == expected_symptom_group
    assert scenario.triage_disposition_uid == expected_triage_disposition_uid
    assert scenario.triage_disposition_description == expected_triage_disposition_description
    assert scenario.final_disposition_group_cmsid == expected_final_disposition_group_cmsid
    assert scenario.final_disposition_code == expected_final_disposition_code
    assert len(scenario.report_texts) == expected_report_text_length
    assert scenario.symptom_discriminator_uid == expected_symptom_discriminator_uid
    assert scenario.symptom_discriminator_desc_text == expected_symptom_discriminator_desc_text

def test_process_malformed_scenario():
    with pytest.raises(Exception):
        handler.process_scenario_file(malformed_scenario_file_name,convert_file_to_stream(malformed_scenario_file_name))

@patch("psycopg2.connect")
def test_process_zipfile(mock_db_connect):
    bundle = get_compressed_object(sample_bundle_file_name)
    processed = handler.process_zipfile(env, mock_db_connect,bundle,mock_zip_filename)
    assert processed == True

@patch("psycopg2.connect")
def test_process_non_zipfile(mock_db_connect):
    processed = handler.process_zipfile(env, mock_db_connect,sample_scenario_file_name,alt_scenario_file_name)
    assert processed == False

@patch("psycopg2.connect")
def test_process_malformed_xml_in_zipfile(mock_db_connect):
    bundle = get_compressed_object(malformed_bundle_file_name)
    processed = handler.process_zipfile(env, mock_db_connect,bundle,malformed_bundle_file_name)
    assert processed == False

def test_get_insert_query():
    expected_report_texts = "One.Two.Three"
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,convert_file_to_stream(sample_scenario_file_name))
    template_scenario.report_texts = expected_report_texts
    query, data = handler.get_insert_query(template_scenario)
    assert query == """insert into pathwaysdos.searchscenarios (releaseid, scenarioid, symptomgroup_uid, triagedispositionuid,
    triage_disposition_description, final_disposition_group_cmsid, final_disposition_code,
    report_texts, symptom_discriminator_uid, symptom_discriminator_desc_text, scenariofilename,
    scenariofile, created_on)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now()
    )"""
    assert data == (expected_pathways_release_id,
        sample_scenario_file_name,
        expected_symptom_group,
        expected_triage_disposition_uid,
        expected_triage_disposition_description,
        expected_final_disposition_group_cmsid,
        expected_final_disposition_code,
        expected_report_texts,
        expected_symptom_discriminator_uid,
        expected_symptom_discriminator_desc_text,
        sample_scenario_file_name,
        sample_scenario_file_name)

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


# def map_xml_to_json():
#     d = handler.map_xml_to_json(convert_file_to_stream(sample_scenario_file_name))
#     print(d["NHSPathways"]["PathwaysCase"]["PathwaysReleaseID"])
#     assert True == False

