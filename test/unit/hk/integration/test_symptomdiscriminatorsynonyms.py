from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from models import symptomdiscriminatorsynonyms

file_path = "application.models.symptomdiscriminatorsynonyms"
env = 'unittest'

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{'symptomdiscriminatorid':11116,'name':'Integration test create'}])
def test_check_sds_record_expected(mock_db, mock_resultset):
    assert symptomdiscriminatorsynonyms.check_symptom_discriminator_synonyms_data(env, mock_db) == True


@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{'symptomdiscriminatorid':11009,'name':'Integration test wrong delete'}])
def test_check_sds_record_created_missing_wrong_sdid(mock_db, mock_resultset):
    assert symptomdiscriminatorsynonyms.check_symptom_discriminator_synonyms_data(env, mock_db) == False


@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{'symptomdiscriminatorid':11116,'name':'Integration test create'},{'symptomdiscriminatorid':11009,'name':'Integration test delete'}])
def test_check_sds_record_created_and_deleted_record(mock_db, mock_resultset):
    assert symptomdiscriminatorsynonyms.check_symptom_discriminator_synonyms_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",side_effect=Exception)
def test_check_symptom_discriminators_data_deleted_record(mock_resultset, mock_db):
    result_set = symptomdiscriminatorsynonyms.get_symptom_discriminator_synonyms_data(env,mock_db)
    assert result_set == {}

def test_create_symptom_discriminator_query():
    symptom_discriminator_synonym_values = (11009, "Integration test delete", 11116,"Integration test create")
    expected_query_string = """select symptomdiscriminatorid, name from pathwaysdos.symptomdiscriminatorsynonyms
where symptomdiscriminatorid = %s and name = %s
or symptomdiscriminatorid = %s and name = %s"""
    expected_data = symptom_discriminator_synonym_values
    print(expected_query_string)
    query, data = symptomdiscriminatorsynonyms.create_symptom_discriminator_synonyms_query(symptom_discriminator_synonym_values)
    assert query == expected_query_string
    assert data == expected_data
