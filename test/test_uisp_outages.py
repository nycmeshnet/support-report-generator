import json
from datetime import datetime
from unittest import mock
from unittest.mock import patch

import pytest
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
def mock_get_devices():
    with mock.patch(
        "mesh_support_report_generator.uisp_outages.get_all_devices"
    ) as mock_get_all_devices:
        with open("test/uisp_data/devices.json") as devices_file:
            mock_get_all_devices.return_value = json.load(devices_file)
        yield mock_get_all_devices


@pytest.fixture
def mock_meshdb_get_device():
    with mock.patch(
        "mesh_support_report_generator.uisp_outages.get_device_details_for_uisp_id"
    ) as mock_get_nn_for_uisp_id:
        with open("test/meshdb_data/device_lookup.json") as devices_file:
            mock_get_nn_for_uisp_id.return_value = json.load(devices_file)
        yield mock_get_nn_for_uisp_id


@patch(
    "mesh_support_report_generator.uisp_outages.UISP_IGNORE_SITE_IDS",
    ["GRAVEYARD_SITE_ID"],
)
@patch(
    "mesh_support_report_generator.uisp_outages.IGNORE_OUTAGE_TOKEN",
    "!!IGNORE_OUTAGE!!",
)
@freeze_time("2024-05-12")
def test_get_uisp_outage_lists(mock_login, mock_get_devices, mock_meshdb_get_device):
    incidents, ignored_incidents, map_link = uisp_outages.get_uisp_outage_lists()
    expected_incidents = [
        Incident(
            device_name="nycmesh-200-omni",
            event_time=datetime(2024, 5, 12, 19, 50, 40, 413000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-156-omni",
            event_time=datetime(2024, 5, 12, 19, 50, 40, 413000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-238-lbe-240",
            event_time=datetime(2024, 5, 8, 14, 47, 2, 507000, tzinfo=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
    ]

    assert incidents == expected_incidents

    assert ignored_incidents == [
        Incident(
            device_name="nycmesh-xxxx-test-dev",
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
        Incident(
            device_name="nycmesh-zzzz-test-dev",
            site_name="maintenance mode",
            event_time=None,
            incident_type=IncidentType.OUTAGE,
            ignored=True,
        ),
    ]

    assert map_link == "https://map.nycmesh.net/nodes/254"
