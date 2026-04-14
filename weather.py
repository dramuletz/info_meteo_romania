"""Entitate Weather pentru Info Meteo Romania."""
from __future__ import annotations

import logging

from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
    Forecast,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MeteoRomaniaCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONDITION_MAP = {
    "cer senin": "sunny",
    "cer partial noros": "partlycloudy",
    "cer noros": "cloudy",
    "cer acoperit": "cloudy",
    "ploaie": "rainy",
    "averse": "pouring",
    "furtuna": "lightning-rainy",
    "ninsoare": "snowy",
    "lapovita": "snowy-rainy",
    "ceata": "fog",
    "burnita": "rainy",
    "viscol": "snowy",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurează entitatea weather."""
    coordinator: MeteoRomaniaCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MeteoRomaniaWeather(coordinator, config_entry)])


class MeteoRomaniaWeather(CoordinatorEntity, WeatherEntity):
    """Entitate Weather pentru ANM."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    def __init__(
        self,
        coordinator: MeteoRomaniaCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Inițializează entitatea weather."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        city = config_entry.data.get("city", "")
        self._attr_name = f"Meteo {city.title()}"
        self._attr_unique_id = f"{config_entry.entry_id}_weather"

    @property
    def device_info(self):
        """Informații despre dispozitiv."""
        city = self._config_entry.data.get("city", "")
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": f"Info Meteo România - {city.title()}",
            "manufacturer": "ANM - Administrația Națională de Meteorologie",
            "model": "Stație Meteo",
            "entry_type": "service",
        }

    def _get_weather(self):
        """Obține datele meteo curente."""
        if self.coordinator.data:
            return self.coordinator.data.get("weather", {})
        return {}

    @property
    def native_temperature(self):
        """Temperatura curentă."""
        weather = self._get_weather()
        try:
            temp = weather.get("temp") or weather.get("temperatura")
            return float(temp) if temp is not None else None
        except (ValueError, TypeError):
            return None

    @property
    def humidity(self):
        """Umiditatea relativă."""
        weather = self._get_weather()
        try:
            val = weather.get("umezeala") or weather.get("humidity")
            return float(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    @property
    def native_pressure(self):
        """Presiunea atmosferică."""
        weather = self._get_weather()
        try:
            val = weather.get("presiune") or weather.get("pressure")
            return float(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    @property
    def native_wind_speed(self):
        """Viteza vântului."""
        weather = self._get_weather()
        try:
            val = weather.get("vant") or weather.get("wind_speed") or weather.get("ff")
            return float(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    @property
    def wind_bearing(self):
        """Direcția vântului."""
        weather = self._get_weather()
        return weather.get("directie_vant") or weather.get("wind_dir") or weather.get("dd")

    @property
    def condition(self):
        """Condiția meteo curentă."""
        weather = self._get_weather()
        nebulozitate = weather.get("nebulozitate", "").lower()
        
        for ro_condition, ha_condition in CONDITION_MAP.items():
            if ro_condition in nebulozitate:
                return ha_condition
        
        return "cloudy"

    @property
    def attribution(self):
        """Atribuire date."""
        return "Date furnizate de ANM - Administrația Națională de Meteorologie"

    @property
    def extra_state_attributes(self):
        """Atribute extra."""
        weather = self._get_weather()
        alerts = self.coordinator.data.get("alerts", []) if self.coordinator.data else []
        
        attrs = {
            "sursa": "ANM - www.meteoromania.ro",
            "localitate": self.coordinator.data.get("city") if self.coordinator.data else None,
            "numar_alerte_active": len(alerts),
        }
        
        if weather.get("strat_zapada"):
            attrs["strat_zapada_cm"] = weather.get("strat_zapada")
        
        if alerts:
            max_color = "Verde"
            for alert in alerts:
                if isinstance(alert, dict):
                    color = alert.get("color", "").lower()
                    if color == "red":
                        max_color = "Roșu"
                        break
                    elif color == "orange":
                        max_color = "Portocaliu"
                    elif color == "yellow" and max_color == "Verde":
                        max_color = "Galben"
            attrs["culoare_alerta_maxima"] = max_color
        
        return attrs
