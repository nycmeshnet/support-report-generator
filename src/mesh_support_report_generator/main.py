import os

from mesh_support_report_generator.endpoints import UFIBER_BASES
from mesh_support_report_generator.post_to_slack import post_to_slack
from mesh_support_report_generator.report import write_report
from mesh_support_report_generator.ufiber_outages import (
    get_ufiber_outage_lists,
)
from mesh_support_report_generator import uisp_outages
from mesh_support_report_generator import unifi_outages

from io import StringIO

from dotenv import load_dotenv

load_dotenv()


def main():
    uisp_incidents = uisp_outages.get_uisp_outage_lists()
    unifi_incidents = unifi_outages.get_unifi_outage_lists()
    ufiber_incidents_by_olt = {
        olt_name: get_ufiber_outage_lists(endpoint)
        for olt_name, endpoint in UFIBER_BASES.items()
    }

    ufiber_incidents = []
    for olt_name, incident_list in ufiber_incidents_by_olt.items():
        for incident in incident_list:
            incident.site_name = olt_name
            ufiber_incidents.append(incident)

    string_stream = StringIO()
    report_header = write_report(
        string_stream, uisp_incidents, unifi_incidents, ufiber_incidents
    )

    string_stream.seek(0)
    diagnostics_str = string_stream.read()

    print(diagnostics_str)
    if os.environ.get("SLACK_ENABLED", "False") == "True":
        print("Posting to slack...")
        file_url = post_to_slack(report_header, diagnostics_str)
        print(f"Posted to {file_url}")
    else:
        print(
            "Not uploading to slack. Set the environment variable SLACK_ENABLED=True "
            "to enable automatic posting to slack"
        )


if __name__ == "__main__":
    main()
