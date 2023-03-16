from ufiber_outages import get_ufiber_outage_lists
from uisp_outages import get_uisp_outage_lists
from unifi_outages import get_unifi_outage_lists


def main():
    get_uisp_outage_lists()
    get_unifi_outage_lists()
    get_ufiber_outage_lists()


if __name__ == "__main__":
    main()
