import os

import requests
from dotenv import load_dotenv

load_dotenv()

from slack_sdk import WebClient


def post_to_slack(report_header: str, diagnostics_str: str):
    slack_client = WebClient(os.environ["SLACK_BOT_TOKEN"])

    resp = slack_client.files_upload_v2(
        title=report_header,
        filename=report_header + ".md",
        content=diagnostics_str,
        channel=os.environ["SLACK_CHANNEL_ID"],
        initial_comment=" ".join(
            ["<@%s>" % uid for uid in os.environ["SLACK_USERS_TO_AT"].split(",")]
            if os.environ["SLACK_USERS_TO_AT"]
            else []
        ),
    )
    return f"https://app.slack.com/client/{resp['file']['user_team']}/{os.environ['SLACK_CHANNEL_ID']}"
