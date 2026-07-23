# Marseille — Arrêtés de mise en sécurité

An interactive map of buildings in Marseille placed under an **"arrêté de mise en sécurité"** (a municipal safety order issued when a building is found structurally unsafe), showing whether that order is still active or has been lifted (**mainlevée**).

## Website

Visit the live site: https://marseille-arretes-de-peril.onrender.com/

## Context

Marseille has one of France's largest stocks of degraded housing. The issue became impossible to ignore after the **8 November 2018 collapse of 63 rue d'Aubagne**, which killed eight people and triggered a wave of emergency evacuations across the city center. In the years since, thousands of residents have been displaced by safety orders.

The City publishes the raw list of orders, but as a flat administrative page it's hard to read: there is no way to see where these buildings are concentrated, how many have actually been resolved, or how the situation compares across quarters (arrondissements).

I lived in Marseille for two years and saw this problem firsthand: for a year, I lived in a building with visible cracks that was never added to the official list of unsafe buildings. People tend to underestimate the risk, or actively avoid reporting it, because having your building added to the list means having to move out, and finding another apartment is not easy.

## The idea

The purpose of this website is to show the scale and geography of the housing crisis, and the pace of the response, by turning that public data into a map.

The app scrapes the City of Marseille's public list of unsafe-building orders ([marseille.fr — arrêtés de péril](https://www.marseille.fr/logement-urbanisme/amelioration-de-lhabitat/arretes-de-peril)), geocodes each address, and plots it on a map of the city. Each building is color-coded:

- **Red** — the safety order is still active (residents evicted, building unresolved)
- **Green** — the order has been lifted (**mainlevée**), meaning the building has been repaired or cleared

## Stack

- **Backend**: Django (`Marseille_website/`), with the mapping logic in the `map` app
- **Data pipeline**: a management command (`map/management/commands/geocode_addresses.py`) scrapes addresses from marseille.fr and geocodes them via the Nominatim/OpenStreetMap API
- **Frontend**: Leaflet for the map, Chart.js for the per-arrondissement breakdown

## Running locally

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py geocode_addresses   # scrape + geocode the latest list
python manage.py runserver
```

---

*Made by Arianna Tonazzolli.*
