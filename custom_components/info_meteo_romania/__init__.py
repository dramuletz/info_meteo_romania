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

from .const import DOMAIN, SCAN_INTERVAL, WEATHER_API_URL, ALERTS_XML_URL, NOWCASTING_XML_URL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.WEATHER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurează integrarea din config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = MeteoRomaniaCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Dezinstalează o intrare de configurare."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class MeteoRomaniaCoordinator(DataUpdateCoordinator):
    """Coordinator pentru actualizarea datelor meteo."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Inițializează coordinatorul."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL),
        )
        self.entry = entry
        self.city = entry.data.get("city")
        self.city_id = entry.data.get("city_id")
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self):
        """Obține datele de la ANM."""
        try:
            async with async_timeout.timeout(30):
                weather_data = await self._fetch_weather()
                alerts_data = await self._fetch_alerts()
                nowcasting_data = await self._fetch_nowcasting()

            return {
                "weather": weather_data,
                "alerts": alerts_data,
                "nowcasting": nowcasting_data,
                "city": self.city,
                "city_id": self.city_id,
            }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Eroare la comunicarea cu ANM: {err}") from err

    async def _fetch_weather(self):
        """Obține starea curentă a vremii."""
        try:
            async with self.session.get(WEATHER_API_URL) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    all_stations = data.get("list", [])
                    # Filtrează pentru orașul selectat
                    for station in all_stations:
                        if str(station.get("id")) == str(self.city_id):
                            return station
                        if station.get("nume", "").upper() == self.city.upper():
                            return station
                    # Dacă nu găsim exact, returnăm primul disponibil
                    return all_stations[0] if all_stations else {}
        except Exception as err:
            _LOGGER.warning("Nu s-au putut obține datele meteo: %s", err)
            return {}

    async def _fetch_alerts(self):
        """Obține avertizările ANM active."""
        try:
            async with self.session.get(ALERTS_XML_URL) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    parsed = xmltodict.parse(content)
                    warnings = parsed.get("warnings", {}).get("warning", [])
                    if isinstance(warnings, dict):
                        warnings = [warnings]
                    return warnings
        except Exception as err:
            _LOGGER.warning("Nu s-au putut obține avertizările: %s", err)
            return []

    async def _fetch_nowcasting(self):
        """Obține avertizările nowcasting."""
        try:
            async with self.session.get(NOWCASTING_XML_URL) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    parsed = xmltodict.parse(content)
                    warnings = parsed.get("warnings", {}).get("warning", [])
                    if isinstance(warnings, dict):
                        warnings = [warnings]
                    return warnings
        except Exception as err:
            _LOGGER.warning("Nu s-au putut obține nowcasting: %s", err)
            return []
