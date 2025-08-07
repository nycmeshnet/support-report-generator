UISP_BASE = "https://uisp.mesh.nycmesh.net/nms/api/v2.1"
UISP_LOGIN = UISP_BASE + "/user/login"
UISP_OUTAGES = UISP_BASE + "/outages"
UISP_DEVICES = UISP_BASE + "/devices"
UISP_DEVICE_DETAILS = UISP_BASE + "/devices/"

UNIFI_BASE = "https://unifi.nycmesh.net:8443/api"
UNIFI_LOGIN = UNIFI_BASE + "/login"
UNIFI_LIST_SITES = UNIFI_BASE + "/self/sites"
UNIFI_LIST_DEVICES = UNIFI_BASE + "/s/%s/stat/device"

UFIBER_BASES = {
    "nycmesh-1932-olt3": "https://10.70.188.2/api/v1.0",
    "nycmesh-1932-olt2": "https://10.70.188.3/api/v1.0",
    "nycmesh-1934-olt1": "https://10.70.188.4/api/v1.0",
    "nycmesh-1936-olt-xgs": "https://10.70.188.5/api/v1.0",
    "nycmesh-584-olt-xgs": "https://10.70.198.4/api/v1.0",
    "nycmesh-730-olt-xgs": "https://10.70.211.2/api/v1.0",
    "nycmesh-3461-olt": "https://10.70.171.5/api/v1.0",
}
UFIBER_LOGIN_SUFFIX = "/user/login"
UFIBER_LIST_DEVICES_SUFFIX = "/gpon/onus"
UFIBER_DESCRIBE_DEVICE_SUFFIX = "/gpon/onus/%s/settings"

MESHDB_BASE = "https://db.nycmesh.net/api/v1"
MESHDB_DEVICES_BY_UISP_ID = MESHDB_BASE + "/devices/lookup/?uisp_id="

MESH_MAP_WITH_NODES = "https://map.nycmesh.net/nodes/"
