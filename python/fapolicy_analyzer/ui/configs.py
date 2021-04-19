from enum import Enum

class Colors:
    LIGHT_RED = "#FF3333"
    LIGHT_YELLOW = "#FFFF33"
    LIGHT_GREEN = "light green"

class StateEvents(Enum):
    STATE_UNAPPLIED_NONE = 0
    STATE_UNAPPLIED_CHANGES = 1
