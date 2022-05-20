import boto3
import os
import base64
from botocore.exceptions import ClientError
from utilities import message

AWS_REGION = os.environ["AWS_REGION"]
secrets_client = boto3.client("secretsmanager", region_name=AWS_REGION)


class SECRETS:
    @staticmethod
    def get_secret_value(secret_store_name, event, start):
        try:
            response = secrets_client.get_secret_value(SecretId=secret_store_name)
        except ClientError as e:
            # logging error here
            message.send_failure_slack_message()
            if e.response["Error"]["Code"] == "DecryptionFailureException":
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response["Error"]["Code"] == "InternalServiceErrorException":
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response["Error"]["Code"] == "InvalidParameterException":
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response["Error"]["Code"] == "InvalidRequestException":
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response["Error"]["Code"] == "ResourceNotFoundException":
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
        except Exception as e:
            # logging error here
            message.send_failure_slack_message(event, start)
            raise e
        else:
            if "SecretString" in response:
                return response["SecretString"]
            else:
                return base64.b64decode(response["SecretBinary"])
