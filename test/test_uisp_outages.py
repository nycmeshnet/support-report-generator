import json
from unittest.mock import patch

import pytest
from datetime import datetime
from unittest import mock

from dateutil.tz import tzutc
from freezegun import freeze_time

from mesh_support_report_generator import uisp_outages
from mesh_support_report_generator.incident import Incident, IncidentType


@pytest.fixture
def mock_login():
    with mock.patch("mesh_support_report_generator.uisp_outages.login") as mock_login:
        mock_login.return_value = "token123"
        yield mock_login


@pytest.fixture
def mock_get_outages():
    with mock.patch(
        "mesh_support_report_generator.uisp_outages.get_outages"
    ) as mock_get_outages:
        with open("test/uisp_data/outages.json") as outages_file:
            mock_get_outages.return_value = {"items": json.load(outages_file)}
        yield mock_get_outages


@pytest.fixture
def mock_get_device():
    def mocked_get_device(_, device_id: str):
        file_name = "test/uisp_data/device.json"
        if device_id == "INJECT_IGNORE_TOKEN":
            file_name = "test/uisp_data/device_with_ignore_token.json"
        with open(file_name) as device_file:
            return json.load(device_file)

    with mock.patch(
        "mesh_support_report_generator.uisp_outages.get_device", mocked_get_device
    ) as mock_get_device:
        yield mock_get_device


@patch(
    "mesh_support_report_generator.uisp_outages.UISP_IGNORE_SITE_IDS",
    ["GRAVEYARD_SITE_ID"],
)
@patch(
    "mesh_support_report_generator.uisp_outages.IGNORE_OUTAGE_TOKEN",
    "!!IGNORE_OUTAGE!!",
)
@freeze_time("2023-04-15")
def test_get_uisp_outage_lists(mock_login, mock_get_outages, mock_get_device):
    incidents = uisp_outages.get_uisp_outage_lists()
    expected_incidents = [
        Incident(
            device_name="nycmesh-lbe-4018",
            event_time=datetime(2023, 4, 15, 22, 21, 22, 200000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-4433-omni",
            event_time=datetime(2023, 4, 15, 2, 29, 53, 391000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-meshroom-nbe-1934",
            event_time=datetime(2023, 4, 14, 20, 23, 42, 59000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-279-omni",
            event_time=datetime(2023, 4, 13, 14, 9, 17, 892000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-5218-sxt",
            event_time=datetime(2023, 4, 13, 3, 48, 26, 364000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-1933-meshsvc",
            event_time=datetime(2023, 4, 9, 21, 48, 41, 111000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
    ]
    assert incidents == expected_incidents
