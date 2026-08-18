DOMAIN = "virtual_switch"

PLATFORMS = ["switch", "select"]

CONF_NAME = "name"
CONF_CUSTOM_STATUSES = "custom_statuses"
CONF_INITIAL_ONLINE = "initial_online"
CONF_INITIAL_STATE = "initial_state"

DEFAULT_INITIAL_ONLINE = True
DEFAULT_INITIAL_STATE = False

SUFFIX_MAIN = "main"
SUFFIX_INTERNAL = "internal"
SUFFIX_ONLINE = "online"
SUFFIX_STATUS = "status"

STATUS_ONLINE = "online"
STATUS_UNAVAILABLE = "unavailable"
STATUS_UNKNOWN = "unknown"
STATUS_ERROR = "error"
FIXED_STATUSES = (STATUS_ONLINE, STATUS_UNAVAILABLE, STATUS_UNKNOWN, STATUS_ERROR)

STORE_VERSION = 1
STORE_KEY = "state"

CARD_URL = "/virtual_switch/virtual-switch-card.js"
CARD_FILENAME = "virtual-switch-card.js"
