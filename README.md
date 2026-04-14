# 🌦️ Info Meteo Romania

[!\[hacs\_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[!\[GitHub Release](https://img.shields.io/github/release/dramuletz/info\_meteo\_romania.svg)](https://github.com/dramuletz/info_meteo_romania/releases)
[!\[License](https://img.shields.io/github/license/dramuletz/info\_meteo\_romania.svg)](LICENSE)

Integrare **Home Assistant** pentru date meteo oficiale de la **ANM (Administrația Națională de Meteorologie)** din România.

## ✨ Funcționalități

* 🌡️ **Temperatură, umiditate, presiune** în timp real
* 💨 **Vânt** - viteză și direcție
* ☁️ **Nebulozitate** actualizată
* ❄️ **Strat de zăpadă** (unde este disponibil)
* 🚨 **Alerte ANM** cu culori (Verde/Galben/Portocaliu/Roșu)
* ⛈️ **Avertizări Nowcasting** (fenomene imediate)
* 🗺️ **72+ localități** din toată România
* 🔄 **Actualizare automată** la 30 de minute

## 📥 Instalare via HACS

### Metodă 1: HACS - Repository Custom (recomandat)

1. Deschide **HACS** în Home Assistant
2. Click pe **"Integrations"**
3. Click pe cele 3 puncte din colțul dreapta sus → **"Custom repositories"**
4. Adaugă URL-ul: `https://github.com/dramuletz/info\_meteo\_romania`
5. Selectează categoria: **Integration**
6. Click **"Add"**
7. Caută **"Info Meteo Romania"** și instalează

### Metodă 2: Instalare manuală

1. Descarcă ultima versiune din [Releases](https://github.com/YOUR_USERNAME/info_meteo_romania/releases)
2. Copiază folderul `custom\_components/info\_meteo\_romania` în directorul `custom\_components` din Home Assistant
3. Repornește Home Assistant

## ⚙️ Configurare

1. Mergi la **Settings → Devices \& Services → Add Integration**
2. Caută **"Info Meteo Romania"**
3. Selectează **localitatea** din lista dropdown
4. Click **Submit**

Poți adăuga **mai multe localități** repetând procesul!

## 📊 Entități Create

Pentru fiecare localitate configurată se creează:

|Entitate|Tip|Descriere|
|-|-|-|
|`weather.meteo\_\[localitate]`|Weather|Card meteo complet|
|`sensor.\[localitate]\_temperatura`|Sensor|Temperatura în °C|
|`sensor.\[localitate]\_umiditate\_relativa`|Sensor|Umiditate în %|
|`sensor.\[localitate]\_presiune\_atmosferica`|Sensor|Presiune în hPa|
|`sensor.\[localitate]\_viteza\_vantului`|Sensor|Vânt în m/s|
|`sensor.\[localitate]\_directia\_vantului`|Sensor|Direcția vântului|
|`sensor.\[localitate]\_nebulozitate`|Sensor|Starea cerului|
|`sensor.\[localitate]\_strat\_zapada`|Sensor|Zăpadă în cm|
|`sensor.\[localitate]\_alerte\_anm`|Sensor|Nr. alerte active|
|`sensor.\[localitate]\_culoare\_alerta\_anm`|Sensor|Severitatea alertei|
|`sensor.\[localitate]\_avertizari\_nowcasting`|Sensor|Nr. avertizări imediate|

## 🗺️ Localități Disponibile

Integrarea suportă **72+ stații meteo ANM** incluzând:

Alba Iulia, Alexandria, Arad, Bacău, Baia Mare, Bistrița, Botoșani, Brăila, Brașov, București, Buzău, Calafat, Cluj-Napoca, Constanța, Craiova, Deva, Focșani, Galați, Giurgiu, Iași, Lugoj, Mangalia, Miercurea Ciuc, Oradea, Petroșani, Piatra Neamț, Pitești, Ploiești, Predeal, Râmnicu Vâlcea, Reșița, Roman, Satu Mare, Sfântu Gheorghe, Sibiu, Sighetu Marmației, Sinaia, Slatina, Slobozia, Suceava, Sulina, Timișoara, Tulcea, Turda, Vaslui, Zalău și multe altele!

## 🏠 Exemplu Dashboard Lovelace

```yaml
type: weather-forecast
entity: weather.meteo\_brasov
forecast\_type: daily
```

```yaml
type: entities
title: Meteo Brașov
entities:
  - entity: sensor.brasov\_temperatura
  - entity: sensor.brasov\_umiditate\_relativa
  - entity: sensor.brasov\_alerte\_anm
    icon: mdi:alert-octagon
  - entity: sensor.brasov\_culoare\_alerta\_anm
```

## 📡 Surse de Date

Toate datele sunt obținute direct de la serverele oficiale ANM:

* **Starea vremii**: `https://www.meteoromania.ro/wp-json/meteoapi/v2/starea-vremii`
* **Alerte XML**: `https://www.meteoromania.ro/avertizari-xml.php`
* **Nowcasting XML**: `https://www.meteoromania.ro/avertizari-nowcasting-xml.php`

## 🤝 Contribuții

Contribuțiile sunt binevenite! Deschide un [Issue](https://github.com/YOUR_USERNAME/info_meteo_romania/issues) sau un [Pull Request](https://github.com/YOUR_USERNAME/info_meteo_romania/pulls).

## 📝 Licență

Distribuit sub licența MIT. Vezi [LICENSE](LICENSE) pentru detalii.

\---

> \*\*Date furnizate de\*\* \[ANM - Administrația Națională de Meteorologie](https://www.meteoromania.ro/)

