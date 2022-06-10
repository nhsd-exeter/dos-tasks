import boto3
from botocore.exceptions import ClientError
from utilities import message, logger


class S3:
    def __init__(self):
        self.s3_client = boto3.client("s3")

    def get_object(self, bucket, filename, event, start):
        try:
            response = self.s3_client.get_object(
                Bucket=bucket,
                Key=filename,
            )
            file = response["Body"].read().decode("utf-8")
            return file
        except ClientError as e:
            logger.log_for_error("Error retrieving object from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            logger.log_for_error("Error retrieving object from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e

    def copy_object(self, bucket, file, event, start):
        try:
            response = self.s3_client.copy_object(
                Bucket=bucket,
                CopySource="{}/{}".format(bucket, file),
                Key="{}/archive/{}".format(file.split("/")[0], file.split("/")[1]),
            )
            return response
        except ClientError as e:
            logger.log_for_error("Error copying object to bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            logger.log_for_error("Error copying object to bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e

    def delete_object(self, bucket, filename, event, start):
        try:
            response = self.s3_client.delete_object(Bucket=bucket, Key=filename)
            return response
        except ClientError as e:
            logger.log_for_error("Error deleting object from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            logger.log_for_error("Error deleting object from bucket: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
