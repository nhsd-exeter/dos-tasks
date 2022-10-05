from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from ..models import symptomgroup

file_path = "application.hk.integration.model.symptomgroup"

def test_check_symptom_group_record_true():
    name = 'Integration Test Update'
    zcodeexists = None
    symptom_group = {'id':2000,'name':'Integration Test Update','zcodeexists':None}
    assert symptomgroup.check_symptom_group_record(symptom_group, name, zcodeexists) == True

def test_check_symptom_group_record_false_name():
    name = 'Integration Test Updat'
    zcodeexists = None
    symptom_group = {'id':2000,'name':'Integration Test Update','zcodeexists':None}
    assert symptomgroup.check_symptom_group_record(symptom_group, name, zcodeexists) == False

def test_check_symptom_group_record_false_zcode():
    name = 'Integration Test Update'
    zcodeexists = None
    symptom_group = {'id':2000,'name':'Integration Test Update','zcodeexists':True}
    assert symptomgroup.check_symptom_group_record(symptom_group, name, zcodeexists) == False

def test_create_symptom_group_query():
    symptom_group_ids = '(2000,2001,2002)'
    expected_query_string = "select id, name, zcodeexists from pathwaysdos.symptomgroups where id in (%s) order by id asc;"
    expected_data = symptom_group_ids
    query, data = symptomgroup.create_symptom_group_query(symptom_group_ids)
    assert query == expected_query_string
    assert data == expected_data
