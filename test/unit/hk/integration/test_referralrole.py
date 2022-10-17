from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from models import referralrole

file_path = "application.models.referralrole"
env = 'unittest'
def test_check_referral_role_record_true():
    name = 'Integration Test Update'
    referral_role = {'id':2000,'name':'Integration Test Update'}
    assert referralrole.check_referral_role_record(env, referral_role, name) == True

def test_check_referral_role_record_false_name():
    name = 'Integration Test Updat'
    referral_role = {'id':2000,'name':'Integration Test Update'}
    assert referralrole.check_referral_role_record(env, referral_role, name) == False

def test_create_referral_role_query():
    referral_role_ids = '(2000,2001,2002)'
    expected_query_string = "select id, name from pathwaysdos.referralroles where id in (2000,2001,2002) order by id asc;"
    expected_data = referral_role_ids
    query, data = referralrole.create_referral_role_query(referral_role_ids)
    assert query == expected_query_string
    assert data == expected_data

@patch("psycopg2.connect")
@patch(f"{file_path}.database.execute_resultset_query",side_effect=Exception)
def test_check_referral_roles_data_deleted_record(mock_resultset, mock_db):
    result_set = referralrole.get_referral_roles_data(env,mock_db)
    assert result_set == {}
