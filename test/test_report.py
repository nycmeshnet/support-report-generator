import datetime
from io import StringIO

from dateutil.tz import tzutc
from freezegun import freeze_time

from mesh_support_report_generator.incident import Incident, IncidentType
from mesh_support_report_generator.report import write_report


@freeze_time("2023-04-15")
def test_report_no_incidents():
    stream = StringIO()
    write_report(stream, [], [], [], [])
    stream.seek(0)
    assert (
        stream.read()
        == """**Outage Report - Friday, April 14, 2023 @ 20:00**

UISP - Currently In Outage (new last 7 days)
-- None --


UNIFI - Currently In Outage (new last 7 days)
-- None --


UFIBER - Currently In Outage
-- None --


UFIBER - Poor Experience (< 100%)
-- None --


UFIBER - Poor Signal (< -28 dBm)
-- None --


Ignored Issues - All Sources
-- None --
"""
    )


@freeze_time("2023-04-15")
def test_report_uisp_only():
    uisp_outages = [
        Incident(
            device_name="nycmesh-abc-123",
            event_time=datetime.datetime.now(tz=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-456",
            event_time=datetime.datetime.now(tz=tzutc()) - datetime.timedelta(hours=2),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-789",
            event_time=datetime.datetime.now(tz=tzutc()) - datetime.timedelta(hours=4),
            incident_type=IncidentType.OUTAGE,
        ),
    ]

    stream = StringIO()
    write_report(stream, uisp_outages, [], [], [])
    stream.seek(0)
    assert (
        stream.read()
        == """**Outage Report - Friday, April 14, 2023 @ 20:00**

UISP - Currently In Outage (new last 7 days)
nycmesh-abc-123 (offline since 2023-04-14 @ 20:00)
nycmesh-abc-456 (offline since 2023-04-14 @ 18:00)
nycmesh-abc-789 (offline since 2023-04-14 @ 16:00)


UNIFI - Currently In Outage (new last 7 days)
-- None --


UFIBER - Currently In Outage
-- None --


UFIBER - Poor Experience (< 100%)
-- None --


UFIBER - Poor Signal (< -28 dBm)
-- None --


Ignored Issues - All Sources
-- None --
"""
    )


@freeze_time("2023-04-15")
def test_report_unifi_only():
    unifi_outages = [
        Incident(
            device_name="nycmesh-abc-123",
            site_name="xyz",
            event_time=datetime.datetime.now(tz=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-456",
            site_name="xyz",
            event_time=datetime.datetime.now(tz=tzutc()) - datetime.timedelta(hours=2),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-789",
            site_name="xyz",
            event_time=datetime.datetime.now(tz=tzutc()) - datetime.timedelta(hours=4),
            incident_type=IncidentType.OUTAGE,
        ),
    ]

    stream = StringIO()
    write_report(stream, [], unifi_outages, [], [])
    stream.seek(0)
    assert (
        stream.read()
        == """**Outage Report - Friday, April 14, 2023 @ 20:00**

UISP - Currently In Outage (new last 7 days)
-- None --


UNIFI - Currently In Outage (new last 7 days)
nycmesh-abc-123 (xyz) (offline since 2023-04-14 @ 20:00)
nycmesh-abc-456 (xyz) (offline since 2023-04-14 @ 18:00)
nycmesh-abc-789 (xyz) (offline since 2023-04-14 @ 16:00)


UFIBER - Currently In Outage
-- None --


UFIBER - Poor Experience (< 100%)
-- None --


UFIBER - Poor Signal (< -28 dBm)
-- None --


Ignored Issues - All Sources
-- None --
"""
    )


@freeze_time("2023-04-15")
def test_report_ufiber_outage_only():
    ufiber_outages = [
        Incident(
            device_name="nycmesh-abc-123",
            site_name="grand1",
            incident_type=IncidentType.OUTAGE,
        )
    ]

    stream = StringIO()
    write_report(stream, [], [], ufiber_outages, [])
    stream.seek(0)
    assert (
        stream.read()
        == """**Outage Report - Friday, April 14, 2023 @ 20:00**

UISP - Currently In Outage (new last 7 days)
-- None --


UNIFI - Currently In Outage (new last 7 days)
-- None --


UFIBER - Currently In Outage
nycmesh-abc-123 (grand1)


UFIBER - Poor Experience (< 100%)
-- None --


UFIBER - Poor Signal (< -28 dBm)
-- None --


Ignored Issues - All Sources
-- None --
"""
    )


@freeze_time("2023-04-15")
def test_report_ufiber_poor_experience_only():
    ufiber_outages = [
        Incident(
            device_name="nycmesh-abc-456",
            site_name="grand2",
            incident_type=IncidentType.POOR_EXPERIENCE,
            metric_value=45,
        ),
    ]

    stream = StringIO()
    write_report(stream, [], [], ufiber_outages, [])
    stream.seek(0)
    assert (
        stream.read()
        == """**Outage Report - Friday, April 14, 2023 @ 20:00**

UISP - Currently In Outage (new last 7 days)
-- None --


UNIFI - Currently In Outage (new last 7 days)
-- None --


UFIBER - Currently In Outage
-- None --


UFIBER - Poor Experience (< 100%)
nycmesh-abc-456 (grand2) (45%)


UFIBER - Poor Signal (< -28 dBm)
-- None --


Ignored Issues - All Sources
-- None --
"""
    )


@freeze_time("2023-04-15")
def test_report_ufiber_poor_signal_only():
    ufiber_outages = [
        Incident(
            device_name="nycmesh-abc-789",
            site_name="grand3",
            incident_type=IncidentType.POOR_SIGNAL,
            metric_value=-34.43,
        ),
    ]

    stream = StringIO()
    write_report(stream, [], [], ufiber_outages, [])
    stream.seek(0)
    assert (
        stream.read()
        == """**Outage Report - Friday, April 14, 2023 @ 20:00**

UISP - Currently In Outage (new last 7 days)
-- None --


UNIFI - Currently In Outage (new last 7 days)
-- None --


UFIBER - Currently In Outage
-- None --


UFIBER - Poor Experience (< 100%)
-- None --


UFIBER - Poor Signal (< -28 dBm)
nycmesh-abc-789 (grand3) (-34.43 dBm)


Ignored Issues - All Sources
-- None --
"""
    )


@freeze_time("2023-04-15")
def test_report_all():
    uisp_outages = [
        Incident(
            device_name="nycmesh-abc-123",
            event_time=datetime.datetime.now(tz=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-456",
            event_time=datetime.datetime.now(tz=tzutc()) - datetime.timedelta(hours=2),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-789",
            event_time=datetime.datetime.now(tz=tzutc()) - datetime.timedelta(hours=4),
            incident_type=IncidentType.OUTAGE,
        ),
    ]
    unifi_outages = [
        Incident(
            device_name="nycmesh-abc-123",
            site_name="xyz",
            event_time=datetime.datetime.now(tz=tzutc()),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-456",
            site_name="xyz",
            event_time=datetime.datetime.now(tz=tzutc()) - datetime.timedelta(hours=2),
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-789",
            site_name="xyz",
            event_time=datetime.datetime.now(tz=tzutc()) - datetime.timedelta(hours=4),
            incident_type=IncidentType.OUTAGE,
        ),
    ]
    ufiber_outages = [
        Incident(
            device_name="nycmesh-abc-123",
            site_name="grand1",
            incident_type=IncidentType.OUTAGE,
        ),
        Incident(
            device_name="nycmesh-abc-456",
            site_name="grand2",
            incident_type=IncidentType.POOR_EXPERIENCE,
            metric_value=45,
        ),
        Incident(
            device_name="nycmesh-abc-789",
            site_name="grand3",
            incident_type=IncidentType.POOR_SIGNAL,
            metric_value=-34.43,
        ),
    ]
    ignored_outages = [
        Incident(
            device_name="nycmesh-abc-123",
            site_name="Ignore token detected",
            incident_type=IncidentType.OUTAGE,
        ),
    ]

    stream = StringIO()
    write_report(stream, uisp_outages, unifi_outages, ufiber_outages, ignored_outages)
    stream.seek(0)
    assert (
        stream.read()
        == """**Outage Report - Friday, April 14, 2023 @ 20:00**

UISP - Currently In Outage (new last 7 days)
nycmesh-abc-123 (offline since 2023-04-14 @ 20:00)
nycmesh-abc-456 (offline since 2023-04-14 @ 18:00)
nycmesh-abc-789 (offline since 2023-04-14 @ 16:00)


UNIFI - Currently In Outage (new last 7 days)
nycmesh-abc-123 (xyz) (offline since 2023-04-14 @ 20:00)
nycmesh-abc-456 (xyz) (offline since 2023-04-14 @ 18:00)
nycmesh-abc-789 (xyz) (offline since 2023-04-14 @ 16:00)


UFIBER - Currently In Outage
nycmesh-abc-123 (grand1)


UFIBER - Poor Experience (< 100%)
nycmesh-abc-456 (grand2) (45%)


UFIBER - Poor Signal (< -28 dBm)
nycmesh-abc-789 (grand3) (-34.43 dBm)


Ignored Issues - All Sources
nycmesh-abc-123 (Ignore token detected)
"""
    )
