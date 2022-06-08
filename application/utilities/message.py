import os
from datetime import datetime
import requests
import json

slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
profile = os.environ.get("PROFILE")
task = os.environ.get("TASK")
headers = {"Content-type": "application/json"}

# Email Function (Include template CR for prod)
# Slack Function


def send_success_slack_message(event, start):
    env = event["env"]
    file = event["filename"]
    bucket = event["bucket"]
    finish, duration = calculate_execution_time(start)
    start = start.strftime("%Y-%m-%d %H:%M:%S")
    success_payload = {
        "attachments": [
            {
                "color": "#0def42",
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "{} HK Lambda".format(task.capitalize())},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": """Status: Success :woohoo:
Project: *uec-dos-tasks* | Environment: *{env}* | Profile: *{profile}*
Task: *{task}* | File: *{file}* | Bucket: *{bucket}*
Start Time: *{start}* | Finish Time: *{finish}* | Duration: *{duration}*""".format(
                                env=env,
                                profile=profile,
                                task=task,
                                file=file,
                                bucket=bucket,
                                start=start,
                                finish=finish,
                                duration=duration,
                            ),
                        },
                    },
                ],
            }
        ]
    }
    return requests.post(slack_webhook_url, json.dumps(success_payload), headers=headers)


def send_failure_slack_message(event, start):
    env = event["env"]
    file = event["filename"]
    bucket = event["bucket"]
    finish, duration = calculate_execution_time(start)
    start = start.strftime("%Y-%m-%d %H:%M:%S")
    failure_payload = {
        "attachments": [
            {
                "color": "#dc3d2a",
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "{} HK Lambda".format(task.capitalize())},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": """Status: Failure :fire:
Project: *uec-dos-tasks* | Environment: *{env}* | Profile: *{profile}*
Task: *{task}* | File: *{file}* | Bucket: *{bucket}*
Start Time: *{start}* | Finish Time: *{finish}* | Duration: *{duration}*""".format(
                                env=env,
                                profile=profile,
                                task=task,
                                file=file,
                                bucket=bucket,
                                start=start,
                                finish=finish,
                                duration=duration,
                            ),
                        },
                    },
                ],
            }
        ]
    }
    return requests.post(slack_webhook_url, json.dumps(failure_payload), headers=headers)


def send_start_message(event, start):
    env = event["env"]
    file = event["filename"]
    bucket = event["bucket"]
    start = start.strftime("%Y-%m-%d %H:%M:%S")
    start_payload = {
        "attachments": [
            {
                "color": "#ffa500",
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "{} HK Lambda".format(task.capitalize())},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": """Status: Job Starting :trex:
Project: *uec-dos-tasks* | Environment: *{env}* | Profile: *{profile}*
Task: *{task}* | File: *{file}* | Bucket: *{bucket}*
Start Time: *{start}*""".format(
                                env=env,
                                profile=profile,
                                task=task,
                                file=file,
                                bucket=bucket,
                                start=start,
                            ),
                        },
                    },
                ],
            }
        ]
    }
    return requests.post(slack_webhook_url, json.dumps(start_payload), headers=headers)


def calculate_execution_time(start):
    now = datetime.utcnow()
    finish = now.strftime("%Y-%m-%d %H:%M:%S")
    duration = str(now - start).split(".")[0]
    return finish, duration
