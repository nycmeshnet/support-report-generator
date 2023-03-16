import pytz

from post_to_slack import post_to_slack
from ufiber_outages import get_ufiber_outage_lists
from uisp_outages import get_uisp_outage_lists
from unifi_outages import get_unifi_outage_lists

from io import StringIO

from datetime import datetime


def main():
    report_time = datetime.now(tz=pytz.timezone("US/Eastern")).strftime(
        "%A, %B %-d, %Y @ %H:%M"
    )
    report_header = f"Outage Report - {report_time}"
    string_stream = StringIO()
    string_stream.write(f"**{report_header}**\n\n")
    get_uisp_outage_lists(string_stream)
    string_stream.write("\n\n")
    get_unifi_outage_lists(string_stream)
    string_stream.write("\n\n")
    get_ufiber_outage_lists(string_stream)

    string_stream.seek(0)
    diagnostics_str = string_stream.read()
    print(diagnostics_str)
    post_to_slack(report_header, diagnostics_str)


if __name__ == "__main__":
    main()
