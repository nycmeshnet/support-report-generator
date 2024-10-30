import csv
import json
import re

import requests
from dotenv import load_dotenv

from mesh_support_report_generator import endpoints
from mesh_support_report_generator.unifi_outages import get_devices, login

load_dotenv()

SITE_ID = "2hp2un8u"
SSID_NAME_REGEX = r"\d+[A-Za-z]"

PASSWORDS_FILE = "ap_passwords.csv"
SSID_NAME_COLUMN = "Apartment Number"
PASSWORD_COLUMN = "Password"


def get_ssids(session: requests.Session, site_id: str):
    response = session.get(
        endpoints.UNIFI_LIST_SSIDS % site_id,
        verify=False,
    )
    response.raise_for_status()
    return json.loads(response.content.decode("UTF8"))["data"]


def set_ssid_password(
    session: requests.Session,
    site_id: str,
    ssid_id: str,
    apartment_number: str,
    password: str,
):
    old_config = json.loads(
        session.get(
            endpoints.UNIFI_SSID % (site_id, ssid_id),
            verify=False,
        ).content.decode("UTF8")
    )["data"][0]

    old_config["name"] = f"NYC Mesh - Apt {apartment_number}"
    old_config["x_passphrase"] = password

    response = session.put(
        endpoints.UNIFI_SSID % (site_id, ssid_id),
        json=old_config,
        verify=False,
    )
    response.raise_for_status()

    return json.loads(response.content.decode("UTF8"))


def main():
    session = requests.Session()
    login(session)

    ssids = {}

    for ssid in get_ssids(session, SITE_ID):
        if re.match(SSID_NAME_REGEX, ssid.get("name", "")):
            ssids[ssid["name"]] = ssid["_id"]

    with open(PASSWORDS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ssid_name = row[SSID_NAME_COLUMN]
            wifi_id = ssids[ssid_name]
            print(f"Setting password for SSID {ssid_name} (id {wifi_id})...")
            set_ssid_password(
                session, SITE_ID, wifi_id, row[SSID_NAME_COLUMN], row[PASSWORD_COLUMN]
            )


if __name__ == "__main__":
    main()
