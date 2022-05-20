import boto3
import os
from botocore.exceptions import ClientError
from utilities import message

AWS_REGION = os.environ["AWS_REGION"]
rds_client = boto3.client("rds", region_name=AWS_REGION)


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
