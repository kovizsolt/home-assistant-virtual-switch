from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.util import slugify

from .const import CONF_NAME, DOMAIN


class VirtualSwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def _create(self, data: dict[str, Any]):
        name = str(data.get(CONF_NAME, "")).strip()
        if not name:
            return None
        await self.async_set_unique_id(slugify(name))
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=name, data={CONF_NAME: name})

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            result = await self._create(user_input)
            if result is not None:
                return result
            errors["base"] = "name_required"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_NAME): str}),
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, Any]):
        result = await self._create(user_input)
        if result is None:
            return self.async_abort(reason="name_required")
        return result

