import sys
from datetime import datetime, timezone, timedelta
import json
import os

import pytz as pytz
from dotenv import load_dotenv
import requests
import endpoints

load_dotenv()

MIN_RX_POWER = -30


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
    for ufiber_endpoint in endpoints.UFIBER_BASES:
        session = requests.Session()
        session.headers = {"x-auth-token": login(session, ufiber_endpoint)}
        devices = get_devices(session, ufiber_endpoint)

        poor_signal_devices.extend(
            [
                {
                    **get_device_details(session, ufiber_endpoint, device["serial"]),
                    **device,
                }
                for device in devices
                if device.get("rxPower", 0) < MIN_RX_POWER
            ]
        )

        disconnected_devices.extend(
            [
                get_device_details(session, ufiber_endpoint, device["serial"])
                for device in devices
                if not device["connected"]
            ]
        )

    yesterday = datetime.now(tz=timezone.utc) - timedelta(hours=24.1)
    last_week = datetime.now(tz=timezone.utc) - timedelta(days=7)

    print("UFIBER - Currently In Outage", file=stream)
    for device in disconnected_devices:
        print(f"{device['name']}", file=stream)
    if len(disconnected_devices) == 0:
        print("-- None --", file=stream)

    print("\n\nUFIBER - Poor Signal (< -30 dBm)", file=stream)
    for device in poor_signal_devices:
        print(f"{device['name']} ({device['rxPower']} dBm)", file=stream)
