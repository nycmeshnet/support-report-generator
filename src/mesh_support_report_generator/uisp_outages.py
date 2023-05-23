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
        if parser.parse(outage["startTimestamp"]) > last_week and outage["inProgress"]
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
            notes = (
                device_details["meta"]["note"]
                .replace("\n", " ")
                .replace(IGNORE_OUTAGE_TOKEN, "")
                .strip()
            )
            incident.ignored = True
            incident.site_name = notes if len(notes) > 0 else "Ignore token detected"
            incident.event_time = None
        elif outage["device"]["site"]["id"] in UISP_IGNORE_SITE_IDS:
            incident.ignored = True
            incident.site_name = outage["device"]["site"]["name"]
            incident.event_time = None

        output_outages.append(incident)

    return (
        [incident for incident in output_outages if not incident.ignored],
        [incident for incident in output_outages if incident.ignored],
    )
