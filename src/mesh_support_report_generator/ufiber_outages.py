import json
import os

from dotenv import load_dotenv
import requests
import mesh_support_report_generator.endpoints as endpoints
from mesh_support_report_generator.incident import Incident, IncidentType
from requests import ConnectTimeout
from urllib3.exceptions import InsecureRequestWarning

load_dotenv()

IGNORE_OUTAGE_TOKEN = os.environ["IGNORE_OUTAGE_TOKEN"]

MIN_RX_POWER = -28
MIN_EXPERIENCE = 100


def login(session: requests.Session, ufiber_base_url: str):
    # Suppress the 'Unverified HTTPS request is being made to host' log spam
    # because the POST is made with verify=False
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
    # Attempt to retrieve the notes from the device details
    # If the notes don't exist, gracefully continue while printing the error and device_details
    try:
        device_notes = device_details["notes"]
    except KeyError:
        print("Device Details object [{}] was missing the notes section"
              .format(device_details))
        device_notes = ''

    ignored = bool(device_notes and IGNORE_OUTAGE_TOKEN in device_notes)

    # Attempt to retrieve the name from the device details
    # If the name doesn't exist, gracefully continue with a stand-in device name
    try:
        device_name = device_details["name"]
    except KeyError:
        print("Device Details object [{}] was missing the name section"
              .format(device_details))
        device_name = 'MISSING_DEVICE_NAME'

    if incident_type == IncidentType.OUTAGE:
        return Incident(
            device_name=device_name,
            incident_type=IncidentType.OUTAGE,
            ignored=ignored,
        )

    if incident_type == IncidentType.POOR_EXPERIENCE:
        return Incident(
            device_name=device_name,
            incident_type=IncidentType.POOR_EXPERIENCE,
            metric_value=device.get("experience", "N/A"),
            ignored=ignored,
        )

    if incident_type == IncidentType.POOR_SIGNAL:
        return Incident(
            device_name=device_name,
            incident_type=IncidentType.POOR_SIGNAL,
            metric_value=device["rxPower"],
            ignored=ignored,
        )

    raise TypeError(f"Invalid incident_type: {incident_type}")


def get_ufiber_outage_lists(ufiber_endpoint):
    print("Fetching Devices Info from UFiber endpoint {}".format(ufiber_endpoint))

    incidents = []

    # Attempt to connect to the current UFiber device, and skip it if it times out
    session = requests.Session()
    try:
        session.headers = {"x-auth-token": login(session, ufiber_endpoint)}
    except ConnectTimeout:
        print("Timed out while connecting to UFiber device {}, skipping".format(ufiber_endpoint))
        return

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

    return {
        "reported": [incident for incident in incidents if not incident.ignored],
        "ignored": [incident for incident in incidents if incident.ignored],
    }
