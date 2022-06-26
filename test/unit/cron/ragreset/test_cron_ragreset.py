from unittest.mock import patch
# import pytest
# import string
# import psycopg2

from .. import handler
# from utilities import secrets,common

file_path = "application.cron.ragreset.handler"


@patch("psycopg2.connect")
@patch(f"{file_path}.common.cron_cleanup")
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
def test_handler_pass(mock_db_details, mock_cleanup, mock_db_connect):
    """Test top level request calls downstream functions - success"""
    payload = {"id": "ABC", "time": "DEF"}
    handler.request(event=payload, context=None)
    mock_cleanup.assert_called_once()
    mock_db_details.assert_called_once
