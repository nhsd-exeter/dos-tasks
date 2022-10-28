from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from models import symptomdiscriminator

file_path = "application.models.symptomdiscriminator"
env = 'unittest'
def test_check_symptom_group_record_true():
    description = 'Integration Test Update'
    symptom_discriminator = {'id':20000,'description':'Integration Test Update'}
    assert symptomdiscriminator.check_symptom_discriminator_record(env, symptom_discriminator, description) == True

def test_check_symptom_discriminator_record_false_description():
    description = 'Integration Test Updat'
    symptom_discriminator = {'id':20000,'description':'Integration Test Update'}
    assert symptomdiscriminator.check_symptom_discriminator_record(env, symptom_discriminator, description) == False

def test_create_symptom_discriminator_query():
    symptom_discriminator_ids = (20000,2001,20002)
    expected_query_string = "select id, description from pathwaysdos.from symptomdiscriminators where id = %s or id = %s or id = %s;"
    expected_data = symptom_discriminator_ids
    query, data = symptomdiscriminator.create_symptom_discriminator_query(symptom_discriminator_ids)
    assert query == expected_query_string
    assert data == expected_data

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",side_effect=Exception)
def test_check_symptom_discriminators_data_deleted_record(mock_resultset, mock_db):
    result_set = symptomdiscriminator.get_symptom_discriminator_data(env,mock_db)
    assert result_set == {}
