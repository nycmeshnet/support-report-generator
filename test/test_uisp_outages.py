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
    incidents, ignored_incidents = uisp_outages.get_uisp_outage_lists()
    expected_incidents = [
        Incident(
            device_name="nycmesh-426-sxt1",
            event_time=datetime(2023, 5, 23, 22, 34, 56, 888000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-lbe-1327",
            event_time=datetime(2023, 5, 23, 22, 34, 51, 598000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-234-omni",
            event_time=datetime(2023, 5, 23, 14, 57, 15, 356000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-464-omni",
            event_time=datetime(2023, 5, 23, 3, 42, 18, 394000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-lbe-464",
            event_time=datetime(2023, 5, 23, 3, 26, 23, 283000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
    ]

    assert incidents == expected_incidents

    assert ignored_incidents == [
        Incident(
            device_name="nycmesh-yyyy-test-dev",
            site_name="Grand Street - 1933",
            event_time=None,
            incident_type=IncidentType.OUTAGE,
            ignored=True,
        ),
        Incident(
            device_name="nycmesh-yyyy-test-dev",
            site_name="otherstuff   abc def",
            event_time=None,
            incident_type=IncidentType.OUTAGE,
            ignored=True,
        ),
    ]
