"""Config flow pentru Info Meteo Romania."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CITIES

_LOGGER = logging.getLogger(__name__)


def _find_city(user_input: str) -> str | None:
    """Cauta orasul dupa nume, case-insensitive."""
    user_input = user_input.strip()
    # Match exact
    for city in CITIES:
        if city.lower() == user_input.lower():
            return city
    # Match partial - inceput de cuvant
    matches = [city for city in CITIES if city.lower().startswith(user_input.lower())]
    if len(matches) == 1:
        return matches[0]
    return None


class InfoMeteoRomaniaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestionează configurarea Info Meteo Romania."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        description_placeholders = {}

        if user_input is not None:
            typed = user_input.get("city", "").strip()
            city_display = _find_city(typed)

            if not city_display:
                # Cauta sugestii
                matches = [
                    city for city in CITIES
                    if typed.lower() in city.lower()
                ]
                if matches:
                    description_placeholders["suggestions"] = ", ".join(matches[:5])
                    errors["city"] = "city_not_found_suggestions"
                else:
                    errors["city"] = "city_not_found"
            else:
                city_api = CITIES[city_display][0]

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

        schema = vol.Schema(
            {
                vol.Required("city"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "total_cities": str(len(CITIES)),
                **description_placeholders,
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
