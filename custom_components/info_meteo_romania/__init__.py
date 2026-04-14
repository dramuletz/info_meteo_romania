"""Info Meteo Romania - Integrare Home Assistant pentru date ANM."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
import async_timeout
import xmltodict
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL, WEATHER_API_URL, ALERTS_XML_URL, NOWCASTING_XML_URL, CITIES

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.WEATHER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    coordinator = MeteoRomaniaCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class MeteoRomaniaCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL),
        )
        self.entry = entry

        # Compatibilitate cu versiunile vechi si noi ale config entry
        # Versiune noua: city_display + city_api
        # Versiune veche: city
        self.city_display = (
            entry.data.get("city_display")
            or entry.data.get("city")
            or ""
        )
        city_api_saved = entry.data.get("city_api", "")

        # Daca city_api nu e salvat, il cautam in CITIES dupa city_display
        if city_api_saved:
            self.city_api = city_api_saved.upper()
        else:
            self.city_api = CITIES.get(self.city_display, self.city_display.upper())

        _LOGGER.debug("Coordinator init: city_display=%s, city_api=%s", self.city_display, self.city_api)
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(30):
                weather_data = await self._fetch_weather()
                alerts_data = await self._fetch_alerts()
                nowcasting_data = await self._fetch_nowcasting()

            return {
                "weather": weather_data,
                "alerts": alerts_data,
                "nowcasting": nowcasting_data,
                "city": self.city_display,
            }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Eroare la comunicarea cu ANM: {err}") from err

    async def _fetch_weather(self):
        try:
            async with self.session.get(WEATHER_API_URL) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    features = data.get("features", [])

                    for feature in features:
                        props = feature.get("properties", {})
                        station_name = props.get("nume", "").upper()
                        if station_name == self.city_api:
                            _LOGGER.debug("Date gasite pentru %s: %s", self.city_api, props)
                            return props

                    _LOGGER.warning(
                        "Statia '%s' nu a fost gasita. Statii disponibile: %s",
                        self.city_api,
                        [f.get("properties", {}).get("nume") for f in features[:10]]
                    )
                    return {}
        except Exception as err:
            _LOGGER.error("Eroare fetch weather: %s", err)
            return {}

    async def _fetch_alerts(self):
        try:
            async with self.session.get(ALERTS_XML_URL) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    parsed = xmltodict.parse(content)
                    warnings = parsed.get("warnings", {}).get("warning", [])
                    if isinstance(warnings, dict):
                        warnings = [warnings]
                    return warnings if warnings else []
        except Exception as err:
            _LOGGER.warning("Eroare fetch alerte: %s", err)
            return []

    async def _fetch_nowcasting(self):
        try:
            async with self.session.get(NOWCASTING_XML_URL) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    parsed = xmltodict.parse(content)
                    warnings = parsed.get("warnings", {}).get("warning", [])
                    if isinstance(warnings, dict):
                        warnings = [warnings]
                    return warnings if warnings else []
        except Exception as err:
            _LOGGER.warning("Eroare fetch nowcasting: %s", err)
            return []
