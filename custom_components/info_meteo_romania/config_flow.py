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
        """Pasul inițial de configurare - selectarea localității."""
        errors: dict[str, str] = {}

        if user_input is not None:
            city_name = user_input["city"]
            city_id = CITIES.get(city_name, 0)

            # Verifică dacă integrarea pentru acest oraș există deja
            await self.async_set_unique_id(f"{DOMAIN}_{city_name.lower().replace(' ', '_')}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Meteo {city_name.title()}",
                data={
                    "city": city_name,
                    "city_id": city_id,
                },
            )

        # Sortează orașele alfabetic pentru dropdown
        sorted_cities = sorted(CITIES.keys())

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

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Returnează options flow."""
        return InfoMeteoRomaniaOptionsFlow(config_entry)


class InfoMeteoRomaniaOptionsFlow(config_entries.OptionsFlow):
    """Gestionează opțiunile integrării."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Inițializează options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Gestionează opțiunile."""
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
