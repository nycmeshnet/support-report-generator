UISP_BASE = "https://uisp.mesh.nycmesh.net/nms/api/v2.1"
UISP_LOGIN = UISP_BASE + "/user/login"
UISP_OUTAGES = UISP_BASE + "/outages"
UISP_DEVICE_DETAILS = UISP_BASE + "/devices/"

UNIFI_BASE = "https://unifi.nycmesh.net:8443/api"
UNIFI_LOGIN = UNIFI_BASE + "/login"
UNIFI_LIST_SITES = UNIFI_BASE + "/self/sites"
UNIFI_LIST_DEVICES = UNIFI_BASE + "/s/%s/stat/device"

UFIBER_BASES = ["https://10.70.188.2/api/v1.0", "https://10.70.188.3/api/v1.0"]
UFIBER_LOGIN_SUFFIX = "/user/login"
UFIBER_LIST_DEVICES_SUFFIX = "/gpon/onus"
UFIBER_DESCRIBE_DEVICE_SUFFIX = "/gpon/onus/%s/settings"
