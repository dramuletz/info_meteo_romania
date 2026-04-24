"""Entitate Weather pentru Info Meteo Romania."""
from __future__ import annotations

import logging
from datetime import datetime

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

# WMO Weather Code -> HA condition
# https://open-meteo.com/en/docs#weathervariables
WMO_CONDITION_MAP = {
    0: "sunny",
    1: "sunny",
    2: "partlycloudy",
    3: "cloudy",
    45: "fog",
    48: "fog",
    51: "rainy",
    53: "rainy",
    55: "rainy",
    61: "rainy",
    63: "rainy",
    65: "pouring",
    71: "snowy",
    73: "snowy",
    75: "snowy",
    77: "snowy",
    80: "rainy",
    81: "pouring",
    82: "pouring",
    85: "snowy-rainy",
    86: "snowy",
    95: "lightning-rainy",
    96: "lightning-rainy",
    99: "lightning-rainy",
}

ANM_CONDITION_MAP = {
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
    coordinator: MeteoRomaniaCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MeteoRomaniaWeather(coordinator, config_entry)])


class MeteoRomaniaWeather(CoordinatorEntity, WeatherEntity):

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._config_entry = config_entry
        city = config_entry.data.get("city_display") or config_entry.data.get("city", "")
        city_slug = city.lower().replace(" ", "_").replace("ă", "a").replace("â", "a").replace("î", "i").replace("ș", "s").replace("ț", "t").replace("ş", "s").replace("ţ", "t")
        self._attr_unique_id = f"{config_entry.entry_id}_weather"
        self.entity_id = f"weather.{city_slug}"

    @property
    def device_info(self):
        city = self._config_entry.data.get("city_display") or self._config_entry.data.get("city", "")
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": f"Info Meteo România - {city.title()}",
            "manufacturer": "Stefan Dram (dramuletz)",
            "model": "ANM - Administrația Națională de Meteorologie - date oficiale",
            "entry_type": "service",
        }

    def _get_weather(self):
        if self.coordinator.data:
            return self.coordinator.data.get("weather", {})
        return {}

    def _anm_condition(self, nebulozitate: str) -> str:
        neb = nebulozitate.lower()
        for ro_cond, ha_cond in ANM_CONDITION_MAP.items():
            if ro_cond in neb:
                return ha_cond
        return "cloudy"

    @property
    def native_temperature(self):
        weather = self._get_weather()
        try:
            return round(float(weather.get("tempe", 0)), 1)
        except (ValueError, TypeError):
            return None

    @property
    def humidity(self):
        weather = self._get_weather()
        try:
            return float(weather.get("umezeala", 0))
        except (ValueError, TypeError):
            return None

    @property
    def native_pressure(self):
        weather = self._get_weather()
        try:
            return round(float(weather.get("presiunetext", "0").split(" ")[0]), 1)
        except (ValueError, TypeError, IndexError):
            return None

    @property
    def native_wind_speed(self):
        """Viteza vantului in km/h (Open-Meteo returneaza km/h)."""
        weather = self._get_weather()
        try:
            vant_text = weather.get("vant", "")
            ms = float(vant_text.split(" ")[0])
            return round(ms * 3.6, 1)
        except (ValueError, TypeError, IndexError):
            return None

    @property
    def wind_bearing(self):
        weather = self._get_weather()
        try:
            return weather.get("vant", "").split(": ")[1].strip()
        except (IndexError, AttributeError):
            return None

    @property
    def condition(self):
        weather = self._get_weather()
        return self._anm_condition(weather.get("nebulozitate", ""))

    @property
    def attribution(self):
        return "Date curente: ANM | Prognoză: Open-Meteo"

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Prognoza 7 zile din Open-Meteo."""
        if not self.coordinator.data:
            return None

        forecast_data = self.coordinator.data.get("forecast", [])
        if not forecast_data:
            return None

        forecasts = []
        for day in forecast_data:
            try:
                wmo_code = int(day.get("weathercode", 0))
                condition = WMO_CONDITION_MAP.get(wmo_code, "cloudy")
                date_str = day.get("date", "")
                dt = datetime.strptime(date_str, "%Y-%m-%d")

                forecasts.append(
                    Forecast(
                        datetime=dt.isoformat(),
                        native_temperature=day.get("temp_max"),
                        native_templow=day.get("temp_min"),
                        condition=condition,
                        precipitation_probability=day.get("precip_prob"),
                        native_wind_speed=day.get("wind_max"),
                    )
                )
            except (ValueError, TypeError) as err:
                _LOGGER.warning("Eroare la procesarea forecast zi: %s", err)
                continue

        return forecasts if forecasts else None

    @property
    def extra_state_attributes(self):
        weather = self._get_weather()
        alerts = self.coordinator.data.get("alerts", []) if self.coordinator.data else []

        attrs = {
            "sursa_date_curente": "ANM - www.meteoromania.ro",
            "sursa_prognoza": "Open-Meteo - open-meteo.com",
            "localitate": self.coordinator.data.get("city") if self.coordinator.data else None,
            "numar_alerte_active": len(alerts),
            "actualizat": weather.get("actualizat", "").replace("&nbsp;", " "),
        }

        zapada = weather.get("zapada", "indisponibil")
        if zapada and zapada != "indisponibil":
            attrs["strat_zapada"] = zapada

        fenomen = weather.get("fenomen_e", "indisponibil")
        if fenomen and fenomen != "indisponibil":
            attrs["fenomen_meteo"] = fenomen

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
