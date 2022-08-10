import pytest
from moto import mock_s3
from unittest.mock import patch
from botocore.exceptions import ClientError
import boto3
import io
import zipfile

file_path = "application.utilities.s3"
mock_body = """1800,"Mock Create Role","CREATE"
1800,"Mock Update Role","UPDATE"
1800,"Mock Update Role","DELETE"
"""
mock_bucket = "mock_bucket"
mock_filename = "mock_env/mock_file.csv"
mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
start = "20220527"
mock_zip_filename = "mock_env/mock_file.zip"
sample_bundle_file_name = "test-files/19.0.zip"


@mock_s3
def test_get_compressed_object_success(aws_credentials):
    from ..s3 import S3
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=mock_bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    s3_client.upload_file(Filename=sample_bundle_file_name, Bucket=mock_bucket, Key=mock_zip_filename)
    response_body = S3().get_compressed_object(mock_bucket, mock_zip_filename, mock_event, start)
    # print (response_body)
    # assert True == False
    # contents = response["Body"].read()
    # assert zipfile.is_zipfile(response_body)
    input_zip = zipfile.ZipFile(io.BytesIO(response_body))

    for name in input_zip.namelist():
        # print("=========== " + name + "============")
        scenario_file = input_zip.read(name).decode("utf-8")
        # print(scenario_file)
        # TODO
    assert True == True


@patch(f"{file_path}.message.send_failure_slack_message")
@mock_s3
def test_get_compressed_object_raises_client_error(mock_send_failure_slack_message, aws_credentials):
    from ..s3 import S3
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=mock_bucket, CreateBucketConfiguration={'LocationConstraint': 'antarctica'})
    with pytest.raises(ClientError) as assertion:
        response = S3().get_compressed_object(mock_bucket, mock_filename, mock_event, start)
    assert str(assertion.value) == "An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist."
    mock_send_failure_slack_message.assert_called_once_with(mock_event, start)



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
