from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import (
    CONF_INITIAL_ONLINE,
    CONF_INITIAL_STATE,
    DEFAULT_INITIAL_ONLINE,
    DEFAULT_INITIAL_STATE,
    DOMAIN,
    STORE_KEY,
    STORE_VERSION,
)
from .state import VirtualSwitchState

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
        self.state = VirtualSwitchState(
            online=bool(entry.data.get(CONF_INITIAL_ONLINE, DEFAULT_INITIAL_ONLINE)),
            internal_state=bool(entry.data.get(CONF_INITIAL_STATE, DEFAULT_INITIAL_STATE)),
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
            values = (stored["online"], stored["internal_state"])
            if not all(isinstance(value, bool) for value in values):
                raise ValueError("stored state values must be boolean")
            self.state = VirtualSwitchState(
                online=stored["online"],
                internal_state=stored["internal_state"],
            )
        except (KeyError, TypeError, ValueError) as error:
            _LOGGER.warning("[%s] Invalid stored state, using defaults: %s", self.name, error)

    @property
    def online(self) -> bool:
        return self.state.online

    @property
    def internal_state(self) -> bool:
        return self.state.internal_state

    async def async_main(self, value: bool) -> None:
        await self._commit(self.state.set_from_main(value))

    async def async_internal(self, value: bool) -> None:
        await self._commit(self.state.set_internal(value))

    async def async_online(self, value: bool) -> None:
        await self._commit(self.state.set_online(value))

    async def _commit(self, changed: bool) -> None:
        if not changed:
            return
        await self.store.async_save(
            {
                "online": self.online,
                "internal_state": self.internal_state,
            }
        )
        async_dispatcher_send(self.hass, self.signal)
