import boto3
from botocore.exceptions import ClientError
from utilities import message

rds_client = boto3.client("rds")


class RDS:
    @staticmethod
    def describe_db_instance(db_instance_identifier, event, start):
        try:
            response = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)
            return response
        except ClientError as e:
            # logging error here
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            # logging error here
            message.send_failure_slack_message(event, start)
            raise e
