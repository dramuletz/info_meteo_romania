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


@dataclass
class MeteoSensorEntityDescription(SensorEntityDescription):
    """Descriere senzor meteo cu câmp extra pentru extragere date."""
    value_fn: callable = None


SENSOR_TYPES: tuple[MeteoSensorEntityDescription, ...] = (
    MeteoSensorEntityDescription(
        key="temperature",
        name="Temperatură",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        value_fn=lambda data: _get_weather_value(data, "temp"),
    ),
    MeteoSensorEntityDescription(
        key="humidity",
        name="Umiditate Relativă",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
        value_fn=lambda data: _get_weather_value(data, "umezeala"),
    ),
    MeteoSensorEntityDescription(
        key="pressure",
        name="Presiune Atmosferică",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
        value_fn=lambda data: _get_weather_value(data, "presiune"),
    ),
    MeteoSensorEntityDescription(
        key="wind_speed",
        name="Viteza Vântului",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
        value_fn=lambda data: _get_weather_value(data, "vant"),
    ),
    MeteoSensorEntityDescription(
        key="wind_direction",
        name="Direcția Vântului",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:compass",
        value_fn=lambda data: _get_weather_value(data, "directie_vant"),
    ),
    MeteoSensorEntityDescription(
        key="cloudiness",
        name="Nebulozitate",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:weather-cloudy",
        value_fn=lambda data: _get_weather_value(data, "nebulozitate"),
    ),
    MeteoSensorEntityDescription(
        key="snow_depth",
        name="Strat Zăpadă",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake",
        value_fn=lambda data: _get_weather_value(data, "strat_zapada"),
    ),
    MeteoSensorEntityDescription(
        key="anm_alerts",
        name="Alerte ANM",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:alert-octagon",
        value_fn=lambda data: _get_alerts_count(data),
    ),
    MeteoSensorEntityDescription(
        key="alert_color",
        name="Culoare Alertă ANM",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:alert",
        value_fn=lambda data: _get_alert_color(data),
    ),
    MeteoSensorEntityDescription(
        key="nowcasting_alerts",
        name="Avertizări Nowcasting",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=None,
        icon="mdi:weather-lightning",
        value_fn=lambda data: _get_nowcasting_count(data),
    ),
)


def _get_weather_value(data: dict, key: str) -> Any:
    """Extrage valoare din datele meteo."""
    weather = data.get("weather", {})
    if not weather:
        return None
    
    value = weather.get(key)
    if value is None:
        # Încearcă câmpuri alternative din API
        alt_keys = {
            "temp": ["temperatura", "t"],
            "umezeala": ["humidity", "rh"],
            "presiune": ["pressure", "p"],
            "vant": ["wind_speed", "ff"],
            "directie_vant": ["wind_dir", "dd"],
            "nebulozitate": ["clouds", "neb"],
            "strat_zapada": ["snow", "snow_depth"],
        }
        for alt in alt_keys.get(key, []):
            value = weather.get(alt)
            if value is not None:
                break
    
    try:
        return round(float(value), 1) if value is not None else None
    except (ValueError, TypeError):
        return value


def _get_alerts_count(data: dict) -> int:
    """Returnează numărul de alerte active."""
    alerts = data.get("alerts", [])
    return len(alerts) if isinstance(alerts, list) else 0


def _get_alert_color(data: dict) -> str:
    """Returnează culoarea celei mai severe alerte active."""
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


def _get_nowcasting_count(data: dict) -> int:
    """Returnează numărul avertizărilor nowcasting."""
    nowcasting = data.get("nowcasting", [])
    return len(nowcasting) if isinstance(nowcasting, list) else 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurează senzorii."""
    coordinator: MeteoRomaniaCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        MeteoRomaniaSensor(coordinator, description, config_entry)
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class MeteoRomaniaSensor(CoordinatorEntity, SensorEntity):
    """Senzor pentru Info Meteo Romania."""

    entity_description: MeteoSensorEntityDescription

    def __init__(
        self,
        coordinator: MeteoRomaniaCoordinator,
        description: MeteoSensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Inițializează senzorul."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_name = f"{config_entry.data['city'].title()} {description.name}"
        self._config_entry = config_entry

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

    @property
    def native_value(self):
        """Returnează valoarea senzorului."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Atribute extra."""
        if self.coordinator.data is None:
            return {}

        attrs = {
            "localitate": self.coordinator.data.get("city"),
            "ultima_actualizare": self.coordinator.last_update_success_time,
            "sursa_date": "ANM - www.meteoromania.ro",
        }

        # Adaugă detalii alerte
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
                        "judet": a.get("county", ""),
                    }
                    for a in alerts if isinstance(a, dict)
                ]

        if self.entity_description.key == "nowcasting_alerts":
            nowcasting = self.coordinator.data.get("nowcasting", [])
            if nowcasting:
                attrs["nowcasting_detalii"] = nowcasting[:5]  # primele 5

        return attrs
