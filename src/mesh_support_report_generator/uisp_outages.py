from datetime import datetime, timezone, timedelta
import json
import os

from dateutil import parser
from dotenv import load_dotenv
import requests
import mesh_support_report_generator.endpoints as endpoints
from mesh_support_report_generator.incident import Incident, IncidentType

load_dotenv()

IGNORE_OUTAGE_TOKEN = os.environ.get("IGNORE_OUTAGE_TOKEN")
UISP_IGNORE_SITE_IDS = os.environ.get("UISP_IGNORE_SITE_IDS", "").split(",")
LAST_N_DAYS_TO_REPORT = 7


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


def get_uisp_outage_lists():
    session = requests.Session()
    session.headers = {"x-auth-token": login(session)}
    outages = get_outages(session, 1000, 1)

    last_week = datetime.now(tz=timezone.utc) - timedelta(days=LAST_N_DAYS_TO_REPORT)
    new_outages = [
        outage
        for outage in outages["items"]
        if parser.parse(outage["startTimestamp"]) > last_week and outage["ongoing"]
    ]

    output_outages = []
    for outage in new_outages:
        incident = Incident(
            device_name=outage["device"]["name"],
            incident_type=IncidentType.OUTAGE,
            event_time=parser.parse(outage["startTimestamp"]),
        )

        device_details = get_device(session, outage["device"]["id"])
        notes = device_details["meta"]["note"]
        if notes and IGNORE_OUTAGE_TOKEN in device_details["meta"]["note"]:
            continue

        if outage["device"]["site"]["id"] in UISP_IGNORE_SITE_IDS:
            continue

        output_outages.append(incident)

    return output_outages
