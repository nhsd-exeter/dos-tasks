import os
import pytest
import json
from moto import mock_secretsmanager
from unittest.mock import patch
from botocore.exceptions import ClientError
import boto3

file_path = "application.utilities.secrets"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
secret_store = "top_secret_store"
start = "20220527"

@mock_secretsmanager
def test_get_json_secrets(aws_credentials):
    from ..secrets import SECRETS
    secretsmanager_client = boto3.client("secretsmanager")
    secret = {"username": "secret_username", "password": "secret_password"}
    secretsmanager_client.create_secret(Name=secret_store, SecretString=json.dumps(secret))
    response = SECRETS().get_secret_value(secret_store, mock_event, start)
    assert json.loads(response, strict=False) == secret


@mock_secretsmanager
def test_get_string_secrets(aws_credentials):
    from ..secrets import SECRETS
    secretsmanager_client = boto3.client("secretsmanager")
    secret = "string_secret"
    secretsmanager_client.create_secret(Name=secret_store, SecretString=secret)
    response = SECRETS().get_secret_value(secret_store, mock_event, start)
    assert response == secret


@patch(f"{file_path}.message.send_failure_slack_message")
@mock_secretsmanager
def test_get_secrets_returns_client_error(mock_send_failure_slack_message, aws_credentials):
    from ..secrets import SECRETS
    secretsmanager_client = boto3.client("secretsmanager")
    secret = {"username": "secret_username", "password": "secret_password"}
    secretsmanager_client.create_secret(Name="invalid_secret_name", SecretString=json.dumps(secret))
    with pytest.raises(ClientError) as assertion:
        response = SECRETS().get_secret_value(secret_store, mock_event, start)
    assert str(assertion.value) == "An error occurred (ResourceNotFoundException) when calling the GetSecretValue operation: Secrets Manager can't find the specified secret."
    mock_send_failure_slack_message.assert_called_once()
