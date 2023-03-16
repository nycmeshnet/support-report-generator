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
            "most_recent_connect_time": datetime.fromtimestamp(
                device["start_connected_millis"] / 1000, timezone.utc
            )
            if device["state"]
            else None,
            "most_recent_disconnect_time": datetime.fromtimestamp(
                device["start_disconnected_millis"] / 1000, timezone.utc
            ),
        }
        for device in devices_full_data
    ]

    yesterday = datetime.now(tz=timezone.utc) - timedelta(hours=24.1)
    last_week = datetime.now(tz=timezone.utc) - timedelta(days=7)
    current_outages = [device for device in devices_simplified if device["in_outage"]]

    new_outages = [
        device
        for device in devices_simplified
        if device["in_outage"] and device["most_recent_disconnect_time"] > yesterday
    ]

    recent_outages = [
        device
        for device in devices_simplified
        if device["most_recent_disconnect_time"] > last_week
        and device["id"] not in [dev["id"] for dev in new_outages]
    ]
    #
    print("UNIFI - Currently In Outage (new last 24 hours)")
    for device in new_outages:
        print(f"{device['site']} {device['name']}")
    if len(new_outages) == 0:
        print("-- None --")

    print("\n\nUNIFI - Other Recent Outages (last 7 days)")
    for device in recent_outages:
        if device["in_outage"]:
            outage_time = (
                device["most_recent_disconnect_time"]
                .astimezone(tz=pytz.timezone("US/Eastern"))
                .strftime("%Y-%m-%d @ %H:%M")
            )
            outage_status = f"OFFLINE since {outage_time}"
        else:
            recovery_time = (
                device["most_recent_connect_time"]
                .astimezone(tz=pytz.timezone("US/Eastern"))
                .strftime("%Y-%m-%d @ %H:%M")
            )
            outage_status = f"Reconnected {recovery_time}"
        print(f"{device['site']} {device['name']} {outage_status}")
