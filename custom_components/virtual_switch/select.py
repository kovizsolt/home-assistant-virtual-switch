from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, FIXED_STATUSES, SUFFIX_STATUS
from .controller import Controller


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    bucket = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([StatusSelect(bucket["controller"], bucket["slug"])])


class StatusSelect(SelectEntity):
    _attr_should_poll = False
    _attr_has_entity_name = False
    _attr_icon = "mdi:list-status"

    def __init__(self, controller: Controller, slug: str) -> None:
        self.controller = controller
        self.entity_id = f"select.{slug}_{SUFFIX_STATUS}"
        self._attr_unique_id = f"{controller.entry.entry_id}_{SUFFIX_STATUS}"
        self._attr_name = f"{controller.name} Status"
        # HA reserves lowercase "unknown" and "unavailable" as entity states.
        # Title-cased fixed option values keep this SelectEntity operable while the
        # controller continues to use the documented lowercase status names.
        self._option_to_status = {
            self._encode_option(status): status for status in controller.status_options
        }
        self._attr_options = list(self._option_to_status)

    @staticmethod
    def _encode_option(status: str) -> str:
        return status.title() if status in FIXED_STATUSES else status

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.controller.entry.entry_id)}, name=self.controller.name
        )

    @property
    def current_option(self) -> str:
        return self._encode_option(self.controller.status)

    async def async_select_option(self, option: str) -> None:
        await self.controller.async_status(self._option_to_status[option])

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, self.controller.signal, self._update))

    @callback
    def _update(self) -> None:
        self.async_write_ha_state()
