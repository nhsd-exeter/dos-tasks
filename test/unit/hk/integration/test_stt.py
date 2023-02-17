from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from models import stt

file_path = "application.models.stt"
env = 'unittest'

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":1,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499}])
def test_check_stt_expected(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == True

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.3.0',"ageid":1,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499}])
def test_check_stt_wrong_name(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":2,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499}])
def test_check_stt_wrong_age(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":1,"genderid":1,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499}])
def test_check_stt_wrong_gender(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":1,"genderid":2,"scenarioid":892,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499}])
def test_check_stt_wrong_scenarioid(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":1,"genderid":1,"scenarioid":893,"symptomgroupid":1015, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499}])
def test_check_stt_wrong_symptomgroupid(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":1,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":2, "dispositiongroupid":18, "symptomdiscriminatorid":4499}])
def test_check_stt_wrong_dispositionid(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":1,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":19, "symptomdiscriminatorid":4499}])
def test_check_stt_wrong_dispositiongroupid(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":1,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4500}])
def test_check_stt_wrong_symptomdiscriminatorid(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [])
def test_check_stt_empty_resultset(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.1',"ageid":1,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499},{"name":'36.2.0',"ageid":1,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499}])
def test_two_records_first_wrong(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False


@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query", return_value = [{"name":'36.2.0',"ageid":1,"genderid":1,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4499},{"name":'36.2.3',"ageid":1,"genderid":2,"scenarioid":893,"symptomgroupid":1014, "dispositionid":1, "dispositiongroupid":18, "symptomdiscriminatorid":4500}])
def test_two_records_second_wrong(mock_db, mock_resultset):
    assert stt.check_stt_scenario_data(env, mock_db) == False

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",side_effect=Exception)
def test_get_stt_scenario_data(mock_resultset, mock_db):
    result_set = stt.get_stt_scenario_data(env,mock_db)
    assert result_set == {}
