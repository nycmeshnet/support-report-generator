import pytest
import datetime

import pytz

from mesh_support_report_generator.incident import Incident, IncidentType


def test_init_outage_missing_event_time():
    with pytest.raises(ValueError):
        Incident("device_name", IncidentType.OUTAGE)


def test_init_poor_signal_missing_metric_value():
    with pytest.raises(ValueError):
        Incident("device_name", IncidentType.POOR_SIGNAL)


def test_init_poor_experience_missing_metric_value():
    with pytest.raises(ValueError):
        Incident("device_name", IncidentType.POOR_EXPERIENCE)


def test_str_outage_with_site_name():
    event_time = datetime.datetime(2022, 1, 1, 5, 0, 0, tzinfo=pytz.UTC)
    incident = Incident(
        "device_name", IncidentType.OUTAGE, event_time, site_name="site_name"
    )
    assert str(incident) == "device_name (site_name) (offline since 2022-01-01 @ 00:00)"


def test_str_outage_without_site_name():
    event_time = datetime.datetime(2022, 1, 1, 5, 0, 0, tzinfo=pytz.UTC)
    incident = Incident("device_name", IncidentType.OUTAGE, event_time)
    assert str(incident) == "device_name (offline since 2022-01-01 @ 00:00)"


def test_str_poor_signal():
    incident = Incident("device_name", IncidentType.POOR_SIGNAL, metric_value=-80.0)
    assert str(incident) == "device_name (-80.0 dBm)"


def test_str_poor_experience():
    incident = Incident("device_name", IncidentType.POOR_EXPERIENCE, metric_value=75.0)
    assert str(incident) == "device_name (75.0%)"


def test_incident_repr():
    incident = Incident(
        device_name="nycmesh-xxx-yyyy",
        incident_type=IncidentType.OUTAGE,
        event_time=datetime.datetime.now(),
    )

    # Get the string representation of the object
    incident_repr = repr(incident)

    # Evaluate the string representation to recreate the object
    recreated_incident = eval(incident_repr)

    # Assert that the recreated object is equal to the original object
    assert recreated_incident.device_name == incident.device_name
    assert recreated_incident.incident_type == incident.incident_type
    assert recreated_incident.event_time == incident.event_time
    assert recreated_incident.site_name == incident.site_name
    assert recreated_incident.metric_value == incident.metric_value


def test_incident_eq():
    # Create some incidents to compare
    incident1 = Incident(
        "device1", IncidentType.OUTAGE, datetime.datetime(2022, 1, 1), "site1"
    )
    incident2 = Incident("device2", IncidentType.POOR_SIGNAL, None, metric_value=-20.0)
    incident3 = Incident(
        "device3",
        IncidentType.POOR_EXPERIENCE,
        datetime.datetime(2022, 1, 1),
        "site3",
        metric_value=75.0,
    )
    incident4 = Incident(
        "device1", IncidentType.OUTAGE, datetime.datetime(2022, 1, 1), "site1"
    )
    incident5 = Incident("device2", IncidentType.POOR_SIGNAL, None, metric_value=-20.0)
    incident6 = Incident(
        "device3",
        IncidentType.POOR_EXPERIENCE,
        datetime.datetime(2022, 1, 1),
        "site3",
        metric_value=75.0,
    )

    # Check that each incident is equal to itself
    assert incident1 == incident1
    assert incident2 == incident2
    assert incident3 == incident3

    # Check that equal incidents are detected as equal
    assert incident1 == incident4
    assert incident2 == incident5
    assert incident3 == incident6

    # Check that incidents with different attributes are detected as unequal
    assert not (incident1 == incident2)
    assert not (incident1 == incident3)
    assert not (incident1 == incident5)
    assert not (incident2 == incident3)
    assert not (incident2 == incident4)
    assert not (incident3 == incident5)
    assert not (incident4 == incident5)
