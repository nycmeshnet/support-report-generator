import json
import os

from dotenv import load_dotenv
import requests
import mesh_support_report_generator.endpoints as endpoints
from mesh_support_report_generator.incident import Incident, IncidentType

load_dotenv()

IGNORE_OUTAGE_TOKEN = os.environ["IGNORE_OUTAGE_TOKEN"]

MIN_RX_POWER = -28
MIN_EXPERIENCE = 100


def login(session: requests.Session, ufiber_base_url: str):
    return session.post(
        ufiber_base_url + endpoints.UFIBER_LOGIN_SUFFIX,
        json={
            "username": os.environ["UFIBER_USERNAME"],
            "password": os.environ["UFIBER_PASSWORD"],
        },
        verify=False,
    ).headers["x-auth-token"]


def get_devices(session: requests.Session, ufiber_base_url: str):
    return json.loads(
        session.get(
            ufiber_base_url + endpoints.UFIBER_LIST_DEVICES_SUFFIX,
            verify=False,
        ).content.decode("UTF8")
    )


def get_device_details(session: requests.Session, ufiber_base_url: str, device_id: str):
    return json.loads(
        session.get(
            ufiber_base_url + endpoints.UFIBER_DESCRIBE_DEVICE_SUFFIX % device_id,
            verify=False,
        ).content.decode("UTF8")
    )


def create_incident(
    device: dict,
    incident_type: IncidentType,
    session: requests.Session,
    ufiber_endpoint: str,
):
    device_details = get_device_details(session, ufiber_endpoint, device["serial"])
    device_notes = device_details["notes"]
    if not device_notes or IGNORE_OUTAGE_TOKEN not in device_notes:
        if incident_type == IncidentType.OUTAGE:
            return Incident(
                device_name=device_details["name"],
                incident_type=IncidentType.OUTAGE,
            )
        elif incident_type == IncidentType.POOR_EXPERIENCE:
            return Incident(
                device_name=device_details["name"],
                incident_type=IncidentType.POOR_EXPERIENCE,
                metric_value=device.get("experience", "N/A"),
            )
        elif incident_type == IncidentType.POOR_SIGNAL:
            return Incident(
                device_name=device_details["name"],
                incident_type=IncidentType.POOR_SIGNAL,
                metric_value=device["rxPower"],
            )

    return None


def get_ufiber_outage_lists(ufiber_endpoint):
    incidents = []

    session = requests.Session()
    session.headers = {"x-auth-token": login(session, ufiber_endpoint)}
    devices = get_devices(session, ufiber_endpoint)

    for device in devices:
        if not device["connected"]:
            incidents.append(
                create_incident(device, IncidentType.OUTAGE, session, ufiber_endpoint)
            )
            continue

        if device.get("experience", 0) < MIN_EXPERIENCE:
            incidents.append(
                create_incident(
                    device, IncidentType.POOR_EXPERIENCE, session, ufiber_endpoint
                )
            )
            continue

        if device.get("rxPower", 0) < MIN_RX_POWER:
            incidents.append(
                create_incident(
                    device, IncidentType.POOR_SIGNAL, session, ufiber_endpoint
                )
            )
            continue

    return [incident for incident in incidents if incident is not None]
