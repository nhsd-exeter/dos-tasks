import pytest
import boto3
from moto import mock_secretsmanager
import mock


# @mock_secretsmanager
# @mock.patch.dict()
# def test_get_secrets():
#     assert response == secret
