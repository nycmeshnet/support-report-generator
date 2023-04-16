import json

import pytest
from datetime import datetime
from unittest import mock

from dateutil.tz import tzutc
from freezegun import freeze_time

from mesh_support_report_generator import unifi_outages
from mesh_support_report_generator.incident import Incident, IncidentType


@pytest.fixture
def mock_login():
    with mock.patch("mesh_support_report_generator.unifi_outages.login") as mock_login:
        mock_login.return_value = "token123"
        yield mock_login


@pytest.fixture
def mock_list_sites():
    with mock.patch(
        "mesh_support_report_generator.unifi_outages.list_sites"
    ) as mock_list_sites:
        with open("test/unifi_data/sites.json") as sites_file:
            mock_list_sites.return_value = json.load(sites_file)
        yield mock_list_sites


@pytest.fixture
def mock_get_devices():
    def mocked_get_devices(_, site_id: str):
        if site_id == "cod8a0z0":
            with open("test/unifi_data/devices.json") as devices_file:
                return json.load(devices_file)
        else:
            return []

    with mock.patch(
        "mesh_support_report_generator.unifi_outages.get_devices", mocked_get_devices
    ) as mock_get_devices:
        yield mock_get_devices


@freeze_time("2023-04-15")
def test_get_unifi_outage_lists(mock_login, mock_list_sites, mock_get_devices):
    incidents = unifi_outages.get_unifi_outage_lists()
    expected_incidents = [
        Incident(
            device_name="Vernon AP E",
            site_name="5916 - Vernon",
            event_time=datetime(2023, 4, 11, 6, 46, 46, 583000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="Vernon AP SW",
            site_name="5916 - Vernon",
            event_time=datetime(2023, 4, 16, 1, 29, 28, 955000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="Vernon AP NW",
            site_name="5916 - Vernon",
            event_time=datetime(2023, 4, 16, 1, 29, 50, 267000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="Vernon AP Switch East",
            site_name="5916 - Vernon",
            event_time=datetime(2023, 4, 16, 1, 29, 50, 267000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="Vernon AP S",
            site_name="5916 - Vernon",
            event_time=datetime(2023, 4, 16, 1, 29, 50, 267000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
    ]
    assert incidents == expected_incidents
