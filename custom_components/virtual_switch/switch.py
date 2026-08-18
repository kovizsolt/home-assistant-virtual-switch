from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, SUFFIX_INTERNAL, SUFFIX_MAIN
from .controller import Controller


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    bucket = hass.data[DOMAIN][entry.entry_id]
    controller: Controller = bucket["controller"]
    slug: str = bucket["slug"]
    async_add_entities(
        [MainSwitch(controller, slug), InternalSwitch(controller, slug)]
    )


class _BaseSwitch(SwitchEntity):
    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, controller: Controller, slug: str, suffix: str, label: str) -> None:
        self.controller = controller
        self.entity_id = f"switch.{slug}_{suffix}"
        self._attr_unique_id = f"{controller.entry.entry_id}_{suffix}"
        self._attr_name = f"{controller.name} {label}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self.controller.entry.entry_id)}, name=self.controller.name)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, self.controller.signal, self._update))

    @callback
    def _update(self) -> None:
        self.async_write_ha_state()


class MainSwitch(_BaseSwitch):
    def __init__(self, controller: Controller, slug: str) -> None:
        super().__init__(controller, slug, SUFFIX_MAIN, "Main")
        self._attr_icon = "mdi:toggle-switch"

    @property
    def is_on(self) -> bool | None:
        return self.controller.main_is_on

    @property
    def available(self) -> bool:
        return self.controller.main_available

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"virtual_switch": True}

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.controller.async_main(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.controller.async_main(False)


class InternalSwitch(_BaseSwitch):
    def __init__(self, controller: Controller, slug: str) -> None:
        super().__init__(controller, slug, SUFFIX_INTERNAL, "Internal")
        self._attr_icon = "mdi:memory"

    @property
    def is_on(self) -> bool:
        return self.controller.internal_state

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.controller.async_internal(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.controller.async_internal(False)
