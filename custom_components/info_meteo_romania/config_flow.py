"""Config flow pentru Info Meteo Romania."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CITIES

_LOGGER = logging.getLogger(__name__)


class InfoMeteoRomaniaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestionează configurarea Info Meteo Romania."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            city_display = user_input["city"]
            city_info = CITIES.get(city_display)
            if city_info:
                city_api = city_info[0]
            else:
                city_api = city_display.upper()

            await self.async_set_unique_id(
                f"{DOMAIN}_{city_display.lower().replace(' ', '_')}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Info Meteo Romania - {city_display}",
                data={
                    "city_display": city_display,
                    "city_api": city_api,
                },
            )

        sorted_cities = sorted(CITIES.keys(), key=lambda x: x.lower())

        schema = vol.Schema(
            {
                vol.Required("city"): vol.In(sorted_cities),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "total_cities": str(len(CITIES)),
            },
        )


class InfoMeteoRomaniaOptionsFlow(config_entries.OptionsFlow):

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "scan_interval",
                        default=self.config_entry.options.get("scan_interval", 30),
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=120)),
                }
            ),
        )
