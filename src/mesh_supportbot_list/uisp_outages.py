import sys
from datetime import datetime, timezone, timedelta
import json
import os

from dateutil import parser
import pytz as pytz
from dotenv import load_dotenv
import requests
import mesh_supportbot_list.endpoints as endpoints

load_dotenv()


def login(session: requests.Session):
    return session.post(
        endpoints.UISP_LOGIN,
        json={
            "username": os.environ["UISP_USERNAME"],
            "password": os.environ["UISP_PASSWORD"],
        },
        verify=False,
    ).headers["x-auth-token"]


def get_outages(session: requests.Session, count: int, page: int, start: datetime):
    return json.loads(
        session.get(
            endpoints.UISP_OUTAGES,
            params={
                "count": count,
                "page": page,
                "period": 1000 * 60 * 60 * 24,
                # "start": int(start.timestamp()),
            },
            verify=False,
        ).content.decode("UTF8")
    )


def get_uisp_outage_lists(stream=sys.stdout):
    session = requests.Session()
    session.headers = {"x-auth-token": login(session)}
    outages = get_outages(session, 1000, 1, datetime.now())

    yesterday = datetime.now(tz=timezone.utc) - timedelta(hours=24.1)
    last_week = datetime.now(tz=timezone.utc) - timedelta(days=7)
    new_outages = [
        outage
        for outage in outages["items"]
        if parser.parse(outage["startTimestamp"]) > last_week and outage["ongoing"]
    ]

    print("UISP - Currently In Outage (new last 7 days)", file=stream)
    for outage in new_outages:
        outage_time = (
            parser.parse(outage["startTimestamp"])
            .astimezone(tz=pytz.timezone("US/Eastern"))
            .strftime("%Y-%m-%d @ %H:%M")
        )
        outage_status = f"(offline since {outage_time})"
        print(f'{outage["device"]["name"]} {outage_status}', file=stream)
    if len(new_outages) == 0:
        print("-- None --", file=stream)
