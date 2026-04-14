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

## Exemplu Dashboard

```yaml
type: weather-forecast
entity: weather.meteo_brasov
forecast_type: daily
```

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
