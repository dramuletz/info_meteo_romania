# Info Meteo Romania 🌦️

<div align="center">

![Logo](https://www.meteoromania.ro/wp-content/uploads/2016/07/logo-meteo2.png)

**Integrare oficială ANM pentru Home Assistant**

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://github.com/hacs/integration)
[![Release](https://img.shields.io/github/v/release/dramuletz/info_meteo_romania?style=for-the-badge&color=blue)](https://github.com/dramuletz/info_meteo_romania/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![HA](https://img.shields.io/badge/Home%20Assistant-2023.1+-41BDF5?style=for-the-badge&logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)

</div>

---

## Despre integrare

Date meteo oficiale de la **ANM – Administrația Națională de Meteorologie** direct în Home Assistant. Alerte, avertizări și starea vremii pentru **72+ localități** din România, actualizate automat la fiecare 30 de minute.

---

## Funcționalități

| | |
|---|---|
| 🌡️ Temperatură, umiditate, presiune | ⛈️ Avertizări Nowcasting |
| 💨 Viteză și direcție vânt | 🗺️ 72+ localități disponibile |
| ☁️ Nebulozitate | 🔄 Actualizare automată 30 min |
| ❄️ Strat de zăpadă | 🟡 Alerte ANM (Verde/Galben/Portocaliu/Roșu) |

---

## Instalare via HACS

**1.** Deschide HACS → Integrations → ⋮ → **Custom repositories**

**2.** Adaugă: `https://github.com/dramuletz/info_meteo_romania` → categorie **Integration**

**3.** Caută **Info Meteo Romania** și instalează

**4.** Repornește Home Assistant

---

## Configurare

1. **Settings** → **Devices & Services** → **Add Integration**
2. Caută **Info Meteo Romania**
3. Selectează **localitatea** din lista dropdown
4. Click **Submit** ✅

> Poți adăuga **mai multe localități** repetând procesul.

---

## Entități create

Pentru fiecare localitate configurată:

| Entitate | Descriere |
|----------|-----------|
| `weather.meteo_[localitate]` | Card meteo complet |
| `sensor.[localitate]_temperatura` | Temperatura în °C |
| `sensor.[localitate]_umiditate_relativa` | Umiditate în % |
| `sensor.[localitate]_presiune_atmosferica` | Presiune în hPa |
| `sensor.[localitate]_viteza_vantului` | Vânt în m/s |
| `sensor.[localitate]_directia_vantului` | Direcția vântului |
| `sensor.[localitate]_nebulozitate` | Starea cerului |
| `sensor.[localitate]_strat_zapada` | Zăpadă în cm |
| `sensor.[localitate]_alerte_anm` | Număr alerte active |
| `sensor.[localitate]_culoare_alerta_anm` | Severitatea alertei |
| `sensor.[localitate]_avertizari_nowcasting` | Avertizări imediate |

---

## Exemple de utilizare

### Card 1 — Glance Card — date rapide

Afișează compact cele mai importante date meteo pe un singur rând.

```yaml
type: glance
title: 🌦️ Meteo Brașov
entities:
  - entity: sensor.brasov_temperature
    name: Temperatură
  - entity: sensor.brasov_humidity
    name: Umiditate
  - entity: sensor.brasov_wind_speed
    name: Vânt
  - entity: sensor.brasov_pressure
    name: Presiune
  - entity: sensor.brasov_alert_color
    name: Alertă ANM
```

---

### Card 2 — Entities Card — panou detaliat cu senzori

Afișează toți senzorii și alertele ANM într-un singur card.

```yaml
type: entities
title: 🌦️ Meteo Brașov - ANM
entities:
  - entity: sensor.brasov_temperature
    name: Temperatură
    icon: mdi:thermometer
  - entity: sensor.brasov_humidity
    name: Umiditate
    icon: mdi:water-percent
  - entity: sensor.brasov_pressure
    name: Presiune
    icon: mdi:gauge
  - entity: sensor.brasov_wind_speed
    name: Vânt
    icon: mdi:weather-windy
  - entity: sensor.brasov_wind_direction
    name: Direcție vânt
    icon: mdi:compass
  - entity: sensor.brasov_cloudiness
    name: Nebulozitate
    icon: mdi:weather-cloudy
  - entity: sensor.brasov_snow_depth
    name: Strat zăpadă
    icon: mdi:snowflake
  - type: divider
  - entity: sensor.brasov_anm_alerts
    name: Alerte ANM active
    icon: mdi:alert-octagon
  - entity: sensor.brasov_alert_color
    name: Severitate alertă
    icon: mdi:alert
  - entity: sensor.brasov_nowcasting_alerts
    name: Avertizări Nowcasting
    icon: mdi:weather-lightning
```

---

### Card 4 — Markdown Card — panou complet cu alerte

Afișează toate datele și alertele ANM într-un format personalizat.

```yaml
type: markdown
title: 🌦️ Meteo Brașov - ANM
content: >
  ### 🌡️ Condiții actuale

  **Temperatură:** {{ states('sensor.brasov_temperature') }} °C

  **Umiditate:** {{ states('sensor.brasov_humidity') }} %

  **Presiune:** {{ states('sensor.brasov_pressure') }} hPa

  **Vânt:** {{ states('sensor.brasov_wind_speed') }} m/s
  {{ states('sensor.brasov_wind_direction') }}

  **Nebulozitate:** {{ states('sensor.brasov_cloudiness') }}

  ---

  ### 🚨 Alerte ANM

  **Alerte active:** {{ states('sensor.brasov_anm_alerts') }}

  **Severitate:** {{ states('sensor.brasov_alert_color') }}

  **Avertizări Nowcasting:** {{ states('sensor.brasov_nowcasting_alerts') }}
```

---

## Exemple de automatizări

### Automatizare 1 — Notificare la alertă ANM activă

Trimite o notificare pe telefon când ANM emite o alertă galbenă, portocalie sau roșie în zona ta.

```yaml
alias: "🚨 Alertă ANM Brașov"
description: "Notificare când apare o alertă ANM activă"
trigger:
  - platform: state
    entity_id: sensor.brasov_alert_color
    to:
      - "Galben"
      - "Portocaliu"
      - "Roșu"
condition: []
action:
  - service: notify.mobile_app_telefonul_meu
    data:
      title: "⚠️ Alertă Meteo ANM - Brașov"
      message: >
        🟡 Alertă {{ states('sensor.brasov_alert_color') }} activă în zona Brașov!

        {% set alerte = state_attr('sensor.brasov_anm_alerts', 'alerte_detalii') %}
        {% if alerte %}
          {% for alerta in alerte %}
          📌 Tip: {{ alerta.tip }}
          📝 {{ alerta.descriere }}
          🕐 Valabilă: {{ alerta.start }} - {{ alerta.sfarsit }}
          {% endfor %}
        {% endif %}
      data:
        importance: high
        color: >
          {% if states('sensor.brasov_alert_color') == 'Roșu' %}
            red
          {% elif states('sensor.brasov_alert_color') == 'Portocaliu' %}
            orange
          {% else %}
            yellow
          {% endif %}
mode: single
```

---

### Automatizare 2 — Notificare la temperaturi extreme

Trimite o notificare când temperatura depășește 35°C sau scade sub -10°C.

```yaml
alias: "🌡️ Temperatură extremă Brașov"
description: "Notificare la temperaturi extreme"
trigger:
  - platform: numeric_state
    entity_id: sensor.brasov_temperature
    above: 35
    id: "cald"
  - platform: numeric_state
    entity_id: sensor.brasov_temperature
    below: -10
    id: "frig"
condition: []
action:
  - service: notify.mobile_app_telefonul_meu
    data:
      title: >
        {% if trigger.id == 'cald' %}
          🥵 Caniculă în Brașov!
        {% else %}
          🥶 Ger extrem în Brașov!
        {% endif %}
      message: >
        Temperatura actuală: {{ states('sensor.brasov_temperature') }} °C
        {% if trigger.id == 'cald' %}
          Rămâi hidratat și evită expunerea la soare!
        {% else %}
          Îmbracă-te corespunzător!
        {% endif %}
mode: single
```

> 💡 Înlocuiește `brasov` cu slug-ul localității tale și `mobile_app_telefonul_meu` cu numele serviciului tău de notificări.

---

## Surse de date

Datele sunt preluate direct de pe serverele oficiale ANM:

- 🌐 [www.meteoromania.ro](https://www.meteoromania.ro/)
- 📡 API Starea Vremii
- 📋 XML Alerte ANM
- ⚡ XML Nowcasting

---

<div align="center">

Dezvoltat cu ❤️ pentru comunitatea Home Assistant din România

</div>
