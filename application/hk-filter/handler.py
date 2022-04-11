import boto3
import json
import os

secrets_client = boto3.client("secretsmanager")
lambda_client = boto3.client("lambda")


def request(event, context):
    print("Event: {}".format(event))
    process_event(event)


def process_event(event):
    try:
        filename = event["Records"][0]["s3"]["object"]["key"]
        print("Filename: {}".format(filename))
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        if filename.split("/")[1] == "archive":
            print("Archived file...")
            return
        else:
            env = filename.split("/")[0]
            task = filename.split("/")[1].split("_")[1].split(".")[0]
    except Exception as e:
        print("Error Processing Event: {}".format(e))
    else:
        print("Invoking HK {} lambda function for {} environment".format(task, env))
        invoke_hk_lambda(task, filename, env, bucket)


def invoke_hk_lambda(task, filename, env, bucket):
    profile = os.environ.get("profile")
    payload = {"filename": filename, "env": env, "bucket": bucket}
    function = "uec-dos-tasks-{0}-hk-{1}-lambda".format(profile, task)

    try:
        response = lambda_client.invoke(FunctionName=function, InvocationType="Event", Payload=json.dumps(payload))

        print("Response: {}".format(response))
    except Exception as e:
        print("Error Invoking Lambda: {}".format(e))
