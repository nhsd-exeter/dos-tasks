import boto3
import json
# import os

secrets_client = boto3.client("secretsmanager")
lambda_client = boto3.client("lambda")


def request(event, context):
    print("Event: {}".format(event))
    process_event(event)


def process_event(event):
    filename = event["s3"]["object"]["key"]
    env = filename.split("/")[0]
    task = filename.split("/")[1].split("_")[1].split(".")[0]
    invoke_hk_lambda(task, filename, env)


def invoke_hk_lambda(task, filename, env):
    payload = {"filename": filename, "env": env}

    response = lambda_client.invoke(
        FunctionName="uec-dos-tasks-hk-{}-lambda".format(task),
        InvocationType="Event",
        Payload=json.dumps(payload),
        Qualifier="latest",
    )

    print("Response: {}".format(response))
