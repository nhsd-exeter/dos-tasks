import pytest
from moto import mock_s3
from unittest.mock import patch
from botocore.exceptions import ClientError
import boto3

file_path = "application.utilities.s3"
mock_body = """1800,"Mock Create Role","CREATE"
1800,"Mock Update Role","UPDATE"
1800,"Mock Update Role","DELETE"
"""
mock_bucket = "mock_bucket"
mock_filename = "mock_env/mock_file.csv"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
start = "20220527"

@mock_s3
def test_get_object_success(aws_credentials):
    from ..s3 import S3
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=mock_bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    s3_client.put_object(Bucket=mock_bucket, Key=mock_filename, Body=mock_body)
    response = S3().get_object(mock_bucket, mock_filename, mock_event, start)
    assert response == mock_body


@patch(f"{file_path}.message.send_failure_slack_message")
@mock_s3
def test_get_object_raises_client_error(mock_send_failure_slack_message, aws_credentials):
    from ..s3 import S3
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=mock_bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    with pytest.raises(ClientError) as assertion:
        response = S3().get_object(mock_bucket, mock_filename, mock_event, start)
    assert str(assertion.value) == "An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist."
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)


@mock_s3
def test_copy_object_success(aws_credentials):
    from ..s3 import S3
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=mock_bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    s3_client.put_object(Bucket=mock_bucket, Key=mock_filename, Body=mock_body)
    s3_object = S3()
    copy_response = s3_object.copy_object(mock_bucket, mock_filename, mock_event, start)
    get_response = s3_object.get_object(mock_bucket, "mock_env/archive/mock_file.csv", mock_event, start)
    assert copy_response["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert get_response == mock_body


@patch(f"{file_path}.message.send_failure_slack_message")
@mock_s3
def test_copy_object_raises_client_error(mock_send_failure_slack_message, aws_credentials):
    from ..s3 import S3
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=mock_bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    with pytest.raises(ClientError) as assertion:
        response = S3().copy_object(mock_bucket, mock_filename, mock_event, start)
    assert str(assertion.value) == "An error occurred (NoSuchKey) when calling the CopyObject operation: The specified key does not exist."
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)


@patch(f"{file_path}.message.send_failure_slack_message")
@mock_s3
def test_delete_object_success(mock_send_failure_slack_message, aws_credentials):
    from ..s3 import S3
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=mock_bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    s3_client.put_object(Bucket=mock_bucket, Key=mock_filename, Body=mock_body)
    s3_object = S3()
    delete_response = s3_object.delete_object(mock_bucket, mock_filename, mock_event, start)
    print(delete_response)
    assert delete_response["ResponseMetadata"]["HTTPStatusCode"] == 204
    with pytest.raises(ClientError) as assertion:
        get_response = s3_object.get_object(mock_bucket, mock_filename, mock_event, start)
    assert str(assertion.value) == "An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist."
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)



@patch(f"{file_path}.message.send_failure_slack_message")
@mock_s3
def test_delete_object_raises_client_error(mock_send_failure_slack_message, aws_credentials):
    from ..s3 import S3
    s3_client = boto3.client("s3")
    # s3_client.create_bucket(Bucket=mock_bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    with pytest.raises(ClientError) as assertion:
        response = S3().delete_object(mock_bucket, mock_filename, mock_event, start)
    assert str(assertion.value) == "An error occurred (NoSuchBucket) when calling the DeleteObject operation: The specified bucket does not exist"
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)
