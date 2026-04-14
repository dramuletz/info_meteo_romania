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
