from unittest import result
from unittest.mock import patch
from datetime import datetime, timedelta
from application.cron.removeoldchanges.handler import getThresholdDate
import pytest


from .. import handler

file_path = "application.cron.removeoldchanges.handler"

expected_delete_query = """
        delete from pathwaysdos.changes c where c.createdTimestamp < (%s)
        returning
        *
    """


@patch("psycopg2.connect")
@patch(f"{file_path}.cron_common.cron_cleanup")
@patch(f"{file_path}.database.execute_cron_delete_query", return_value="" )
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
def test_handler_pass(mock_db_details, mock_update_query, mock_cleanup, mock_db_connect):
    """Test top level request calls downstream functions - success"""
    payload = {"id": "ABC", "time": "DEF"}
    handler.request(event=payload, context=None)
    mock_cleanup.assert_called_once()
    mock_db_details.assert_called_once()
    mock_update_query.assert_called_once()


def test_generate_delete_query():
    current_timestamp = datetime.now()
    threshold_date = current_timestamp - timedelta(90)
    threshold_date = threshold_date.strftime("%Y-%m-%d %H:%M:%S")
    query, data  = handler.generate_delete_query(threshold_date)
    assert ''.join(query.split()) == ''.join(expected_delete_query.split())
    assert len(data) == 1
    assert data[0] == threshold_date

# @patch("psycopg2.connect")
# def test_log_deleted_changes(mock_db_connect):
#     row_one = {"serviceid": 1,"service_name": "Mustang"}
#     row_two = {"serviceid": 2,"service_name": "Mustang"}
#     deleted_services = [row_one,row_two]
#     handler.log_deleted_changes('mockenv', mock_db_connect,deleted_services)




#TODO  - will comeback to best method for this

def test_getThresholdDate():
        current_timestamp = datetime.now()
        threshold_in_days = 1
        threshold_date = current_timestamp - timedelta(days=threshold_in_days)
        threshold_date = threshold_date.strftime('%Y-%m-%d %H:%M:%S')
        returned_date = getThresholdDate(threshold_in_days)
        assert returned_date == threshold_date
