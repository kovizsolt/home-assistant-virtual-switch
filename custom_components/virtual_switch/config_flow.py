from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig
from homeassistant.util import slugify

from .const import CONF_CUSTOM_STATUSES, CONF_NAME, DOMAIN
from .state import build_status_definitions


def _status_lines(value: Any) -> list[str]:
    """Normalize the multiline UI value (and tolerate previously stored lists)."""
    values = value if isinstance(value, list) else str(value or "").splitlines()
    return [line for item in values if (line := str(item).strip())]


class VirtualSwitchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return VirtualSwitchOptionsFlow(config_entry)

    async def _create(self, data: dict[str, Any]):
        name = str(data.get(CONF_NAME, "")).strip()
        if not name:
            return None
        await self.async_set_unique_id(slugify(name))
        self._abort_if_unique_id_configured()
        custom_statuses = _status_lines(data.get(CONF_CUSTOM_STATUSES, []))
        build_status_definitions(custom_statuses)
        return self.async_create_entry(
            title=name, data={CONF_NAME: name, CONF_CUSTOM_STATUSES: custom_statuses}
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                result = await self._create(user_input)
                if result is not None:
                    return result
                errors["base"] = "name_required"
            except ValueError:
                errors["base"] = "invalid_custom_statuses"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Optional(CONF_CUSTOM_STATUSES, default=""): TextSelector(
                        TextSelectorConfig(multiline=True)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, Any]):
        try:
            result = await self._create(user_input)
        except ValueError:
            return self.async_abort(reason="invalid_custom_statuses")
        if result is None:
            return self.async_abort(reason="name_required")
        return result


class VirtualSwitchOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._custom_statuses = _status_lines(
            config_entry.options.get(
                CONF_CUSTOM_STATUSES, config_entry.data.get(CONF_CUSTOM_STATUSES, [])
            )
        )

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            custom_statuses = _status_lines(user_input.get(CONF_CUSTOM_STATUSES, ""))
            try:
                build_status_definitions(custom_statuses)
            except ValueError:
                errors["base"] = "invalid_custom_statuses"
            else:
                return self.async_create_entry(
                    title="", data={CONF_CUSTOM_STATUSES: custom_statuses}
                )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_CUSTOM_STATUSES, default="\n".join(self._custom_statuses)
                    ): TextSelector(TextSelectorConfig(multiline=True))
                }
            ),
            errors=errors,
        )
