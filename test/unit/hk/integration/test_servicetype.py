from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from models import servicetype

file_path = "application.models.servicetype"
env = 'unittest'
national_ranking = 8

def test_check_service_type_record_true():
    name = 'Integration Test Update'
    service_type = {'id':2000,'name':'Integration Test Update','nationalranking':8, 'searchcapacitystatus':True, 'capacitymodel':'n/a', 'capacityreset':'interval'}
    assert servicetype.check_service_type_record(env, service_type, name, national_ranking) == True

def test_check_service_type_record_false_ranking():
    name = 'Integration Test Update'
    service_type = {'id':2000,'name':'Integration Test Update','nationalranking':9, 'searchcapacitystatus':True, 'capacitymodel':'n/a', 'capacityreset':'interval'}
    assert servicetype.check_service_type_record(env, service_type, name, national_ranking) == False

def test_check_service_type_record_false_name():
    name = 'Integration Test Updat'
    service_type = {'id':2000,'name':'Integration Test Update','nationalranking':8, 'searchcapacitystatus':True, 'capacitymodel':'n/a', 'capacityreset':'interval'}
    assert servicetype.check_service_type_record(env, service_type, name, national_ranking) == False

def test_create_service_type_query():
    service_type_ids = '(2000,2001,2002)'
    expected_query_string = "select id, name, nationalranking, searchcapacitystatus, capacitymodel, capacityreset from servicetypes  where id = %s or id = %s or id = %s;"
    expected_data = service_type_ids
    query, data = servicetype.create_service_type_query(service_type_ids)
    assert query.replace(" ", "") == expected_query_string.replace(" ", "")
    assert data == expected_data

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",side_effect=Exception)
def test_check_service_types_data_deleted_record(mock_resultset, mock_db):
    result_set = servicetype.get_service_types_data(env,mock_db)
    assert result_set == {}
