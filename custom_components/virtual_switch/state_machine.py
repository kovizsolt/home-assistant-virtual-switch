from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from .const import (
    EVENT_GO_OFFLINE,
    EVENT_GO_ONLINE,
    EVENT_INTERNAL_OFF,
    EVENT_INTERNAL_ON,
    EVENT_MAIN_OFF,
    EVENT_MAIN_ON,
    STATE_OFFLINE,
    STATE_ONLINE,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Transition:
    target: str
    action: str


TRANSITIONS = {
    STATE_ONLINE: {
        EVENT_MAIN_ON: Transition(STATE_ONLINE, "set_both_on"),
        EVENT_MAIN_OFF: Transition(STATE_ONLINE, "set_both_off"),
        EVENT_INTERNAL_ON: Transition(STATE_ONLINE, "set_both_on"),
        EVENT_INTERNAL_OFF: Transition(STATE_ONLINE, "set_both_off"),
        EVENT_GO_ONLINE: Transition(STATE_ONLINE, "sync_reported"),
        EVENT_GO_OFFLINE: Transition(STATE_OFFLINE, "noop"),
    },
    STATE_OFFLINE: {
        EVENT_MAIN_ON: Transition(STATE_OFFLINE, "set_internal_on"),
        EVENT_MAIN_OFF: Transition(STATE_OFFLINE, "set_internal_off"),
        EVENT_INTERNAL_ON: Transition(STATE_OFFLINE, "set_internal_on"),
        EVENT_INTERNAL_OFF: Transition(STATE_OFFLINE, "set_internal_off"),
        EVENT_GO_ONLINE: Transition(STATE_ONLINE, "sync_reported"),
        EVENT_GO_OFFLINE: Transition(STATE_OFFLINE, "noop"),
    },
}


class VirtualSwitchStateMachine:
    def __init__(self, *, online: bool, internal_state: bool, reported_state: bool) -> None:
        self.state = STATE_ONLINE if online else STATE_OFFLINE
        self.internal_state = internal_state
        self.reported_state = reported_state

    @property
    def online(self) -> bool:
        return self.state == STATE_ONLINE

    @property
    def snapshot(self) -> tuple[bool, bool, bool]:
        return self.online, self.internal_state, self.reported_state

    async def handle(self, event: str) -> None:
        transition = TRANSITIONS.get(self.state, {}).get(event)
        if transition is None:
            _LOGGER.warning("Unknown transition: state=%s event=%s", self.state, event)
            return
        old_state = self.state
        getattr(self, transition.action)()
        self.state = transition.target
        if old_state != self.state:
            _LOGGER.info(
                "%s -> %s, event=%s, timestamp=%s",
                old_state,
                self.state,
                event,
                datetime.now(timezone.utc).isoformat(),
            )

    def noop(self) -> None:
        return

    def set_both_on(self) -> None:
        self.internal_state = True
        self.reported_state = True

    def set_both_off(self) -> None:
        self.internal_state = False
        self.reported_state = False

    def set_internal_on(self) -> None:
        self.internal_state = True

    def set_internal_off(self) -> None:
        self.internal_state = False

    def sync_reported(self) -> None:
        self.reported_state = self.internal_state
