from unittest.mock import Mock, patch
import psycopg2
import pytest
from .. import cron_common

@patch("psycopg2.connect")
def test_cron_cleanup(mock_db_connect):
    mock_db_connect.close.return_value = "Closed connection"
    result = cron_common.cron_cleanup('mockenv',mock_db_connect)
    mock_db_connect.close.assert_called_once()
    assert result == "Cleanup Successful"
