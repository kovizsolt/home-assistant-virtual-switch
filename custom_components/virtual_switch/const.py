DOMAIN = "virtual_switch"

PLATFORMS = ["switch"]

CONF_NAME = "name"
CONF_INITIAL_ONLINE = "initial_online"
CONF_INITIAL_STATE = "initial_state"

DEFAULT_INITIAL_ONLINE = True
DEFAULT_INITIAL_STATE = False

STATE_ONLINE = "ONLINE"
STATE_OFFLINE = "OFFLINE"

EVENT_MAIN_ON = "main_on"
EVENT_MAIN_OFF = "main_off"
EVENT_INTERNAL_ON = "internal_on"
EVENT_INTERNAL_OFF = "internal_off"
EVENT_GO_ONLINE = "go_online"
EVENT_GO_OFFLINE = "go_offline"

SUFFIX_MAIN = "main"
SUFFIX_INTERNAL = "internal"
SUFFIX_ONLINE = "online"

STORE_VERSION = 1
STORE_KEY = "state"

CARD_URL = "/virtual_switch/virtual-switch-card.js"
CARD_FILENAME = "virtual-switch-card.js"
