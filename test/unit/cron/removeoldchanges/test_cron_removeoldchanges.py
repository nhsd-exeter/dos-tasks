from unittest import result
from unittest.mock import patch
from datetime import datetime, timedelta
from application.cron.removeoldchanges.handler import getThresholdDate
import pytest


from .. import handler

file_path = "application.cron.removeoldchanges.handler"

expected_delete_query = """delete from pathwaysdos.changes c where c.createdTimestamp < %s
        returning
        *
    """

expected_delete_count_query = """select count(*) removed_count from pathwaysdos.changes c where c.createdTimestamp < %s
    """

@patch("psycopg2.connect")
@patch(f"{file_path}.cron_common.cron_cleanup")
@patch(f"{file_path}.database.execute_cron_delete_query", return_value="" )
@patch(f"{file_path}.database.execute_cron_query", return_value={})
@patch(f"{file_path}.log_removed_changes", return_value={})
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
def test_handler_pass(mock_db_details,mock_log_removed_changes,mock_delete_count_query, mock_delete_query, mock_cleanup, mock_db_connect):
    """Test top level request calls downstream functions - success"""
    payload = {"id": "A", "time": "D"}
    handler.request(event=payload, context=None)
    mock_cleanup.assert_called_once()
    mock_db_details.assert_called_once()
    mock_delete_query.assert_called_once()

def test_generate_delete_query():
    current_timestamp = datetime.now()
    threshold_date = current_timestamp - timedelta(90)
    threshold_date = threshold_date.strftime("%Y-%m-%d %H:%M:%S")
    query, data  = handler.generate_delete_query(threshold_date)
    assert len(data) == 1
    assert data[0] == threshold_date
    assert ''.join(query.split()) == ''.join(expected_delete_query.split())


def test_generate_delete_count_query():
    current_timestamp = datetime.now()
    threshold_date = current_timestamp - timedelta(90)
    threshold_date = threshold_date.strftime("%Y-%m-%d %H:%M:%S")
    query, data = handler.generate_delete_count_query(threshold_date)
    assert ''.join(query.split()) == ''.join(expected_delete_count_query.split())
    assert query == expected_delete_count_query
    assert len(data) == 1
    assert data[0] == threshold_date

@patch("psycopg2.connect")
@patch(f"{file_path}.get_delete_count", return_value= [{"removed_count": 1}])
def test_get_log_data(mock_get_delete_count,mock_db_connect):
# def test_get_log_data(mock_db_connect):
    handler.get_log_data('mockenv', mock_db_connect,mock_get_delete_count)
    # assert log_info == {"operation": "delete", "removed_count" : 1}
    # mock_get_delete_count.assert_called_once()


@patch("psycopg2.connect")
def test_get_delete_count(mock_db_connect):
    current_timestamp = datetime.now()
    threshold_date = current_timestamp - timedelta(90)
    threshold_date = threshold_date.strftime("%Y-%m-%d %H:%M:%S")
    actual_return = handler.get_delete_count('mockenv', mock_db_connect, threshold_date)
    expected_return = {"removed_count" : 1}
    # assert expected_return == actual_return



#TODO  - will comeback to best method for this

def test_getThresholdDate():
        current_timestamp = datetime.now()
        threshold_in_days = 1
        threshold_date = current_timestamp - timedelta(days=threshold_in_days)
        threshold_date = threshold_date.strftime('%Y-%m-%d %H:%M:%S')
        returned_date = getThresholdDate(threshold_in_days)
        assert returned_date == threshold_date
