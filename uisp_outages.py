from datetime import datetime, timezone, timedelta
import json
import os

import pytz as pytz
from dotenv import load_dotenv
import requests
import endpoints

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


def get_uisp_outage_lists():
    session = requests.Session()
    session.headers = {"x-auth-token": login(session)}
    outages = get_outages(session, 1000, 1, datetime.now())

    yesterday = datetime.now(tz=timezone.utc) - timedelta(hours=24.1)
    last_week = datetime.now(tz=timezone.utc) - timedelta(days=7)
    new_outages = [
        outage
        for outage in outages["items"]
        if datetime.fromisoformat(outage["startTimestamp"]) > yesterday
        and outage["ongoing"]
    ]

    recent_outages = [
        outage
        for outage in outages["items"]
        if datetime.fromisoformat(outage["startTimestamp"]) > last_week
        and outage["id"] not in [out["id"] for out in new_outages]
    ]

    print("UISP - Currently In Outage (new last 24 hours)")
    for outage in new_outages:
        print(outage["device"]["name"])
    if len(new_outages) == 0:
        print("-- None --")

    print("\n\nUISP - Other Recent Outages (last 7 days)")
    for outage in recent_outages:
        if outage["ongoing"]:
            outage_time = (
                datetime.fromisoformat(outage["startTimestamp"])
                .astimezone(tz=pytz.timezone("US/Eastern"))
                .strftime("%Y-%m-%d @ %H:%M")
            )
            outage_status = f"OFFLINE since {outage_time}"
        else:
            recovery_time = (
                datetime.fromisoformat(outage["endTimestamp"])
                .astimezone(tz=pytz.timezone("US/Eastern"))
                .strftime("%Y-%m-%d @ %H:%M")
            )
            outage_status = f"Reconnected {recovery_time}"
        print(f"{outage['device']['name']}  {outage_status}")
