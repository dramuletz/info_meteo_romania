# 🏠 Exemple Lovelace — Info Meteo Romania

Această pagină conține exemple de carduri și automatizări pentru integrarea **Info Meteo Romania**.

> ⚠️ **Important:** În toate exemplele de mai jos, înlocuiește `<oras>` cu slug-ul localității tale.
>
> **Cum obții slug-ul localității?**
> Slug-ul se formează din numele localității scris cu litere mici, fără diacritice și cu `_` în loc de spații.
>
> | Localitate | Slug |
> |-----------|------|
> | Brașov | `brasov` |
> | Cluj-Napoca | `cluj_napoca` |
> | Timișoara | `timisoara` |
> | București Băneasa | `bucuresti_baneasa` |
> | Târgu Mureș | `targu_mures` |

---

## 📋 Cuprins

- [Cum adaugi un card](#cum-adaugi-un-card)
- [Card 1 — Glance Card](#card-1--glance-card)
- [Card 2 — Entities Card](#card-2--entities-card)
- [Card 3 — Markdown Card](#card-3--markdown-card)
- [Card 4 — Alertă ANM cu culoare](#card-4--alertă-anm-cu-culoare)
- [Automatizări](#automatizări)

---

## Cum adaugi un card

1. Mergi în **Home Assistant** → **Dashboard**
2. Click pe cele **3 puncte** din dreapta sus → **Edit Dashboard**
3. Click pe **"+ Add Card"**
4. Alege **"Manual"** (din josul listei)
5. Șterge conținutul existent și **lipește codul YAML** al cardului dorit
6. Înlocuiește `<oras>` cu slug-ul tău
7. Click **Save**

---

## Card 1 — Glance Card

Afișează compact cele mai importante date meteo pe un singur rând. Ideal pentru un overview rapid.

### Instalare

Nu necesită carduri extra — este un card nativ Home Assistant.

### Cod YAML

```yaml
type: glance
title: 🌦️ Meteo <oras>
entities:
  - entity: sensor.<oras>_temperature
    name: Temperatură
  - entity: sensor.<oras>_humidity
    name: Umiditate
  - entity: sensor.<oras>_wind_speed
    name: Vânt
  - entity: sensor.<oras>_pressure
    name: Presiune
  - entity: sensor.<oras>_alert_color
    name: Alertă ANM
```

### Personalizare

- Poți adăuga sau elimina entități din lista `entities`
- Poți schimba `title` cu orice text dorești
- Poți adăuga `show_state: false` pe orice entitate pentru a ascunde valoarea

---

## Card 2 — Entities Card

Afișează toți senzorii și alertele ANM într-un singur card detaliat cu iconițe.

### Instalare

Nu necesită carduri extra — este un card nativ Home Assistant.

### Cod YAML

```yaml
type: entities
title: 🌦️ Meteo <oras> - ANM
entities:
  - entity: sensor.<oras>_temperature
    name: Temperatură
    icon: mdi:thermometer
  - entity: sensor.<oras>_humidity
    name: Umiditate
    icon: mdi:water-percent
  - entity: sensor.<oras>_pressure
    name: Presiune
    icon: mdi:gauge
  - entity: sensor.<oras>_wind_speed
    name: Vânt
    icon: mdi:weather-windy
  - entity: sensor.<oras>_wind_direction
    name: Direcție vânt
    icon: mdi:compass
  - entity: sensor.<oras>_cloudiness
    name: Nebulozitate
    icon: mdi:weather-cloudy
  - entity: sensor.<oras>_snow_depth
    name: Strat zăpadă
    icon: mdi:snowflake
  - type: divider
  - entity: sensor.<oras>_anm_alerts
    name: Alerte ANM active
    icon: mdi:alert-octagon
  - entity: sensor.<oras>_alert_color
    name: Severitate alertă
    icon: mdi:alert
  - entity: sensor.<oras>_nowcasting_alerts
    name: Avertizări Nowcasting
    icon: mdi:weather-lightning
```

### Personalizare

- Poți elimina senzorii care nu te interesează
- Poți schimba iconițele cu orice icoană `mdi:` disponibilă în HA
- Poți adăuga `secondary_info: last-changed` pentru a vedea când s-a actualizat ultima dată

---

## Card 3 — Markdown Card

Afișează toate datele meteo și alertele ANM într-un format text personalizat.

### Instalare

Nu necesită carduri extra — este un card nativ Home Assistant.

### Cod YAML

```yaml
type: markdown
title: 🌦️ Meteo <oras> - ANM
content: >
  ### 🌡️ Condiții actuale

  **Temperatură:** {{ states('sensor.<oras>_temperature') }} °C

  **Umiditate:** {{ states('sensor.<oras>_humidity') }} %

  **Presiune:** {{ states('sensor.<oras>_pressure') }} hPa

  **Vânt:** {{ states('sensor.<oras>_wind_speed') }} m/s -
  {{ states('sensor.<oras>_wind_direction') }}

  **Nebulozitate:** {{ states('sensor.<oras>_cloudiness') }}

  ---

  ### 🚨 Alerte ANM

  **Alerte active:** {{ states('sensor.<oras>_anm_alerts') }}

  **Severitate:** {{ states('sensor.<oras>_alert_color') }}

  **Avertizări Nowcasting:** {{ states('sensor.<oras>_nowcasting_alerts') }}
```

### Personalizare

- Poți adăuga sau elimina orice linie din secțiunea `content`
- Poți folosi **Markdown** standard pentru formatare (bold, italic, titluri)
- Poți combina mai mulți senzori în același text folosind `{{ states('sensor...') }}`

---

## Card 4 — Alertă ANM cu culoare

Afișează textul complet al avertizării ANM cu stegulețul colorat corespunzător severității.

### Instalare

Nu necesită carduri extra — este un card nativ Home Assistant.

### Cod YAML

```yaml
type: markdown
title: 🚨 Avertizări ANM <oras>
content: >
  {% set culoare = states('sensor.<oras>_alert_color') %}
  {% set nr_alerte = states('sensor.<oras>_anm_alerts') | int(0) %}
  {% set alerte = state_attr('sensor.<oras>_anm_alerts', 'alerte_detalii') %}

  {% if nr_alerte == 0 %}
  🟢 **Nu există avertizări meteo!**
  {% else %}
  {% if culoare == 'Roșu' %}🔴{% elif culoare == 'Portocaliu' %}🟠{% elif culoare == 'Galben' %}🟡{% else %}🟢{% endif %} **Alertă {{ culoare }} activă**

  ---
  {% if alerte %}
  {% for alerta in alerte %}
  **📌 Tip:** {{ alerta.tip }}
  **⚡ Fenomene:** {{ alerta.fenomene }}
  **🕐 Interval:** {{ alerta.interval }}
  **📝 Mesaj:** {{ alerta.mesaj }}

  {% endfor %}
  {% endif %}
  {% endif %}
```

### Personalizare

- Poți schimba emoji-urile stegulețelor după preferință
- Poți elimina câmpurile din bucla `for` pe care nu le dorești (ex. județ)
- Mesajul `Nu există avertizări meteo!` poate fi personalizat

---

## Automatizări

### Cum adaugi o automatizare

1. Mergi în **Settings** → **Automations & Scenes**
2. Click pe **"+ Create Automation"**
3. Click pe cele **3 puncte** din dreapta sus → **"Edit in YAML"**
4. Șterge conținutul și lipește codul automatizării
5. Înlocuiește `<oras>` cu slug-ul tău și `<serviciu_notificare>` cu serviciul tău (ex: `notify.mobile_app_telefonul_meu`)
6. Click **Save**

---

### Automatizare 1 — Notificare la alertă ANM activă

Trimite o notificare pe telefon când ANM emite o alertă galbenă, portocalie sau roșie în zona ta, cu textul complet al avertizării.

```yaml
alias: "🚨 Alertă ANM <oras>"
description: "Notificare când apare o alertă ANM activă"
trigger:
  - platform: state
    entity_id: sensor.<oras>_alert_color
    to:
      - "Galben"
      - "Portocaliu"
      - "Roșu"
condition: []
action:
  - service: <serviciu_notificare>
    data:
      title: "⚠️ Alertă Meteo ANM - <oras>"
      message: >
        {% set culoare = states('sensor.<oras>_alert_color') %}
        🚨 Alertă {{ culoare }} activă!

        {% set alerte = state_attr('sensor.<oras>_anm_alerts', 'alerte_detalii') %}
        {% if alerte %}
          {% for alerta in alerte %}
          📌 {{ alerta.tip }}
          ⚡ {{ alerta.fenomene }}
          🕐 {{ alerta.interval }}
          📝 {{ alerta.mesaj }}
          {% endfor %}
        {% endif %}
      data:
        importance: high
        color: >
          {% if states('sensor.<oras>_alert_color') == 'Roșu' %}
            red
          {% elif states('sensor.<oras>_alert_color') == 'Portocaliu' %}
            orange
          {% else %}
            yellow
          {% endif %}
mode: single
```

### Personalizare

- Poți elimina din `to:` culorile pentru care nu vrei notificări (ex. elimini `"Galben"` dacă vrei notificări doar pentru portocaliu și roșu)
- Poți adăuga mai multe servicii de notificare în secțiunea `action`
- Poți adăuga o condiție de timp pentru a nu primi notificări noaptea

---

### Automatizare 2 — Notificare la temperaturi extreme

Trimite o notificare când temperatura depășește 35°C (caniculă) sau scade sub -10°C (ger extrem).

```yaml
alias: "🌡️ Temperatură extremă <oras>"
description: "Notificare la temperaturi extreme"
trigger:
  - platform: numeric_state
    entity_id: sensor.<oras>_temperature
    above: 35
    id: "cald"
  - platform: numeric_state
    entity_id: sensor.<oras>_temperature
    below: -10
    id: "frig"
condition: []
action:
  - service: <serviciu_notificare>
    data:
      title: >
        {% if trigger.id == 'cald' %}
          🥵 Caniculă în <oras>!
        {% else %}
          🥶 Ger extrem în <oras>!
        {% endif %}
      message: >
        Temperatura actuală: {{ states('sensor.<oras>_temperature') }} °C
        {% if trigger.id == 'cald' %}
        Rămâi hidratat și evită expunerea la soare!
        {% else %}
        Îmbracă-te corespunzător!
        {% endif %}
mode: single
```

### Personalizare

- Poți modifica pragurile de temperatură (`above: 35` și `below: -10`) după preferință
- Poți adăuga condiție de timp pentru a primi notificări doar în anumite ore
- Poți combina ambele trigger-e într-o singură automatizare

---

<div align="center">

📖 Înapoi la [README](README.md)

</div>
