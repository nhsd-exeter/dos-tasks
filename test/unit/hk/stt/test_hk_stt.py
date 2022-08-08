from unittest.mock import Mock, patch
import pytest
import string
import psycopg2
import os

from .. import handler
# from .. import scenario
from utilities import secrets,common

file_path = "application.hk.stt.handler"
env = "unittest"
# test/unit/hk/stt/Scenario_2.xml
sample_scenario_file_name = "test-files/Scenario_2.xml"
alt_scenario_file_name = "test-files/Scenario 1.xml"
malformed_scenario_file_name = "test-files/Scenario_malformed.xml"
sample_bundle_file_name = "19.0.zip"
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
#  TODO get tree once

def test_listdir():
    print(os.listdir())
    assert True == True

def test_get_pathways_release_id():
    """Test function to extract bundle/pathways release version from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    pathways_release_id = handler.get_pathways_release_id(tree)
    assert pathways_release_id == expected_pathways_release_id

def test_get_scenario_id_from_file_name_with_underscore_separator():
    """Test function to extract scenario id from name of file"""
    scenario_id = handler.get_scenario_id_from_file_name(sample_scenario_file_name)
    assert scenario_id == expected_scenario_id

def test_get_scenario_id_from_file_name_with_space_separator():
    """Test function to extract scenario id from name of file"""
    scenario_id = handler.get_scenario_id_from_file_name(alt_scenario_file_name)
    assert scenario_id == alt_expected_scenario_id

def test_get_symptom_group():
    """Test function to extract symptomgroup from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    symptom_group = handler.get_symptom_group(tree)
    assert symptom_group == expected_symptom_group

def test_get_triage_disposition_uid():
    """Test function to extract triage disposition uid from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    disposition_uid = handler.get_triage_disposition_uid(tree)
    assert disposition_uid == expected_triage_disposition_uid

def test_get_triage_disposition_description():
    """Test function to extract triage disposition description from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    disposition_description = handler.get_triage_disposition_description(tree)
    assert disposition_description == expected_triage_disposition_description

def test_get_final_disposition_group_cmsid():
    """Test function to extract final disposition cmsid from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    final_disposition_cmsid = handler.get_final_disposition_group_cmsid(tree)
    assert final_disposition_cmsid == expected_final_disposition_group_cmsid

def test_get_final_disposition_code():
    """Test function to extract final disposition code from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    final_disposition_code = handler.get_final_disposition_code(tree)
    assert final_disposition_code == expected_final_disposition_code

def test_get_triage_lines():
    """Test function to extract all triage lines from xml"""
    triage_lines = []
    tree = handler.get_tree(sample_scenario_file_name)
    triage_lines = handler.get_triage_lines(tree)
    assert len(triage_lines) == expected_number_of_triage_lines

def test_get_triage_line_data():
    """Test function to extract last symptom discriminator from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    report_texts, symptom_discriminator_uid, symptom_discriminator_desc = handler.get_triage_line_data(tree)
    assert len(report_texts) == expected_report_text_length
    assert report_texts[expected_report_text_length-1] == expected_last_report_text
    assert symptom_discriminator_uid == expected_symptom_discriminator_uid
    assert symptom_discriminator_desc == expected_symptom_discriminator_desc_text

def test_process_scenario():
    scenario = handler.process_scenario_file(sample_scenario_file_name,sample_scenario_file_name)
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
        handler.process_scenario_file(malformed_scenario_file_name,malformed_scenario_file_name)

@patch("psycopg2.connect")
def test_process_zipfile(mock_db_connect):
    handler.process_zipfile(mock_db_connect, sample_bundle_file_name)
    # TODO
    assert True == True

def test_get_insert_query():
    expected_report_texts = "One.Two.Three"
    template_scenario = handler.process_scenario_file(sample_scenario_file_name,sample_scenario_file_name)
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
