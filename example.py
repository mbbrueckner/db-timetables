import os
from dotenv import load_dotenv

from src.db_timetables import TimetablesClient, ArrivalDeparture, TimetableStop

load_dotenv()

client = TimetablesClient(
    client_id=os.environ["CLIENT_ID"],
    api_key=os.environ["CLIENT_SECRET"],
)


def train_name(stop: TimetableStop) -> str:
    """Return the most human-readable train label for a stop.

    Prefers the line indicator from the event (e.g. 'RE3', 'S3') because it
    matches platform boards. Falls back to category + trip number.
    """
    tl = stop.train_line
    if not tl:
        return "?"
    event: ArrivalDeparture | None = stop.departure or stop.arrival
    line = event.line if event else ""
    if line:
        # Line already encodes the category (e.g. "RE3", "IC51") — use as-is.
        return line
    return f"{tl.category} {tl.number}".strip() if tl.number else tl.category


#  Station search 
print("### Station search: Frankfurt ###")
stations = client.get_station("Jena Frankfurt")
for s in stations[:5]:
    print(f"  {s.name} (EVA {s.eva})")

if not stations:
    print("  No stations found.")
    exit()

eva = stations[0].eva
print(f"\nUsing station: {stations[0].name} ({eva})\n")

#  Planned timetable for current hour 
print("### Planned timetable (current hour) ###")
plan = client.get_plan(eva)
print(f"  Station: {plan.station}, {len(plan.stops)} stops")
for stop in plan.stops[:5]:
    event = stop.departure or stop.arrival
    pt = event.planned_time.strftime("%H:%M") if event and event.planned_time else "?"
    platform = event.effective_platform if event else "?"
    print(f"  {train_name(stop):12}  planned={pt}  platform={platform}")

#  Timetable with live changes merged in 
print(f"\n### Timetable with live changes ###")
live = client.get_timetable_with_changes(eva)
delayed = [
    s for s in live.stops
    if s.departure and s.departure.delay_minutes and s.departure.delay_minutes > 0
]
cancelled = [s for s in live.stops if s.is_cancelled]
print(f"  Total stops : {len(live.stops)}")
print(f"  Delayed     : {len(delayed)}")
print(f"  Cancelled   : {len(cancelled)}")

print()
for stop in delayed[:5]:
    dp = stop.departure
    print(
        f"  {train_name(stop):12}  "
        f"+{dp.delay_minutes} min  "
        f"platform={dp.effective_platform}"
    )

for stop in cancelled[:5]:
    event = stop.departure or stop.arrival
    platform = event.effective_platform if event else "?"
    print(f"  {train_name(stop):12}  cancelled  platform={platform}")