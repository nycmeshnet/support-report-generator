import sys
from datetime import datetime, timezone, timedelta
import json
import os

from dateutil import parser
import pytz as pytz
from dotenv import load_dotenv
import requests
import mesh_support_report_generator.endpoints as endpoints

load_dotenv()

IGNORE_OUTAGE_TOKEN = os.environ["IGNORE_OUTAGE_TOKEN"]


def login(session: requests.Session):
    return session.post(
        endpoints.UISP_LOGIN,
        json={
            "username": os.environ["UISP_USERNAME"],
            "password": os.environ["UISP_PASSWORD"],
        },
        verify=False,
    ).headers["x-auth-token"]


def get_outages(session: requests.Session, count: int, page: int):
    return json.loads(
        session.get(
            endpoints.UISP_OUTAGES,
            params={
                "count": count,
                "page": page,
                "period": 1000 * 60 * 60 * 24,
            },
            verify=False,
        ).content.decode("UTF8")
    )


def get_device(session: requests.Session, device_id: str):
    return json.loads(
        session.get(
            endpoints.UISP_DEVICE_DETAILS + device_id,
            verify=False,
        ).content.decode("UTF8")
    )


def get_uisp_outage_lists(stream=sys.stdout):
    session = requests.Session()
    session.headers = {"x-auth-token": login(session)}
    outages = get_outages(session, 1000, 1)

    yesterday = datetime.now(tz=timezone.utc) - timedelta(hours=24.1)
    last_week = datetime.now(tz=timezone.utc) - timedelta(days=7)
    new_outages = [
        outage
        for outage in outages["items"]
        if parser.parse(outage["startTimestamp"]) > last_week and outage["ongoing"]
    ]

    not_ignored_outages = []
    for outage in new_outages:
        device_details = get_device(session, outage["device"]["id"])
        notes = device_details["meta"]["note"]
        if not notes or IGNORE_OUTAGE_TOKEN not in device_details["meta"]["note"]:
            not_ignored_outages.append(outage)

    outages_to_print = not_ignored_outages

    print("UISP - Currently In Outage (new last 7 days)", file=stream)
    for outage in outages_to_print:
        outage_time = (
            parser.parse(outage["startTimestamp"])
            .astimezone(tz=pytz.timezone("US/Eastern"))
            .strftime("%Y-%m-%d @ %H:%M")
        )
        outage_status = f"(offline since {outage_time})"
        print(f'{outage["device"]["name"]} {outage_status}', file=stream)
    if len(outages_to_print) == 0:
        print("-- None --", file=stream)
