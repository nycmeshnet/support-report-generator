import sys
from datetime import datetime

import pytz

from mesh_support_report_generator import uisp_outages, unifi_outages, ufiber_outages
from mesh_support_report_generator.incident import IncidentType


def write_report(
    stream: sys.stdout,
    uisp_incidents,
    unifi_incidents,
    ufiber_incidents,
    ignored_incidents,
):
    report_time = datetime.now(tz=pytz.timezone("US/Eastern")).strftime(
        "%A, %B %d, %Y @ %H:%M"
    )
    report_header = f"Outage Report - {report_time}"
    stream.write(f"**{report_header}**\n\n")

    print(
        f"UISP - Currently In Outage (new last {uisp_outages.LAST_N_DAYS_TO_REPORT} days)",
        file=stream,
    )
    for incident in uisp_incidents:
        print(incident, file=stream)
    if len(uisp_incidents) == 0:
        print("-- None --", file=stream)
    stream.write("\n\n")

    print(
        f"UNIFI - Currently In Outage (new last {unifi_outages.LAST_N_DAYS_TO_REPORT} days)",
        file=stream,
    )
    for incident in unifi_incidents:
        print(incident, file=stream)
    if len(unifi_incidents) == 0:
        print("-- None --", file=stream)
    stream.write("\n\n")

    print("UFIBER - Currently In Outage", file=stream)
    for incident in ufiber_incidents:
        if incident.incident_type == IncidentType.OUTAGE:
            print(incident, file=stream)
    if not any(
        incident.incident_type == IncidentType.OUTAGE for incident in ufiber_incidents
    ):
        print("-- None --", file=stream)
    stream.write("\n\n")

    print(
        f"UFIBER - Poor Experience (< {ufiber_outages.MIN_EXPERIENCE}%)",
        file=stream,
    )
    for incident in ufiber_incidents:
        if incident.incident_type == IncidentType.POOR_EXPERIENCE:
            print(incident, file=stream)
    if not any(
        incident.incident_type == IncidentType.POOR_EXPERIENCE
        for incident in ufiber_incidents
    ):
        print("-- None --", file=stream)
    stream.write("\n\n")

    print(f"UFIBER - Poor Signal (< {ufiber_outages.MIN_RX_POWER} dBm)", file=stream)
    for incident in ufiber_incidents:
        if incident.incident_type == IncidentType.POOR_SIGNAL:
            print(incident, file=stream)
    if not any(
        incident.incident_type == IncidentType.POOR_SIGNAL
        for incident in ufiber_incidents
    ):
        print("-- None --", file=stream)
    stream.write("\n\n")

    print(f"Ignored Issues - All Sources", file=stream)
    for incident in ignored_incidents:
        print(incident, file=stream)
    if len(ignored_incidents) == 0:
        print("-- None --", file=stream)

    return report_header
