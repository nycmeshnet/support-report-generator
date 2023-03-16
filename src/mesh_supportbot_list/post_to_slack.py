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
        channels=os.environ["SLACK_SUPPORT_CHANNEL_ID"],
        initial_comment=" ".join(
            ["<@%s>" % uid for uid in os.environ["SLACK_USERS_TO_AT"].split(",")]
        ),
    )
