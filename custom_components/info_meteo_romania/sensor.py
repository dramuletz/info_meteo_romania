"""Senzori pentru Info Meteo Romania."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MeteoRomaniaCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _parse_temperature(data):
    """Extrage temperatura - campul 'tempe' din API."""
    weather = data.get("weather", {})
    try:
        return round(float(weather.get("tempe", 0)), 1)
    except (ValueError, TypeError):
        return None


def _parse_humidity(data):
    """Extrage umiditatea - campul 'umezeala' din API."""
    weather = data.get("weather", {})
    try:
        return float(weather.get("umezeala", 0))
    except (ValueError, TypeError):
        return None


def _parse_pressure(data):
    """Extrage presiunea din campul 'presiunetext' ex: '1013.2 mb, in scadere'."""
    weather = data.get("weather", {})
    presiune_text = weather.get("presiunetext", "")
    try:
        return round(float(presiune_text.split(" ")[0]), 1)
    except (ValueError, TypeError, IndexError):
        return None


def _parse_pressure_trend(data):
    """Extrage trendul presiunii din 'presiunetext'."""
    weather = data.get("weather", {})
    presiune_text = weather.get("presiunetext", "")
    parts = presiune_text.split(", ")
    return parts[1] if len(parts) > 1 else None


def _parse_wind_speed(data):
    """Extrage viteza vantului din campul 'vant' ex: '7.0 m/s, directia : ESE'."""
    weather = data.get("weather", {})
    vant_text = weather.get("vant", "")
    try:
        return round(float(vant_text.split(" ")[0]), 1)
    except (ValueError, TypeError, IndexError):
        return None


def _parse_wind_direction(data):
    """Extrage directia vantului din campul 'vant' ex: '7.0 m/s, directia : ESE'."""
    weather = data.get("weather", {})
    vant_text = weather.get("vant", "")
    try:
        return vant_text.split(": ")[1].strip()
    except (IndexError, AttributeError):
        return None


def _parse_cloudiness(data):
    """Extrage nebulozitatea."""
    weather = data.get("weather", {})
    return weather.get("nebulozitate", None)


def _parse_snow(data):
    """Extrage stratul de zapada din campul 'zapada' ex: '177 cm la ora 15'."""
    weather = data.get("weather", {})
    zapada_text = weather.get("zapada", "indisponibil")
    if zapada_text == "indisponibil":
        return None
    try:
        return float(zapada_text.split(" ")[0])
    except (ValueError, TypeError, IndexError):
        return None


def _parse_phenomenon(data):
    """Extrage fenomenul meteo."""
    weather = data.get("weather", {})
    fenomen = weather.get("fenomen_e", "indisponibil")
    return None if fenomen == "indisponibil" else fenomen


def _parse_alerts_count(data):
    """Numarul de alerte active."""
    alerts = data.get("alerts", [])
    return len(alerts) if isinstance(alerts, list) else 0


def _parse_alert_color(data):
    """Culoarea celei mai severe alerte."""
    alerts = data.get("alerts", [])
    if not alerts:
        return "Verde"
    color_priority = {"red": 4, "orange": 3, "yellow": 2, "green": 1}
    color_names = {"red": "Roșu", "orange": "Portocaliu", "yellow": "Galben", "green": "Verde"}
    max_color = "green"
    max_priority = 0
    for alert in alerts:
        if isinstance(alert, dict):
            color = alert.get("color", "green").lower()
            if color_priority.get(color, 0) > max_priority:
                max_priority = color_priority[color]
                max_color = color
    return color_names.get(max_color, "Verde")


def _parse_nowcasting_count(data):
    """Numarul de avertizari nowcasting."""
    nowcasting = data.get("nowcasting", [])
    return len(nowcasting) if isinstance(nowcasting, list) else 0


@dataclass
class MeteoSensorEntityDescription(SensorEntityDescription):
    value_fn: callable = None


SENSOR_TYPES: tuple[MeteoSensorEntityDescription, ...] = (
    MeteoSensorEntityDescription(
        key="temperature",
        name="Temperatură",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        value_fn=_parse_temperature,
    ),
    MeteoSensorEntityDescription(
        key="humidity",
        name="Umiditate Relativă",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
        value_fn=_parse_humidity,
    ),
    MeteoSensorEntityDescription(
        key="pressure",
        name="Presiune Atmosferică",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
        value_fn=_parse_pressure,
    ),
    MeteoSensorEntityDescription(
        key="wind_speed",
        name="Viteza Vântului",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
        value_fn=_parse_wind_speed,
    ),
    MeteoSensorEntityDescription(
        key="wind_direction",
        name="Direcția Vântului",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:compass",
        value_fn=_parse_wind_direction,
    ),
    MeteoSensorEntityDescription(
        key="cloudiness",
        name="Nebulozitate",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:weather-cloudy",
        value_fn=_parse_cloudiness,
    ),
    MeteoSensorEntityDescription(
        key="snow_depth",
        name="Strat Zăpadă",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake",
        value_fn=_parse_snow,
    ),
    MeteoSensorEntityDescription(
        key="phenomenon",
        name="Fenomen Meteo",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:weather-partly-rainy",
        value_fn=_parse_phenomenon,
    ),
    MeteoSensorEntityDescription(
        key="anm_alerts",
        name="Alerte ANM",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:alert-octagon",
        value_fn=_parse_alerts_count,
    ),
    MeteoSensorEntityDescription(
        key="alert_color",
        name="Culoare Alertă ANM",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:alert",
        value_fn=_parse_alert_color,
    ),
    MeteoSensorEntityDescription(
        key="nowcasting_alerts",
        name="Avertizări Nowcasting",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:weather-lightning",
        value_fn=_parse_nowcasting_count,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MeteoRomaniaCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = [
        MeteoRomaniaSensor(coordinator, description, config_entry)
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class MeteoRomaniaSensor(CoordinatorEntity, SensorEntity):
    entity_description: MeteoSensorEntityDescription

    def __init__(self, coordinator, description, config_entry):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        city_display = config_entry.data.get('city_display') or config_entry.data.get('city', '')
        self._attr_name = f"{city_display.title()} {description.name}"
        self._config_entry = config_entry

    @property
    def device_info(self):
        city = self._config_entry.data.get('city_display') or self._config_entry.data.get('city', '')
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": f"Info Meteo România - {city.title()}",
            "manufacturer": "ANM - Administrația Națională de Meteorologie",
            "model": "Stație Meteo",
            "entry_type": "service",
        }

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        attrs = {
            "localitate": self.coordinator.data.get("city"),
            "sursa_date": "ANM - www.meteoromania.ro",
        }
        if self.entity_description.key == "pressure":
            attrs["trend"] = _parse_pressure_trend(self.coordinator.data)
        if self.entity_description.key == "anm_alerts":
            alerts = self.coordinator.data.get("alerts", [])
            if alerts:
                attrs["alerte_detalii"] = [
                    {
                        "tip": a.get("type", ""),
                        "culoare": a.get("color", ""),
                        "start": a.get("start_date", ""),
                        "sfarsit": a.get("end_date", ""),
                        "descriere": a.get("description", ""),
                    }
                    for a in alerts if isinstance(a, dict)
                ]
        return attrs
