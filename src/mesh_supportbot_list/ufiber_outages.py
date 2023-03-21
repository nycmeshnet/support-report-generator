import sys
from datetime import datetime, timezone, timedelta
import json
import os

from dotenv import load_dotenv
import requests
import mesh_supportbot_list.endpoints as endpoints

load_dotenv()

MIN_RX_POWER = -30
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


def get_ufiber_outage_lists(stream=sys.stdout):
    poor_signal_devices = []
    disconnected_devices = []
    poor_experience_devices = []

    for ufiber_endpoint in endpoints.UFIBER_BASES:
        session = requests.Session()
        session.headers = {"x-auth-token": login(session, ufiber_endpoint)}
        devices = get_devices(session, ufiber_endpoint)

        for device in devices:
            if not device["connected"]:
                disconnected_devices.append(
                    get_device_details(session, ufiber_endpoint, device["serial"])
                )
                continue
            if device.get("rxPower", 0) < MIN_RX_POWER:
                poor_signal_devices.append(
                    {
                        **get_device_details(
                            session, ufiber_endpoint, device["serial"]
                        ),
                        **device,
                    }
                )

            if device.get("experience", 0) < MIN_EXPERIENCE:
                poor_experience_devices.append(
                    {
                        **get_device_details(
                            session, ufiber_endpoint, device["serial"]
                        ),
                        **device,
                    }
                )

    yesterday = datetime.now(tz=timezone.utc) - timedelta(hours=24.1)
    last_week = datetime.now(tz=timezone.utc) - timedelta(days=7)

    print("UFIBER - Currently In Outage", file=stream)
    for device in disconnected_devices:
        print(f"{device['name']}", file=stream)
    if len(disconnected_devices) == 0:
        print("-- None --", file=stream)

    print(f"\n\nUFIBER - Poor Signal (< {MIN_RX_POWER} dBm)", file=stream)
    for device in poor_signal_devices:
        print(f"{device['name']} ({device['rxPower']} dBm)", file=stream)
    if len(poor_signal_devices) == 0:
        print("-- None --", file=stream)

    print(f"\n\nUFIBER - Poor Experience (< {MIN_EXPERIENCE}%)", file=stream)
    for device in poor_experience_devices:
        print(f"{device['name']} ({device.get('experience', 'N/A')}%)", file=stream)
    if len(poor_experience_devices) == 0:
        print("-- None --", file=stream)
