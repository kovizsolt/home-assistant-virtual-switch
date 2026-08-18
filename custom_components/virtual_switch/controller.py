from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import (
    CONF_CUSTOM_STATUSES,
    CONF_INITIAL_ONLINE,
    CONF_INITIAL_STATE,
    DEFAULT_INITIAL_ONLINE,
    DEFAULT_INITIAL_STATE,
    DOMAIN,
    STORE_KEY,
    STORE_VERSION,
    STATUS_ONLINE,
    STATUS_UNAVAILABLE,
)
from .state import VirtualSwitchState, build_status_definitions

_LOGGER = logging.getLogger(__name__)


class Controller:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.name = entry.title
        self.signal = f"{DOMAIN}_{entry.entry_id}_update"
        self.store: Store[dict[str, Any]] = Store(
            hass, STORE_VERSION, f"{DOMAIN}/{entry.entry_id}/{STORE_KEY}.json"
        )
        custom_statuses = list(
            entry.options.get(
                CONF_CUSTOM_STATUSES, entry.data.get(CONF_CUSTOM_STATUSES, [])
            )
        )
        self.status_definitions = build_status_definitions(custom_statuses)
        initial_status = (
            STATUS_ONLINE
            if bool(entry.data.get(CONF_INITIAL_ONLINE, DEFAULT_INITIAL_ONLINE))
            else STATUS_UNAVAILABLE
        )
        self.state = VirtualSwitchState(
            status=initial_status,
            internal_state=bool(entry.data.get(CONF_INITIAL_STATE, DEFAULT_INITIAL_STATE)),
            definitions=self.status_definitions,
        )

    async def async_setup(self) -> None:
        try:
            stored = await self.store.async_load()
        except (OSError, ValueError, TypeError) as error:
            _LOGGER.warning("[%s] Failed to load stored state: %s", self.name, error)
            return
        if stored is None:
            return
        try:
            internal_state = stored["internal_state"]
            if not isinstance(internal_state, bool):
                raise ValueError("stored internal_state must be boolean")
            if isinstance(stored.get("status"), str):
                status = stored["status"]
            elif isinstance(stored.get("online"), bool):
                status = STATUS_ONLINE if stored["online"] else STATUS_UNAVAILABLE
            else:
                raise ValueError("stored status is invalid")
            if status not in self.status_definitions:
                raise ValueError(f"stored status {status!r} is not configured")
            self.state = VirtualSwitchState(
                status=status,
                internal_state=internal_state,
                definitions=self.status_definitions,
            )
        except (KeyError, TypeError, ValueError) as error:
            _LOGGER.warning("[%s] Invalid stored state, using defaults: %s", self.name, error)

    @property
    def online(self) -> bool:
        return self.state.status == STATUS_ONLINE

    @property
    def status(self) -> str:
        return self.state.status

    @property
    def status_options(self) -> list[str]:
        return list(self.status_definitions)

    @property
    def main_available(self) -> bool:
        return self.state.main_available

    @property
    def main_is_on(self) -> bool | None:
        return self.state.main_is_on

    @property
    def internal_state(self) -> bool:
        return self.state.internal_state

    async def async_main(self, value: bool) -> None:
        await self._commit(self.state.set_from_main(value))

    async def async_internal(self, value: bool) -> None:
        await self._commit(self.state.set_internal(value))

    async def async_online(self, value: bool) -> None:
        await self._commit(self.state.set_online(value))

    async def async_status(self, value: str) -> None:
        await self._commit(self.state.set_status(value))

    async def _commit(self, changed: bool) -> None:
        if not changed:
            return
        await self.store.async_save(
            {
                "status": self.status,
                "internal_state": self.internal_state,
            }
        )
        async_dispatcher_send(self.hass, self.signal)
