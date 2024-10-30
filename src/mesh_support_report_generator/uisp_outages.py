import json
import os
from datetime import datetime, timedelta, timezone

import requests
from dateutil import parser
from dotenv import load_dotenv

import mesh_support_report_generator.endpoints as endpoints
from mesh_support_report_generator.incident import Incident, IncidentType
from urllib3.exceptions import InsecureRequestWarning

load_dotenv()

IGNORE_OUTAGE_TOKEN = os.environ.get("IGNORE_OUTAGE_TOKEN")
UISP_IGNORE_SITE_IDS = os.environ.get("UISP_IGNORE_SITE_IDS", "").split(",")
LAST_N_DAYS_TO_REPORT = 7


def login(session: requests.Session):
    # Suppress the 'Unverified HTTPS request is being made to host' log spam
    # because the POST is made with verify=False
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    return session.post(
        endpoints.UISP_LOGIN,
        json={
            "username": os.environ["UISP_USERNAME"],
            "password": os.environ["UISP_PASSWORD"],
        },
        verify=False,
    ).headers["x-auth-token"]


def get_all_devices(session: requests.Session):
    return json.loads(
        session.get(
            endpoints.UISP_DEVICES,
            verify=False,
        ).content.decode("UTF8")
    )


def get_uisp_outage_lists():
    session = requests.Session()
    session.headers = {"x-auth-token": login(session)}
    devices = get_all_devices(session)

    last_week = datetime.now(tz=timezone.utc) - timedelta(days=LAST_N_DAYS_TO_REPORT)
    outage_devices = [
        device
        for device in devices
        if device["overview"]["status"] != "active"
        and device["identification"]["type"] != "onu"  # These get handled separately
        and parser.parse(device["overview"]["lastSeen"]) > last_week
    ]

    output_outages = []
    for device in outage_devices:
        incident = Incident(
            device_name=device["identification"]["name"],
            incident_type=IncidentType.OUTAGE,
            event_time=parser.parse(device["overview"]["lastSeen"]),
        )

        notes = device["meta"]["note"]
        site_id = (
            device["identification"]["site"]["id"]
            if device["identification"]["site"]
            else None
        )
        if notes and IGNORE_OUTAGE_TOKEN in device["meta"]["note"]:
            notes = (
                device["meta"]["note"]
                .replace("\n", " ")
                .replace(IGNORE_OUTAGE_TOKEN, "")
                .strip()
            )
            incident.ignored = True
            incident.site_name = notes if len(notes) > 0 else "Ignore token detected"
            incident.event_time = None
        elif site_id in UISP_IGNORE_SITE_IDS:
            incident.ignored = True
            incident.site_name = device["identification"]["site"]["name"]
            incident.event_time = None
        elif device["meta"]["maintenance"]:
            incident.ignored = True
            incident.event_time = None
            incident.site_name = "maintenance mode"

        output_outages.append(incident)

    return (
        sorted(
            [incident for incident in output_outages if not incident.ignored],
            key=lambda x: x.event_time,
            reverse=True,
        ),
        [incident for incident in output_outages if incident.ignored],
    )
