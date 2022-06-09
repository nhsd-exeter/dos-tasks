from utilities.logger import log_for_audit
from utilities.message import send_start_message, send_success_slack_message, send_failure_slack_message
from datetime import datetime
import boto3
import json
import os

lambda_client = boto3.client("lambda")


def request(event, context):
    start = datetime.utcnow()
    print("Event: {}".format(event))
    if "archive" not in event["Records"][0]["s3"]["object"]["key"]:
        send_start_message(
            {
                "filename": event["Records"][0]["s3"]["object"]["key"],
                "env": event["Records"][0]["s3"]["object"]["key"].split("/")[0],
                "bucket": event["Records"][0]["s3"]["bucket"]["name"],
            },
            start,
        )
    process_event(event, start)
    return "HK task filtered successfully"


def process_event(event, start):
    try:
        filename = event["Records"][0]["s3"]["object"]["key"]
        if "archive" in filename:
            print("Archived file...")
            return
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        env = filename.split("/")[0]
        task = filename.split("/")[1].split("_")[1].split(".")[0]
        if not filename.endswith(".csv"):
            log_for_audit("Incorrect file extension, found: {}, expected: '.csv'".format(filename.split(".")[1]))
            raise IOError("Incorrect file extension, found: {}, expected: '.csv'".format(filename.split(".")[1]))
    except Exception as e:
        print("Error Processing Event: {}".format(e))
        send_failure_slack_message({"filename": filename, "env": env, "bucket": bucket}, start)
        raise e
    else:
        print("Invoking HK {} lambda function for {} environment".format(task, env))
        invoke_hk_lambda(task, filename, env, bucket, start)
    return "HK Filter Event processed successfully"


def invoke_hk_lambda(task, filename, env, bucket, start):
    profile = os.environ.get("PROFILE")
    # version = os.environ.get(task)
    payload = {"filename": filename, "env": env, "bucket": bucket}
    function = "uec-dos-tasks-{0}-hk-{1}-lambda".format(profile, task)
    print("Profile: {}".format(profile))
    print("Payload: {}".format(payload))
    print("Function: {}".format(function))
    try:
        response = lambda_client.invoke(FunctionName=function, InvocationType="Event", Payload=json.dumps(payload))
        print("Response: {}".format(response))
        send_success_slack_message(payload, start)
        return "HK {} invoked successfully".format(task)
    except Exception as e:
        print("Error Invoking Lambda: {}".format(e))
        send_failure_slack_message(payload, start)
        raise e
