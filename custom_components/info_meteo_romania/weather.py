"""Entitate Weather pentru Info Meteo Romania."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

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
    coordinator: MeteoRomaniaCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MeteoRomaniaWeather(coordinator, config_entry)])


class MeteoRomaniaWeather(CoordinatorEntity, WeatherEntity):
    """Entitate Weather pentru ANM."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: MeteoRomaniaCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
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
            "manufacturer": "ANM - Administrația Națională de Meteorologie",
            "model": "Stație Meteo",
            "entry_type": "service",
        }

    def _get_weather(self):
        if self.coordinator.data:
            return self.coordinator.data.get("weather", {})
        return {}

    def _parse_condition(self, nebulozitate: str) -> str:
        neb = nebulozitate.lower()
        for ro_cond, ha_cond in CONDITION_MAP.items():
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
            presiune_text = weather.get("presiunetext", "")
            return round(float(presiune_text.split(" ")[0]), 1)
        except (ValueError, TypeError, IndexError):
            return None

    @property
    def native_wind_speed(self):
        weather = self._get_weather()
        try:
            vant_text = weather.get("vant", "")
            return round(float(vant_text.split(" ")[0]), 1)
        except (ValueError, TypeError, IndexError):
            return None

    @property
    def wind_bearing(self):
        weather = self._get_weather()
        try:
            vant_text = weather.get("vant", "")
            return vant_text.split(": ")[1].strip()
        except (IndexError, AttributeError):
            return None

    @property
    def condition(self):
        weather = self._get_weather()
        nebulozitate = weather.get("nebulozitate", "")
        return self._parse_condition(nebulozitate)

    @property
    def attribution(self):
        return "Date furnizate de ANM - Administrația Națională de Meteorologie"

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Returnează prognoza zilnica - date curente pentru azi."""
        weather = self._get_weather()
        if not weather:
            return None

        today = datetime.now()
        forecasts = []

        # ANM nu ofera prognoza zilnica in API-ul public
        # Afisam datele curente pentru ziua de azi
        try:
            temp = round(float(weather.get("tempe", 0)), 1)
            condition = self._parse_condition(weather.get("nebulozitate", ""))

            forecasts.append(
                Forecast(
                    datetime=today.isoformat(),
                    native_temperature=temp,
                    native_templow=temp,
                    condition=condition,
                    humidity=float(weather.get("umezeala", 0)),
                )
            )
        except (ValueError, TypeError) as err:
            _LOGGER.warning("Eroare la generarea forecast: %s", err)
            return None

        return forecasts

    @property
    def extra_state_attributes(self):
        weather = self._get_weather()
        alerts = self.coordinator.data.get("alerts", []) if self.coordinator.data else []

        attrs = {
            "sursa": "ANM - www.meteoromania.ro",
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
