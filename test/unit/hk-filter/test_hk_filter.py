import pytest
import boto3
from datetime import datetime
from moto import s3
from .. import handler


def test_incorrect_file_extension_returns_error():
    start = datetime.utcnow()
    mock_event = {'Records': [{'s3': {'bucket': {'name': 'uec-dos-tasks-mock-bucket'}, 'object': {'key': 'unittest/DPTS-001_referralroles.py'}}}]}
    with pytest.raises(IOError) as assertion:
        error_message = "Incorrect file extension, found: .py, expected: '.csv'"
        handler.process_event(mock_event, start)
        assert str(assertion.value) == error_message
