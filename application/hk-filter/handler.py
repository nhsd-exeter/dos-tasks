from utilities.logging import log_for_audit
from utilities import message
from datetime import datetime
import boto3
import json
import os

lambda_client = boto3.client("lambda")
start = datetime.utcnow()


def request(event, context):
    print("Event: {}".format(event))
    if "archive" not in event["Records"][0]["s3"]["object"]["key"]:
        message.send_start_message(
            {
                "filename": event["Records"][0]["s3"]["object"]["key"],
                "env": event["Records"][0]["s3"]["object"]["key"].split("/")[0],
                "bucket": event["Records"][0]["s3"]["bucket"]["name"],
            },
            start,
        )
    process_event(event)


def process_event(event):
    try:
        filename = event["Records"][0]["s3"]["object"]["key"]
        if not filename.endswith(".csv"):
            log_for_audit("Incorrect file extension, found: {}, expected: '.csv'".format(filename.split(".")[1]))
            raise UnicodeDecodeError(
                "Incorrect file extension, found: {}, expected: '.csv'".format(filename.split(".")[1])
            )
        print("Filename: {}".format(filename))
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        if "archive" in filename:
            print("Archived file...")
            return
        else:
            env = filename.split("/")[0]
            task = filename.split("/")[1].split("_")[1].split(".")[0]
    except Exception as e:
        print("Error Processing Event: {}".format(e))
        message.send_failure_slack_message({"filename": filename, "env": env, "bucket": bucket}, start)
        raise e
    else:
        print("Invoking HK {} lambda function for {} environment".format(task, env))
        invoke_hk_lambda(task, filename, env, bucket)


def invoke_hk_lambda(task, filename, env, bucket):
    profile = os.environ.get("PROFILE")
    # version = os.environ.get(task)
    payload = {"filename": filename, "env": env, "bucket": bucket}
    function = "uec-dos-tasks-{0}-hk-{1}-lambda".format(profile, task)

    try:
        response = lambda_client.invoke(FunctionName=function, InvocationType="Event", Payload=json.dumps(payload))
        print("Response: {}".format(response))
        message.send_success_slack_message(payload, start)
    except Exception as e:
        print("Error Invoking Lambda: {}".format(e))
        message.send_failure_slack_message(payload, start)
        raise e
