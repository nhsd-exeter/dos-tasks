import os
import pytest
import requests
import json
from time import sleep
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from .. import message


@patch("requests.post", return_value="Success 200")
def test_send_success_slack_message(mock_post):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = datetime.utcnow()
    finish = start + timedelta(seconds=3)
    duration = "0:00:03"
    sleep(3)
    result = message.send_success_slack_message(mock_event, start)
    assert result == "Success 200"
    mock_post.assert_called_once_with("https://slackmockurl.com/", json.dumps({
        "attachments": [
            {
                "color": "#0def42",
                "blocks": [
                    {"type": "header", "text": {"type": "plain_text", "text": "Utilities HK Lambda"}},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": """Status: Success :woohoo:
Project: *uec-dos-tasks* | Environment: *mock_env* | Profile: *local*
Task: *utilities* | File: *mock_filename* | Bucket: *mock_bucket*
Start Time: *{start}* | Finish Time: *{finish}* | Duration: *{duration}*""".format(
                                start=start.strftime("%Y-%m-%d %H:%M:%S"),
                                finish=finish.strftime("%Y-%m-%d %H:%M:%S"),
                                duration=duration,
                            ),
                        },
                    },
                ],
            }
        ]
    }), headers={"Content-type": "application/json"})


@patch("requests.post", return_value="Success 200")
def test_send_failure_slack_message(mock_post):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = datetime.utcnow()
    finish = start + timedelta(seconds=1)
    duration = "0:00:01"
    sleep(1)
    result = message.send_failure_slack_message(mock_event, start)
    assert result == "Success 200"
    mock_post.assert_called_once_with("https://slackmockurl.com/", json.dumps({
        "attachments": [
            {
                "color": "#dc3d2a",
                "blocks": [
                    {"type": "header", "text": {"type": "plain_text", "text": "Utilities HK Lambda"}},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": """Status: Failure :fire:
Project: *uec-dos-tasks* | Environment: *mock_env* | Profile: *local*
Task: *utilities* | File: *mock_filename* | Bucket: *mock_bucket*
Start Time: *{start}* | Finish Time: *{finish}* | Duration: *{duration}*""".format(
                                start=start.strftime("%Y-%m-%d %H:%M:%S"),
                                finish=finish.strftime("%Y-%m-%d %H:%M:%S"),
                                duration=duration,
                            ),
                        },
                    },
                ],
            }
        ]
    }), headers={"Content-type": "application/json"})


@patch("requests.post", return_value="Success 200")
def test_send_slack_message(mock_post):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    start = datetime.utcnow()
    result = message.send_start_message(mock_event, start)
    assert result == "Success 200"
    mock_post.assert_called_once_with("https://slackmockurl.com/", json.dumps({
        "attachments": [
            {
                "color": "#ffa500",
                "blocks": [
                    {"type": "header", "text": {"type": "plain_text", "text": "Utilities HK Lambda"}},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": """Status: Job Starting :trex:
Project: *uec-dos-tasks* | Environment: *mock_env* | Profile: *local*
Task: *utilities* | File: *mock_filename* | Bucket: *mock_bucket*
Start Time: *{start}*""".format(
                                start=start.strftime("%Y-%m-%d %H:%M:%S"),
                            ),
                        },
                    },
                ],
            }
        ]
    }), headers={"Content-type": "application/json"})


def test_calculate_execution_time():
    start = datetime.utcnow()
    sleep(2)
    finish, duration = message.calculate_execution_time(start)
    assert finish == (start + timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")
    assert str(duration) == "0:00:02"
