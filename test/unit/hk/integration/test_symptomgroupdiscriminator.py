from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from models import symptomgroupsymptomdiscriminator

file_path = "application.models.symptomgroupsymptomdiscriminator"
env = 'unittest'

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"symptomgroupid":1121,"symptomdiscriminatorid":4033}])
def test_check_sgsd_record_expected(mock_db, mock_resultset):
    assert symptomgroupsymptomdiscriminator.check_symptom_group_symptom_discriminators_data(env, mock_db) == True

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"symptomgroupid":1120,"symptomdiscriminatorid":4033}])
def test_check_sgsd_record_created_missing_wrong_sg(mock_db, mock_resultset):
    assert symptomgroupsymptomdiscriminator.check_symptom_group_symptom_discriminators_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"symptomgroupid":1121,"symptomdiscriminatorid":4032}])
def test_check_sgsd_record_created_missing_wrong_sd(mock_db, mock_resultset):
    assert symptomgroupsymptomdiscriminator.check_symptom_group_symptom_discriminators_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"symptomgroupid":1121,"symptomdiscriminatorid":4032},{"symptomgroupid":1121,"symptomdiscriminatorid":4017}])
def test_check_sgsd_record_created_with_deleted_record(mock_db, mock_resultset):
    assert symptomgroupsymptomdiscriminator.check_symptom_group_symptom_discriminators_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",side_effect=Exception)
def test_check_symptom_discriminators_data_deleted_record(mock_resultset, mock_db):
    result_set = symptomgroupsymptomdiscriminator.get_symptom_group_symptom_discriminators_data(env,mock_db)
    assert result_set == {}
