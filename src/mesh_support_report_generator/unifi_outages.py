import json
import os
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

import mesh_support_report_generator.endpoints as endpoints
from mesh_support_report_generator.incident import Incident, IncidentType
from urllib3.exceptions import InsecureRequestWarning

load_dotenv()

LAST_N_DAYS_TO_REPORT = 7


def login(session: requests.Session):
    # Suppress the 'Unverified HTTPS request is being made to host' log spam
    # because the POST is made with verify=False
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    return session.post(
        endpoints.UNIFI_LOGIN,
        json={
            "username": os.environ["UNIFI_USERNAME"],
            "password": os.environ["UNIFI_PASSWORD"],
        },
        verify=False,
    )


def list_sites(session: requests.Session):
    return json.loads(
        session.get(
            endpoints.UNIFI_LIST_SITES,
            verify=False,
        ).content.decode("UTF8")
    )["data"]


def get_devices(session: requests.Session, site_id: str):
    return json.loads(
        session.get(
            endpoints.UNIFI_LIST_DEVICES % site_id,
            verify=False,
        ).content.decode("UTF8")
    )["data"]


def get_unifi_outage_lists():
    session = requests.Session()
    login(session)
    sites = [{"name": site["desc"], "id": site["name"]} for site in list_sites(session)]
    devices_full_data = []
    for site in sites:
        site_devices = [
            {"site": site["name"], **device}
            for device in get_devices(session, site["id"])
        ]
        devices_full_data.extend(site_devices)

    devices_simplified = [
        {
            "id": device["_id"],
            "site": device["site"],
            "name": device.get("name", device["mac"]),
            "in_outage": device["state"] == 0,
            "most_recent_connect_time": (
                datetime.fromtimestamp(
                    device["start_connected_millis"] / 1000, timezone.utc
                )
                if device["state"] == 1
                else None
            ),
            "most_recent_disconnect_time": datetime.fromtimestamp(
                device["start_disconnected_millis"] / 1000, timezone.utc
            ),
        }
        for device in devices_full_data
        if "_id" in device
    ]

    last_week = datetime.now(tz=timezone.utc) - timedelta(days=LAST_N_DAYS_TO_REPORT)

    return [
        Incident(
            incident_type=IncidentType.OUTAGE,
            device_name=device["name"],
            event_time=device["most_recent_disconnect_time"],
            site_name=device["site"],
        )
        for device in devices_simplified
        if device["in_outage"] and device["most_recent_disconnect_time"] > last_week
    ]
