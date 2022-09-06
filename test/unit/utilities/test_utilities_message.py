import json
import datetime
from unittest.mock import patch
from .. import message

file_path = 'application.utilities.message'

@patch("requests.post", return_value="Success 200")
@patch(f"{file_path}.datetime", wraps=datetime.datetime)
# @patch(f"{file_path}.slack_summary_counts", return_value="""BLANK": 1, "CREATE": 2,"DELETE": 3, "ERROR":4,"UPDATE": 5""")
def test_send_success_slack_message(mock_datetime, mock_post):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_datetime.utcnow.return_value = datetime.datetime(2022, 4, 26, hour=19, minute=9, second=6)
    start = datetime.datetime(2022, 4, 26, hour=19, minute=4, second=40)
    finish = datetime.datetime(2022, 4, 26, hour=19, minute=9, second=6)
    duration = "0:04:26"
    mock_summary_dict = ""
    mock_summary_dict = {"BLANK": 4, "CREATE": 3,"DELETE": 2, "ERROR": 1,"UPDATE": 0}

    result = message.send_success_slack_message(mock_event, start, mock_summary_dict)
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
Summary: *updated:0, inserted:3, deleted:2, blank:4, errored:1*
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
@patch(f"{file_path}.datetime", wraps=datetime.datetime)
def test_send_failure_slack_message(mock_datetime, mock_post):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_datetime.utcnow.return_value = datetime.datetime(2022, 4, 26, hour=19, minute=9, second=6)
    start = datetime.datetime(2022, 4, 26, hour=19, minute=4, second=40)
    finish = datetime.datetime(2022, 4, 26, hour=19, minute=9, second=6)
    duration = "0:04:26"
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
Summary: *updated:0, inserted:0, deleted:0, blank:0, errored:0*
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
@patch(f"{file_path}.datetime", wraps=datetime.datetime)
def test_send_slack_message(mock_datetime, mock_post):
    mock_event = {"filename": "mock_filename", "env": "mock_env", "bucket": "mock_bucket"}
    mock_datetime.utcnow.return_value = datetime.datetime(2022, 4, 26, hour=19, minute=9, second=6)
    start = datetime.datetime(2022, 4, 26, hour=19, minute=9, second=6)
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


@patch(f"{file_path}.datetime", wraps=datetime.datetime)
def test_calculate_execution_time(mock_datetime):
    mock_datetime.utcnow.return_value = datetime.datetime(2022, 4, 26, hour=19, minute=9, second=6)
    start = datetime.datetime(2022, 4, 26, hour=19, minute=4, second=40)
    finish, duration = message.calculate_execution_time(start)
    assert finish == "2022-04-26 19:09:06"
    assert str(duration) == "0:04:26"
