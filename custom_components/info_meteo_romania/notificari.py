from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = "info_meteo_romania_notificari"

EVENT_NOTIFICARE = "info_meteo_romania_notificare"

COLOR_PRIORITY = {"rosu": 3, "portocaliu": 2, "galben": 1, "verde": 0}
COLOR_EMOJI = {"rosu": "🔴", "portocaliu": "🟠", "galben": "🟡", "verde": "🟢"}
COLOR_NAMES = {"rosu": "Roșu", "portocaliu": "Portocaliu", "galben": "Galben", "verde": "Verde"}


class ManagerNotificari:
    def __init__(self, hass: HomeAssistant, city: str, entry_id: str) -> None:
        self.hass = hass
        self.city = city
        self.entry_id = entry_id
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry_id}")
        self._alerte_notificate: set[str] = set()
        self._lock = asyncio.Lock()

    async def async_incarca(self) -> None:
        """Incarca starea salvata din storage."""
        data = await self._store.async_load()
        if not data:
            return
        self._alerte_notificate = set(data.get("notificate", []))

    async def _salveaza(self) -> None:
        """Salveaza starea curenta in storage."""
        await self._store.async_save(
            {"notificate": sorted(self._alerte_notificate)}
        )

    async def proceseaza(self, alerts: list[dict[str, Any]]) -> None:
        """Proceseaza alertele ANM si trimite notificari daca e cazul."""
        async with self._lock:
            notification_id = f"info_meteo_romania_{self.entry_id}"

            if not alerts:
                # Nu exista alerte - sterge notificarea daca exista
                persistent_notification.async_dismiss(
                    self.hass,
                    notification_id=notification_id,
                )
                self._alerte_notificate.clear()
                await self._salveaza()
                return

            # Determina culoarea maxima
            max_color = "verde"
            for alert in alerts:
                if isinstance(alert, dict):
                    c = alert.get("culoare", "verde").lower()
                    if COLOR_PRIORITY.get(c, 0) > COLOR_PRIORITY.get(max_color, 0):
                        max_color = c

            # Construieste cheia unica pentru aceasta combinatie de alerte
            alert_key = "_".join(
                sorted([
                    f"{a.get('tip', '')}_{a.get('start', '')}_{a.get('sfarsit', '')}"
                    for a in alerts if isinstance(a, dict)
                ])
            )

            # Trimite notificarea doar daca e o alerta noua
            if alert_key not in self._alerte_notificate:
                await self._trimite_alerta(
                    alerts=alerts,
                    max_color=max_color,
                    notification_id=notification_id,
                    alert_key=alert_key,
                )
                self._alerte_notificate = {alert_key}
                await self._salveaza()
            else:
                # Actualizeaza notificarea existenta (datele pot fi schimbate)
                await self._trimite_alerta(
                    alerts=alerts,
                    max_color=max_color,
                    notification_id=notification_id,
                    alert_key=alert_key,
                )

    async def _trimite_alerta(
        self,
        alerts: list[dict[str, Any]],
        max_color: str,
        notification_id: str,
        alert_key: str,
    ) -> None:
        """Trimite notificarea persistenta in Home Assistant."""
        emoji = COLOR_EMOJI.get(max_color, "🟡")
        color_name = COLOR_NAMES.get(max_color, max_color)
        title = f"{emoji} Alertă ANM {color_name} - {self.city}"

        lines = []
        for alert in alerts:
            if not isinstance(alert, dict):
                continue
            tip = alert.get("tip", "")
            fenomene = alert.get("fenomene", "")
            interval = alert.get("interval", "")
            mesaj = alert.get("mesaj", "")

            if tip:
                lines.append(f"**{tip}**")
            if fenomene and fenomene != "conform textelor;":
                lines.append(f"⚡ {fenomene}")
            if interval and interval != "conform textelor;":
                lines.append(f"🕐 {interval}")
            if mesaj:
                lines.append(mesaj[:800])
            lines.append("---")

        message = "\n\n".join(lines) if lines else f"Alertă meteo activă în zona {self.city}."

        _LOGGER.debug("Notificare ANM %s: %s", max_color, title)

        persistent_notification.async_create(
            self.hass,
            message,
            title=title,
            notification_id=notification_id,
        )

        self.hass.bus.async_fire(
            EVENT_NOTIFICARE,
            {
                "tip": max_color,
                "titlu": title,
                "mesaj": message,
                "oras": self.city,
                "numar_alerte": len(alerts),
            },
        )
