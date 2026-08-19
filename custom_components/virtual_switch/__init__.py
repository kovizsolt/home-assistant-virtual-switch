from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import storage
from homeassistant.loader import async_get_integration
from homeassistant.util import slugify

from .const import (
    CARD_FILENAME,
    CARD_URL,
    DOMAIN,
    PLATFORMS,
    STORE_KEY,
    STORE_VERSION,
    SUFFIX_ONLINE,
)
from .controller import Controller

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    card_path = Path(__file__).parent / "www" / CARD_FILENAME
    integration = await async_get_integration(hass, DOMAIN)
    resource_url = f"{CARD_URL}?v={integration.version}"
    await hass.http.async_register_static_paths([StaticPathConfig(CARD_URL, str(card_path), False)])
    resources = hass.data[LOVELACE_DATA].resources
    if isinstance(resources, ResourceStorageCollection):
        await resources.async_get_info()
        existing = next(
            (item for item in resources.async_items() if item.get("url", "").split("?", 1)[0] == CARD_URL),
            None,
        )
        if existing is None:
            await resources.async_create_item({"res_type": "module", "url": resource_url})
        elif existing.get("url") != resource_url:
            await resources.async_update_item(existing["id"], {"res_type": "module", "url": resource_url})
    else:
        _LOGGER.warning("Lovelace YAML resource mode is active; add %s as a module resource", CARD_URL)
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    slug = slugify(entry.title)
    controller = Controller(hass, entry)
    await controller.async_setup()
    entity_registry = er.async_get(hass)
    legacy_online_entity = entity_registry.async_get_entity_id(
        "switch", DOMAIN, f"{entry.entry_id}_{SUFFIX_ONLINE}"
    )
    if legacy_online_entity is not None:
        entity_registry.async_remove(legacy_online_entity)
    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="Virtual Switch",
        model="Simulated switch with connectivity",
    )
    hass.data[DOMAIN][entry.entry_id] = {"controller": controller, "slug": slug}
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    store = storage.Store(hass, STORE_VERSION, f"{DOMAIN}/{entry.entry_id}/{STORE_KEY}.json")
    await store.async_remove()
