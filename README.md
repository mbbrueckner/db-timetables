# deutsche-bahn

A Python library for the Deutsche Bahn APIs — currently supporting the [Timetables API](https://developers.deutschebahn.com/db-api-marketplace/apis/product/timetables) and the [StaDa Station Data API](https://developers.deutschebahn.com/db-api-marketplace/apis/product/stada).

## Requirements

- Python 3.13+
- `requests`

## Installation

```bash
uv add deutsche-bahn-py
```

Or with pip:

```bash
pip install deutsche-bahn-py
```

## Setup

1. Register at [developers.deutschebahn.com](https://developers.deutschebahn.com), create an application, and subscribe to the APIs you need (**Timetables** and/or **StaDa**).
2. Copy your **Client ID** and **API Key**.

---

## Timetables API

```python
from deutsche_bahn.timetables import TimetablesClient

client = TimetablesClient(
    client_id="your_client_id",
    api_key="your_api_key",
)
```

### Find a station

```python
stations = client.get_station("Frankfurt")
# [Station(name='Frankfurt am Main - Stadion', eva='8002040'), ...]

eva = stations[0].eva
```

Stations are identified by their **EVA number**, a numeric DB station ID.

### Planned timetable

```python
plan = client.get_plan(eva)               # current hour
plan = client.get_plan(eva, hour=14)      # specific hour today
plan = client.get_plan(eva, date=datetime(2026, 5, 20), hour=9)

for stop in plan.stops:
    dp = stop.departure
    print(stop.train_line.display_name, dp.planned_time, dp.planned_platform)
```

Returns one hour of scheduled departures/arrivals. No live data.

### Live timetable (plan + changes merged)

```python
live = client.get_timetable_with_changes(eva)

for stop in live.stops:
    dp = stop.departure
    if dp and dp.delay_minutes:
        print(f"{stop.train_line.display_name} is +{dp.delay_minutes} min late")
    if stop.is_cancelled:
        print(f"{stop.train_line.display_name} is cancelled")
```

This is the most useful method — it fetches the plan and all current deviations, then merges them so each stop reflects reality.

### Changes only

```python
# All current deviations for the station (delays, cancellations, platform changes)
changes = client.get_full_changes(eva)

# Only what changed since your last call - use this when polling
recent = client.get_recent_changes(eva)
```

### Data model

#### `TimetableStop`

| Attribute | Type | Description |
|---|---|---|
| `id` | `str` | Unique stop identifier |
| `train_line` | `TrainLine` | Train category and number |
| `arrival` | `ArrivalDeparture \| None` | Arrival data |
| `departure` | `ArrivalDeparture \| None` | Departure data |
| `messages` | `list[Message]` | Delay/disruption messages |
| `is_cancelled` | `bool` | True if arrival or departure is cancelled |

#### `ArrivalDeparture`

| Attribute | Type | Description |
|---|---|---|
| `planned_time` | `datetime \| None` | Scheduled time |
| `changed_time` | `datetime \| None` | Actual/expected time (set when delayed) |
| `planned_platform` | `str` | Scheduled platform |
| `changed_platform` | `str` | Actual platform (set when changed) |
| `planned_path` | `list[str]` | Scheduled route as station names |
| `changed_path` | `list[str]` | Actual route (set when rerouted) |
| `effective_time` | `datetime \| None` | `changed_time` if set, else `planned_time` |
| `effective_platform` | `str` | `changed_platform` if set, else `planned_platform` |
| `delay_minutes` | `int \| None` | Difference in minutes, or `None` if on time |
| `is_cancelled` | `bool` | True if status is cancelled |

#### `TrainLine`

| Attribute | Type | Description |
|---|---|---|
| `category` | `str` | Train category (ICE, IC, RE, S, …) |
| `number` | `str` | Train number |
| `owner` | `str` | Operator code |
| `display_name` | `str` | `"{category} {number}"` (e.g. `"ICE 9551"`) |

#### `Station`

| Attribute | Type | Description |
|---|---|---|
| `eva` | `str` | EVA station number |
| `name` | `str` | Station name |
| `ds100` | `str` | DS100 abbreviation |
| `lat` / `lon` | `float` | Coordinates |

---

## StaDa Station Data API

```python
from deutsche_bahn.stada import StaDaClient

client = StaDaClient(
    client_id="your_client_id",
    api_key="your_api_key",
)
```

### Search for stations

```python
results = client.get_stations(searchstring="Frankfurt")
# StationQuery(total=12, offset=0, limit=100, result=[...])

for station in results.result:
    print(station.number, station.name, station.category)
```

Supports wildcards `*` and `?` in the search string.

### Filter options

```python
# By federal state
results = client.get_stations(federalstate="bayern")

# By category range or list
results = client.get_stations(category="1-3")
results = client.get_stations(category="1,3,5")

# By EVA number
results = client.get_stations(eva=8000105)

# By Ril100 identifier
results = client.get_stations(ril="FF")

# Combine filters with OR logic
results = client.get_stations(searchstring="Hbf", federalstate="hessen", logicaloperator="or")

# Pagination
results = client.get_stations(offset=100, limit=50)
```

### Fetch a single station

```python
station = client.get_station(1071)  # Bahnhofsnummer
print(station.result[0].name)       # Frankfurt(Main)Hbf
```

### 3-S-Zentralen

3-S-Zentralen are the 24/7 operations centres for German railway stations.

```python
# All 3-S-Zentralen
szentralen = client.get_szentralen()

# Single entry by ID
sz = client.get_szentrale(50)
print(sz.result[0].name, sz.result[0].public_phone_number)
```

### Data model

#### `StadaStation`

| Attribute | Type | Description |
|---|---|---|
| `number` | `int` | Bahnhofsnummer (station ID) |
| `name` | `str` | Station name |
| `category` | `int` | Station category (1–7) |
| `price_category` | `int` | Price category |
| `federal_state` | `str` | Federal state name |
| `has_wifi` | `bool` | DB WiFi available |
| `has_db_lounge` | `bool` | DB Lounge available |
| `has_travel_center` | `bool` | DB Reisezentrum available |
| `has_locker_system` | `bool` | Lockers available |
| `has_parking` | `bool` | Parking available |
| `has_bicycle_parking` | `bool` | Bicycle parking available |
| `has_taxi_rank` | `bool` | Taxi rank available |
| `has_stepless_access` | `str` | `"yes"`, `"no"`, or `"partial"` |
| `eva_numbers` | `list[EVANumber]` | Associated EVA numbers |
| `ril100_identifiers` | `list[RiL100Identifier]` | Ril100 codes |
| `mailing_address` | `Address \| None` | Station mailing address |
| `szentrale` | `SZentrale \| None` | Responsible 3-S-Zentrale |

#### `SZentrale`

| Attribute | Type | Description |
|---|---|---|
| `number` | `int` | Unique ID |
| `name` | `str` | Name |
| `public_phone_number` | `str` | Public phone |
| `email` | `str` | Email address |
| `address` | `Address \| None` | Physical address |

---

## Exceptions

All clients share the same exception hierarchy:

| Exception | When |
|---|---|
| `AuthenticationError` | Invalid or missing credentials (401/403) |
| `NotFoundError` | Station or resource not found (404) |
| `RateLimitError` | Too many requests (429) |
| `DBApiError` | Any other API or network error |

```python
from deutsche_bahn.stada.exceptions import NotFoundError, RateLimitError, DBApiError

try:
    station = client.get_station(9999999)
except NotFoundError:
    print("Station not found")
except RateLimitError:
    print("Rate limit hit")
except DBApiError as e:
    print(f"API error: {e}")
```

## API reference

- [Timetables API](https://developers.deutschebahn.com/db-api-marketplace/apis/product/timetables)
- [StaDa Station Data API](https://developers.deutschebahn.com/db-api-marketplace/apis/product/stada)

Data is provided under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).