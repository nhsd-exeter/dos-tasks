import os
import pytest
import boto3
from moto import mock_secretsmanager
import mock
from .. import secrets


# @pytest.fixture
# @mock_secretsmanager
# def mock_secrets():
#     client = boto3.client("secretsmanager")
#     secret = {"Name": "top_secret_store", "SecretString": '{"test":"success"}'}
#     client.create_secret(**secret)

# @mock_secretsmanager
# def test_get_secrets():
#     secret_store = os.environ.get("SECRET_STORE")
#     event = "dummy_event"
#     start = "20220527"
#     secret = '{"test":"success"}'
#     response = secrets.SECRETS.get_secret_value(secret_store, event, start)
#     assert response == secret
