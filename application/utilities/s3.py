import boto3
from botocore.exceptions import ClientError
from utilities import message, logging

s3_client = boto3.client("s3")
s3_resource = boto3.resource("s3")


class S3:
    @staticmethod
    def download_file(bucket, filename, event, start):
        download_location = "/tmp/{}".format(filename)
        try:
            s3_resource.meta.client.download_file(bucket, filename, download_location)
            return download_location
        except Exception as e:
            logging.log_for_error("Error downloading file from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e

    @staticmethod
    def upload_file(bucket, file, event, start):
        upload_location = "{}/archive/{}".format(file.split("/")[0], file.split("/")[1])
        try:
            s3_resource.meta.client.upload_file(file, bucket, upload_location)
            return upload_location
        except Exception as e:
            logging.log_for_error("Error uploading file to bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e

    @staticmethod
    def get_object(bucket, filename, event, start):
        try:
            response = s3_client.get_object(
                Bucket=bucket,
                Key=filename,
            )
            file = response["Body"].read().decode("utf-8")
            return file
        except ClientError as e:
            logging.log_for_error("Error retrieving object from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            logging.log_for_error("Error retrieving object from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e

    @staticmethod
    def put_object(bucket, file, event, start):
        upload_location = "{}/archive/{}".format(file.split("/")[0], file.split("/")[1])
        try:
            response = s3_client.put_object(Bucket=bucket, Key=upload_location, Body=file)
            return response
        except ClientError as e:
            logging.log_for_error("Error placing object in bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            logging.log_for_error("Error placing object in bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e

    @staticmethod
    def copy_object(bucket, file, event, start):
        try:
            response = s3_client.copy_object(
                Bucket=bucket, CopySource="{}/{}".format(bucket, file), Key="{}/archive/{}".format(file.split("/")[0], file.split("/")[1])
            )
            return response
        except ClientError as e:
            logging.log_for_error("Error copying object to bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            logging.log_for_error("Error copying object to bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e

    @staticmethod
    def delete_object(bucket, filename, event, start):
        try:
            response = s3_client.delete_object(Bucket=bucket, Key=filename)
            return response
        except ClientError as e:
            logging.log_for_error("Error deleting object from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            logging.log_for_error("Error deleting object from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
