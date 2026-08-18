from __future__ import annotations


class VirtualSwitchState:
    """Single source of truth for the simulated device."""

    def __init__(self, *, online: bool, internal_state: bool) -> None:
        self.online = online
        self.internal_state = internal_state

    @property
    def main_available(self) -> bool:
        return self.online

    @property
    def main_is_on(self) -> bool:
        return self.internal_state

    def set_from_main(self, value: bool) -> bool:
        if not self.online:
            return False
        return self.set_internal(value)

    def set_internal(self, value: bool) -> bool:
        if self.internal_state == value:
            return False
        self.internal_state = value
        return True

    def set_online(self, value: bool) -> bool:
        if self.online == value:
            return False
        self.online = value
        return True

