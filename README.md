# db-timetables

A Python library for the [Deutsche Bahn Timetables API](https://developers.deutschebahn.com/db-api-marketplace/apis/product/timetables).

## Requirements

- Python 3.13+
- `requests`

## Installation

```bash
uv add db-timetables
```

Or with pip:

```bash
pip install db-timetables
```

## Setup

1. Register at [developers.deutschebahn.com](https://developers.deutschebahn.com), create an application, and subscribe to the **Timetables** API.
2. Copy your **Client ID** and **API Key**.

## Usage

```python
from db_timetables import TimetablesClient

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

This is the most useful method - it fetches the plan and all current deviations, then merges them so each stop reflects reality.

### Changes only

```python
# All current deviations for the station (delays, cancellations, platform changes)
changes = client.get_full_changes(eva)

# Only what changed since your last call - use this when polling
recent = client.get_recent_changes(eva)
```

## Data model

### `TimetableStop`

| Attribute | Type | Description |
|---|---|---|
| `id` | `str` | Unique stop identifier |
| `train_line` | `TrainLine` | Train category and number |
| `arrival` | `ArrivalDeparture \| None` | Arrival data |
| `departure` | `ArrivalDeparture \| None` | Departure data |
| `messages` | `list[Message]` | Delay/disruption messages |
| `is_cancelled` | `bool` | True if arrival or departure is cancelled |

### `ArrivalDeparture`

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

### `TrainLine`

| Attribute | Type | Description |
|---|---|---|
| `category` | `str` | Train category (ICE, IC, RE, S, …) |
| `number` | `str` | Train number |
| `owner` | `str` | Operator code |
| `display_name` | `str` | `"{category} {number}"` (e.g. `"ICE 9551"`) |

### `Station`

| Attribute | Type | Description |
|---|---|---|
| `eva` | `str` | EVA station number |
| `name` | `str` | Station name |
| `ds100` | `str` | DS100 abbreviation |
| `lat` / `lon` | `float` | Coordinates |

## Exceptions

| Exception | When |
|---|---|
| `AuthenticationError` | Invalid or missing credentials (401/403) |
| `NotFoundError` | Station or resource not found (404) |
| `RateLimitError` | Too many requests (429) - free tier allows 60 req/min |
| `DBApiError` | Any other API or network error |

```python
from db_timetables import TimetablesClient, RateLimitError, NotFoundError

try:
    stations = client.get_station("München")
except NotFoundError:
    print("No stations found")
except RateLimitError:
    print("Slow down - rate limit hit")
```

## API reference

Full DB API documentation: [developers.deutschebahn.com](https://developers.deutschebahn.com/db-api-marketplace/apis/product/timetables)

Data is provided under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).