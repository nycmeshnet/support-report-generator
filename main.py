from ufiber_outages import get_ufiber_outage_lists
from uisp_outages import get_uisp_outage_lists
from unifi_outages import get_unifi_outage_lists

from io import StringIO


def main():
    string_stream = StringIO()
    get_uisp_outage_lists(string_stream)
    string_stream.write("\n\n")
    get_unifi_outage_lists(string_stream)
    string_stream.write("\n\n")
    get_ufiber_outage_lists(string_stream)

    string_stream.seek(0)
    print(string_stream.read())


if __name__ == "__main__":
    main()
