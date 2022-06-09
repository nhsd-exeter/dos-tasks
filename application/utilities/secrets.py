import boto3
import base64
from botocore.exceptions import ClientError
from utilities import message, logger


class SECRETS:
    def __init__(self):
        self.secrets_client = boto3.client("secretsmanager")

    def get_secret_value(self, secret_store_name, event, start):
        try:
            print(secret_store_name)
            response = self.secrets_client.get_secret_value(SecretId=secret_store_name)
        except ClientError as e:
            logger.log_for_error("Error retrieving secrets: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        except Exception as e:
            logger.log_for_error("Error retrieving secrets: {}".format(e))
            message.send_failure_slack_message(event, start)
            raise e
        else:
            if "SecretString" in response:
                return response["SecretString"]
            else:
                return base64.b64decode(response["SecretBinary"])
