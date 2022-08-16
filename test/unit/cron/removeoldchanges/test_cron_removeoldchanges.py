from unittest import result
from unittest.mock import patch
from datetime import datetime, timedelta
from application.cron.removeoldchanges.handler import getThresholdDate
import pytest

# import string
# import psycopg2

from .. import handler
# from utilities import secrets,common

file_path = "application.cron.removeoldchanges.handler"

expected_delete_query = """
        delete from pathwaysdos.changes c where c.createdTimestamp < (%s)
        returning
        *
    """


# expected_service_query = """select uid, name, typeid, parentid
#             from services
#             where id = %s
#     """

# expected_parent_uid_query = """select ser.id as parentid, ser.uid as parentuid
#             from services as ser
#             where ser.id = (select parentid from services where id = %s);
#     """

# expected_region_name_query = """select s.uid, s.name,
#             (with recursive tree AS(
#             select s.id,s.uid,s.parentid,s.name, 1 AS lvl FROM services s where s.id = %s
#             union all
#             select s.id,s.uid,s.parentid,s.name, lvl+1 AS lvl
#             from services s
#             inner join tree t ON s.id = t.parentid)
#             select name from tree order by lvl desc limit 1) AS dosregion
#         from services s
#         where s.id = %s
#     """

@patch("psycopg2.connect")
@patch(f"{file_path}.cron_common.cron_cleanup")
@patch(f"{file_path}.database.execute_cron_query", return_value="" )
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
def test_handler_pass(mock_db_details, mock_update_query, mock_cleanup, mock_db_connect):
    """Test top level request calls downstream functions - success"""
    payload = {"id": "ABC", "time": "DEF"}
    handler.request(event=payload, context=None)
    mock_cleanup.assert_called_once()
    mock_db_details.assert_called_once()
    mock_update_query.assert_called_once()


def test_generate_delete_query():
    threshold_date=datetime.now()
    delete_query, data  = handler.generate_delete_query(threshold_date)
    assert delete_query == expected_delete_query

@patch("psycopg2.connect")
def test_log_deleted_changes(mock_db_connect):
    row_one = {"serviceid": 1,"service_name": "Mustang"}
    row_two = {"serviceid": 2,"service_name": "Mustang"}
    deleted_services = [row_one,row_two]
    handler.log_deleted_changes('mockenv', mock_db_connect,deleted_services)




#TODO  - will comeback to best method for this
@patch(f"{file_path}.getThresholdDate", return_value="2016, 8, 4, 12, 22, 44, 123456")
def test_getThresholdDate(mock_getThresholdDate):
    with patch('datetime.datetime') as date_mock:
        current_timestamp = date_mock.now().return_value
        threshold_in_days = 1
        threshold_date = current_timestamp - timedelta(days=threshold_in_days)
        threshold_date = threshold_date.strftime('%Y-%m-%d %H:%M:%S')
        returned_date = getThresholdDate(threshold_in_days)
        # assert returned_date == threshold_date
