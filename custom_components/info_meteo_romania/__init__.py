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

from .const import DOMAIN, SCAN_INTERVAL, WEATHER_API_URL, ALERTS_XML_URL, NOWCASTING_XML_URL, FORECAST_API_URL, CITIES, CITY_COUNTY

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
        self.city_display = (
            entry.data.get("city_display")
            or entry.data.get("city")
            or ""
        )
        city_api_saved = entry.data.get("city_api", "")

        city_info = CITIES.get(self.city_display)
        if city_info:
            self.city_api = city_info[0]
            self.lat = city_info[1]
            self.lon = city_info[2]
        else:
            self.city_api = city_api_saved.upper() if city_api_saved else self.city_display.upper()
            self.lat = None
            self.lon = None

        self.county = CITY_COUNTY.get(self.city_display, "")

        _LOGGER.debug("Coordinator: city=%s, api=%s, lat=%s, lon=%s",
                      self.city_display, self.city_api, self.lat, self.lon)
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(30):
                weather_data = await self._fetch_weather()
                alerts_data = await self._fetch_alerts()
                nowcasting_data = await self._fetch_nowcasting()
                forecast_data = await self._fetch_forecast()

            return {
                "weather": weather_data,
                "alerts": alerts_data,
                "nowcasting": nowcasting_data,
                "forecast": forecast_data,
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
                        if props.get("nume", "").upper() == self.city_api:
                            return props
                    _LOGGER.warning("Statia '%s' nu a fost gasita in API.", self.city_api)
                    return {}
        except Exception as err:
            _LOGGER.error("Eroare fetch weather: %s", err)
            return {}

    async def _fetch_forecast(self):
        """Prognoza 7 zile via Open-Meteo (gratuit, fara API key)."""
        if not self.lat or not self.lon:
            return []
        try:
            url = FORECAST_API_URL.format(lat=self.lat, lon=self.lon)
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    daily = data.get("daily", {})
                    if not daily:
                        return []

                    times = daily.get("time", [])
                    temp_max = daily.get("temperature_2m_max", [])
                    temp_min = daily.get("temperature_2m_min", [])
                    precip_prob = daily.get("precipitation_probability_max", [])
                    weathercodes = daily.get("weathercode", [])
                    wind_max = daily.get("windspeed_10m_max", [])

                    forecasts = []
                    for i, date in enumerate(times):
                        forecasts.append({
                            "date": date,
                            "temp_max": temp_max[i] if i < len(temp_max) else None,
                            "temp_min": temp_min[i] if i < len(temp_min) else None,
                            "precip_prob": precip_prob[i] if i < len(precip_prob) else None,
                            "weathercode": weathercodes[i] if i < len(weathercodes) else 0,
                            "wind_max": wind_max[i] if i < len(wind_max) else None,
                        })
                    return forecasts
        except Exception as err:
            _LOGGER.warning("Eroare fetch forecast Open-Meteo: %s", err)
            return []

    def _filter_by_county(self, warnings: list) -> list:
        """Filtreaza alertele pentru judetul orasului selectat.
        
        Logam continutul alertelor pentru debug si returnam toate alertele active.
        Filtrarea pe judet nu este posibila fara a cunoaste exact structura XML-ului ANM.
        """
        if not warnings:
            return []
        
        for w in warnings:
            if isinstance(w, dict):
                _LOGGER.debug("Alerta ANM gasita: %s", w)
        
        return warnings

    async def _fetch_alerts(self):
        try:
            async with self.session.get(ALERTS_XML_URL) as resp:
                if resp.status == 200:
                    raw = await resp.text()
                    _LOGGER.debug("RAW XML alerte ANM: %s", raw[:2000])
                    parsed = xmltodict.parse(raw)
                    _LOGGER.debug("Parsed XML alerte ANM: %s", parsed)
                    # Incearca toate cheile posibile din XML
                    root = parsed
                    warnings = (
                        root.get("warnings", {}).get("warning") or
                        root.get("alerts", {}).get("alert") or
                        root.get("warning") or
                        root.get("alert") or
                        []
                    )
                    if isinstance(warnings, dict):
                        warnings = [warnings]
                    warnings = warnings if warnings else []
                    _LOGGER.debug("Alerte gasite: %d -> %s", len(warnings), warnings)
                    return self._filter_by_county(warnings)
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
                    warnings = warnings if warnings else []
                    return self._filter_by_county(warnings)
        except Exception as err:
            _LOGGER.warning("Eroare fetch nowcasting: %s", err)
            return []
