---
name: location-and-environment
description: "Location intelligence: weather forecasts, geocoding, places, routes, timezones."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Weather, Maps, Geocoding, Places, Routing, Location, Forecast, OpenStreetMap, wttr.in]
    related_skills: [time-sensitive-queries]
---

# Location & Environment

Location intelligence and environmental data: weather forecasts, geocoding, place search, routing, and timezone lookups. All tools are free, no API keys required.

## Decision: Which Tool?

| Task | Tool | Section |
|------|------|---------|
| Weather forecast / current conditions | wttr.in API | [Weather] |
| City name → coordinates | Nominatim search | [Geocoding & Places] |
| Coordinates → address | Nominatim reverse | [Geocoding & Places] |
| Find nearby restaurants/hospitals/etc. | Overpass API nearby | [Geocoding & Places] |
| Driving/walking distance & time | OSRM distance | [Routing] |
| Turn-by-turn directions | OSRM directions | [Routing] |
| Timezone for a location | TimeAPI.io | [Timezones] |

---

## Weather

### Core Approach

Use `curl https://wttr.in/` — a free, no-auth weather API. `web_extract` consistently fails on weather sites, so always use wttr.in directly.

### Quick Commands

```bash
# Current conditions (one-liner)
curl -s "https://wttr.in/Beijing?format=%c+%t+%h+%w+%p&lang=zh"
# Output: ✨ +24°C 61% ↙16km/h 0.0mm

# Multi-day visual forecast
curl -s "https://wttr.in/Beijing?lang=zh&format=v2"
# Returns ASCII-art chart with 3-day forecast

# Structured JSON (for programmatic parsing)
curl -s "https://wttr.in/Beijing?format=j1"
# Returns full JSON with weather[] array (3 days)
```

### Workflow

1. **Identify location** — city name in English or pinyin (e.g., `Beijing`, `Shanghai`)
2. **Determine query type**: quick check → format string; visual → `format=v2`; detailed → `format=j1`
3. **Handle ambiguity** — if user says "朝阳" (could be Beijing or Liaoning), clarify or default
4. **Present clearly** — use a table for forecast, mention rain probability prominently

### Pitfalls

- **web_extract fails on weather sites** — always use `curl https://wttr.in/`
- **Chinese city names** — use English/pinyin: `Beijing` not `北京`, `Chaoyang+Beijing` for districts
- **Tomorrow vs today at midnight** — check system date; `[0]` = today, `[1]` = tomorrow
- **Rate limiting** — cache results; one request per city per conversation is usually sufficient

---

## Geocoding & Places

### Script

```bash
MAPS=scripts/maps_client.py
```

### search — Place name to coordinates

```bash
python3 $MAPS search "Eiffel Tower"
python3 $MAPS search "1600 Pennsylvania Ave, Washington DC"
```

Returns: lat, lon, display name, type, bounding box, importance score.

### reverse — Coordinates to address

```bash
python3 $MAPS reverse 48.8584 2.2945
```

Returns: full address breakdown (street, city, state, country, postcode).

### nearby — Find places by category

```bash
# By coordinates
python3 $MAPS nearby 48.8584 2.2945 restaurant --limit 10

# By address (auto-geocoded)
python3 $MAPS nearby --near "Times Square, New York" --category cafe
python3 $MAPS nearby --near "90210" --category pharmacy

# Multiple categories
python3 $MAPS nearby --near "downtown austin" --category restaurant --category bar --limit 10
```

**46 categories**: restaurant, cafe, bar, hospital, pharmacy, hotel, guest_house, camp_site, supermarket, atm, gas_station, parking, museum, park, school, university, bank, police, fire_station, library, airport, train_station, bus_stop, church, mosque, synagogue, dentist, doctor, cinema, theatre, gym, swimming_pool, post_office, convenience_store, bakery, bookshop, laundry, car_wash, car_rental, bicycle_rental, taxi, veterinary, zoo, playground, stadium, nightclub.

Each result includes: `name`, `address`, `lat`/`lon`, `distance_m`, `maps_url`, `directions_url`, and tags (`cuisine`, `hours`, `phone`, `website`).

### area — Bounding box for a place

```bash
python3 $MAPS area "Manhattan, New York"
```

### bbox — Search within a bounding box

```bash
python3 $MAPS bbox 40.75 -74.00 40.77 -73.98 restaurant --limit 20
```

### Working With Location Pins

When a user sends a location pin (latitude/longitude), pass coordinates straight to `nearby`:
```bash
python3 $MAPS nearby 36.17 -115.14 cafe --radius 1500
```

---

## Routing

### distance — Travel distance and time

```bash
python3 $MAPS distance "Paris" --to "Lyon"
python3 $MAPS distance "New York" --to "Boston" --mode driving
python3 $MAPS distance "Big Ben" --to "Tower Bridge" --mode walking
```

Modes: driving (default), walking, cycling. Returns road distance, duration, and straight-line distance.

### directions — Turn-by-turn navigation

```bash
python3 $MAPS directions "Eiffel Tower" --to "Louvre Museum" --mode walking
python3 $MAPS directions "JFK Airport" --to "Times Square" --mode driving
```

Returns numbered steps with instruction, distance, duration, road name, and maneuver type.

---

## Timezones

```bash
python3 $MAPS timezone 48.8584 2.2945
python3 $MAPS timezone 35.6762 139.6503
```

Returns timezone name, UTC offset, and current local time.

---

## Pitfalls

- Nominatim ToS: max 1 req/s (handled automatically by the script)
- `nearby` requires lat/lon OR `--near "<address>"` — one of the two is needed
- OSRM routing coverage is best for Europe and North America
- Overpass API can be slow during peak hours; script falls back between mirrors automatically
- If a zip code gives ambiguous results, include country/state
- For "open now?" questions, check the `hours` field; verify with `web_search` since OSM hours are community-maintained

## Verification

```bash
python3 scripts/maps_client.py search "Statue of Liberty"
# Should return lat ~40.689, lon ~-74.044

python3 scripts/maps_client.py nearby --near "Times Square" --category restaurant --limit 3
# Should return restaurants within ~500m
```
