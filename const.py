"""Constante pentru Info Meteo Romania."""

DOMAIN = "info_meteo_romania"
SCAN_INTERVAL = 30  # minute

# URL-uri API ANM
WEATHER_API_URL = "https://www.meteoromania.ro/wp-json/meteoapi/v2/starea-vremii"
ALERTS_XML_URL = "https://www.meteoromania.ro/avertizari-xml.php"
NOWCASTING_XML_URL = "https://www.meteoromania.ro/avertizari-nowcasting-xml.php"

# Atribute senzori
ATTR_TEMPERATURE = "temperature"
ATTR_HUMIDITY = "humidity"
ATTR_PRESSURE = "pressure"
ATTR_WIND_SPEED = "wind_speed"
ATTR_WIND_DIRECTION = "wind_direction"
ATTR_CLOUDINESS = "cloudiness"
ATTR_SNOW_DEPTH = "snow_depth"
ATTR_ALERTS = "alerts"
ATTR_NOWCASTING = "nowcasting"
ATTR_ALERT_TYPE = "alert_type"
ATTR_ALERT_COLOR = "alert_color"
ATTR_ALERT_START = "alert_start"
ATTR_ALERT_END = "alert_end"
ATTR_ALERT_DESCRIPTION = "alert_description"

# Culori alerte ANM
ALERT_COLORS = {
    "green": "Verde",
    "yellow": "Galben",
    "orange": "Portocaliu",
    "red": "Roșu",
}

# Lista completă localități ANM cu ID-uri
CITIES = {
    "ADAMCLISI": 1,
    "ADJUD": 2,
    "ALBA IULIA": 3,
    "ALEXANDRIA": 4,
    "AMZACEA": 5,
    "ARAD": 6,
    "BACĂU": 7,
    "BAIA MARE": 8,
    "BĂILE HERCULANE": 9,
    "BĂILEȘTI": 10,
    "BÂRLAD": 11,
    "BISTRIȚA": 12,
    "BOTOȘANI": 13,
    "BRĂILA": 14,
    "BRAȘOV": 15,
    "BUCUREȘTI": 16,
    "BUZĂU": 17,
    "CALAFAT": 18,
    "CĂLĂRAȘI": 19,
    "CÂMPINA": 20,
    "CÂMPULUNG MUSCEL": 21,
    "CARACAL": 22,
    "CARANSEBEȘ": 23,
    "CERNAVODĂ": 24,
    "CLUJ-NAPOCA": 25,
    "CONSTANȚA": 26,
    "CRAIOVA": 27,
    "CURTEA DE ARGEȘ": 28,
    "DEVA": 29,
    "DROBETA TURNU SEVERIN": 30,
    "FĂLTICENI": 31,
    "FETEȘTI": 32,
    "FOCȘANI": 33,
    "GALAȚI": 34,
    "GIURGIU": 35,
    "IAȘI": 36,
    "LUGOJ": 37,
    "MANGALIA": 38,
    "MEDGIDIA": 39,
    "MIERCUREA CIUC": 40,
    "ODORHEIUL SECUIESC": 41,
    "ORADEA": 42,
    "PETROȘANI": 43,
    "PIATRA NEAMȚ": 44,
    "PITEȘTI": 45,
    "PLOIEȘTI": 46,
    "PREDEAL": 47,
    "RÂMNICU VÂLCEA": 48,
    "REȘIȚA": 49,
    "ROMAN": 50,
    "ROȘIORII DE VEDE": 51,
    "SATU MARE": 52,
    "SFÂNTU GHEORGHE": 53,
    "SIBIU": 54,
    "SIGHETU MARMAȚIEI": 55,
    "SINAIA": 56,
    "SLATINA": 57,
    "SLOBOZIA": 58,
    "SUCEAVA": 59,
    "SULINA": 60,
    "TÂRGOVIȘTE": 61,
    "TÂRGU JIU": 62,
    "TÂRGU MUREȘ": 63,
    "TÂRGU NEAMȚ": 64,
    "TIMIȘOARA": 65,
    "TULCEA": 66,
    "TURDA": 67,
    "TURNU MĂGURELE": 68,
    "URZICENI": 69,
    "VASLUI": 70,
    "ZALĂU": 71,
    "ZIMNICEA": 72,
}
