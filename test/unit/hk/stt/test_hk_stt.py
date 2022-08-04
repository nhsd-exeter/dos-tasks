from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from .. import handler
from utilities import secrets,common

file_path = "application.hk.stt.handler"
env = "unittest"
sample_scenario_file_name = "sample.xml"

#  TODO get tree once

def test_get_symptom_group():
    """Test function to extract symptomgroup from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    symptom_group = handler.get_symptom_group(tree)
    assert symptom_group == "1203"

def test_get_triage_disposition_uid():
    """Test function to extract triage disposition uid from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    disposition_uid = handler.get_triage_disposition_uid(tree)
    assert disposition_uid == "Dx75"

def test_get_triage_disposition_description():
    """Test function to extract triage disposition description from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    disposition_description = handler.get_triage_disposition_description(tree)
    assert disposition_description == "MUST contact own GP Practice within 3 working days"

def test_get_final_disposition_group_cmsid():
    """Test function to extract final disposition cmsid from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    final_disposition_cmsid = handler.get_final_disposition_group_cmsid(tree)
    assert final_disposition_cmsid == "1075"

def test_get_final_disposition_code():
    """Test function to extract final disposition code from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    final_disposition_code = handler.get_final_disposition_code(tree)
    assert final_disposition_code == "Dx75"

def test_get_triage_lines():
    """Test function to extract all triage lines from xml"""
    triage_lines = []
    tree = handler.get_tree(sample_scenario_file_name)
    triage_lines = handler.get_triage_lines(tree)
    assert len(triage_lines) == 62

def test_get_triage_line_data():
    """Test function to extract last symptom discriminator from xml"""
    tree = handler.get_tree(sample_scenario_file_name)
    report_texts, symptom_discriminator_uid, symptom_discriminator_desc = handler.get_triage_line_data(tree)
    assert len(report_texts) == 33
    assert report_texts[32] == "Remember to take a list of any current medications if you go to the out of hours surgery."
    assert symptom_discriminator_uid == '4533'
    assert symptom_discriminator_desc == 'Improving Access to Psychological Therapies service'
