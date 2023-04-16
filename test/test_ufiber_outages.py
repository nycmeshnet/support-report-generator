import json
from unittest.mock import patch

import pytest
from datetime import datetime
from unittest import mock

from dateutil.tz import tzutc
from freezegun import freeze_time

from mesh_support_report_generator import ufiber_outages
from mesh_support_report_generator.incident import Incident, IncidentType

MOCK_UFIBER_ENDPOINT = "http://mock_url_not_real"


@pytest.fixture
def mock_login():
    with mock.patch("mesh_support_report_generator.ufiber_outages.login") as mock_login:
        mock_login.return_value = "token123"
        yield mock_login


@pytest.fixture
def mock_get_devices():
    with mock.patch(
        "mesh_support_report_generator.ufiber_outages.get_devices"
    ) as mock_get_devices:
        with open("test/ufiber_data/devices.json") as devices_file:
            mock_get_devices.return_value = json.load(devices_file)
        yield mock_get_devices


@pytest.fixture
def mock_get_device_details():
    def mocked_get_device_details(_, ufiber_endpoint, device_serial: str):
        assert ufiber_endpoint == MOCK_UFIBER_ENDPOINT
        file_name = "test/ufiber_data/device_details.json"
        if device_serial == "INJECT_IGNORE_TOKEN":
            file_name = "test/ufiber_data/device_details_with_ignore_token.json"
        with open(file_name) as device_details_file:
            return json.load(device_details_file)

    with mock.patch(
        "mesh_support_report_generator.ufiber_outages.get_device_details",
        mocked_get_device_details,
    ) as mock_get_device_details:
        yield mock_get_device_details


@patch(
    "mesh_support_report_generator.ufiber_outages.IGNORE_OUTAGE_TOKEN",
    "!!IGNORE_OUTAGE!!",
)
@freeze_time("2023-04-15")
def test_get_ufiber_outage_lists(mock_login, mock_get_devices, mock_get_device_details):
    incidents = ufiber_outages.get_ufiber_outage_lists(MOCK_UFIBER_ENDPOINT)
    reported_incidents = incidents["reported"]
    ignored_incidents = incidents["ignored"]

    expected_incidents = [
        Incident(
            device_name="DEVICE_NAME",
            metric_value=-40.13,
            incident_type=IncidentType.POOR_SIGNAL,
        ),
        Incident(
            device_name="DEVICE_NAME",
            metric_value=56,
            incident_type=IncidentType.POOR_EXPERIENCE,
        ),
        Incident(
            device_name="DEVICE_NAME",
            incident_type=IncidentType.OUTAGE,
        ),
    ]

    assert reported_incidents == expected_incidents
    assert ignored_incidents == [
        Incident(
            device_name="DEVICE_NAME",
            incident_type=IncidentType.OUTAGE,
            ignored=True,
        )
    ]
