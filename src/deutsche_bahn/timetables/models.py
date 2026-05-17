from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class MessageType(StrEnum):
    HIM = "h"  # HIM message (Hafas Information Manager)
    QUALITY_CHANGE = "q"
    FREE = "f"
    CAUSE_OF_DELAY = "d"
    IBIS = "i"
    UNASSIGNED_IBIS = "u"
    DISRUPTION = "r"
    CONNECTION = "c"


class EventStatus(StrEnum):
    PLANNED = "p"
    ADDED = "a"
    CANCELLED = "c"


class ConnectionStatus(StrEnum):
    WAITING = "w"
    NO_WAIT = "n"
    ALTERNATIVE = "a"


class DistributorType(StrEnum):
    CITY = "s"
    REGION = "r"
    LONG_DISTANCE = "f"
    OTHER = "x"


class DelaySource(StrEnum):
    LEIBIT = "L"
    RISNE_AUTO = "NA"
    RISNE_MANUAL = "NM"
    VDV = "V"
    ISTP_AUTO = "IA"
    ISTP_MANUAL = "IM"
    AUTOMATIC_PROGNOSIS = "A"


def _parse_db_time(value: str | None) -> datetime | None:
    """Parse DB compact time format YYMMDDhhmm to datetime."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%y%m%d%H%M")
    except ValueError:
        return None


@dataclass
class Station:
    eva: str
    name: str
    ds100: str = ""
    lat: float = 0.0
    lon: float = 0.0

    @classmethod
    def from_xml(cls, element: ET.Element) -> Station:
        return cls(
            eva=element.get("eva", ""),
            name=element.get("name", ""),
            ds100=element.get("ds100", ""),
            lat=float(element.get("lat") or 0),
            lon=float(element.get("lon") or 0),
        )


@dataclass
class TrainLine:
    """Characterises a trip (tl element)."""

    trip_type: str = ""  # t: p=planned, e=extra, z=?, s=?, h=?, n=?
    category: str = ""  # c: ICE, IC, RE, S, etc.
    number: str = ""  # n: train number
    owner: str = ""  # o: operator EVU code
    filter_flags: str = ""  # f: filter flags

    @classmethod
    def from_xml(cls, element: ET.Element | None) -> TrainLine | None:
        if element is None:
            return None
        return cls(
            trip_type=element.get("t", ""),
            category=element.get("c", ""),
            number=element.get("n", ""),
            owner=element.get("o", ""),
            filter_flags=element.get("f", ""),
        )

    @property
    def display_name(self) -> str:
        return " ".join(p for p in (self.category, self.number) if p)


@dataclass
class DistributorMessage:
    """Additional station-based disruption message from a specific distributor."""

    name: str = ""  # n: distributor name
    type: str = ""  # t: s=CITY, r=REGION, f=LONG_DISTANCE, x=OTHER
    internal_text: str = ""  # int
    timestamp: datetime | None = None

    @classmethod
    def from_xml(cls, element: ET.Element) -> DistributorMessage:
        return cls(
            name=element.get("n", ""),
            type=element.get("t", ""),
            internal_text=element.get("int", ""),
            timestamp=_parse_db_time(element.get("ts")),
        )


@dataclass
class Message:
    """A message associated with an event, stop, or trip."""

    id: str = ""
    type: str = ""  # t: h, q, f, d, i, u, r, c
    timestamp: datetime | None = None
    code: int | None = None  # c: numeric code
    category: str = ""  # cat
    external_category: str = ""  # ec
    external_text: str = ""  # ext
    internal_text: str = ""  # int
    external_link: str = ""  # elnk
    owner: str = ""  # o
    priority: str = ""  # pr: 1=HIGH, 2=MEDIUM, 3=LOW, 4=DONE
    deleted: bool = False  # del: 1 if deleted
    valid_from: datetime | None = None  # from
    valid_to: datetime | None = None  # to
    trip_labels: list[TrainLine] = field(default_factory=list)  # tl
    distributor_messages: list[DistributorMessage] = field(default_factory=list)  # dm

    @classmethod
    def from_xml(cls, element: ET.Element) -> Message:
        code_raw = element.get("c")
        return cls(
            id=element.get("id", ""),
            type=element.get("t", ""),
            timestamp=_parse_db_time(element.get("ts")),
            code=int(code_raw) if code_raw else None,
            category=element.get("cat", ""),
            external_category=element.get("ec", ""),
            external_text=element.get("ext", ""),
            internal_text=element.get("int", ""),
            external_link=element.get("elnk", ""),
            owner=element.get("o", ""),
            priority=element.get("pr", ""),
            deleted=element.get("del", "0") == "1",
            valid_from=_parse_db_time(element.get("from")),
            valid_to=_parse_db_time(element.get("to")),
            trip_labels=[t for tl in element.findall("tl") if (t := TrainLine.from_xml(tl))],
            distributor_messages=[DistributorMessage.from_xml(dm) for dm in element.findall("dm")],
        )

    @property
    def text(self) -> str:
        return self.internal_text or self.external_text


@dataclass
class ArrivalDeparture:
    """An arrival or departure event at a stop (ar / dp element)."""

    planned_time: datetime | None = None  # pt
    changed_time: datetime | None = None  # ct
    planned_platform: str = ""  # pp
    changed_platform: str = ""  # cp
    planned_path: list[str] = field(default_factory=list)  # ppth (pipe-separated)
    changed_path: list[str] = field(default_factory=list)  # cpth
    planned_status: EventStatus | None = None
    changed_status: EventStatus | None = None
    cancellation_time: datetime | None = None  # clt
    line: str = ""  # l: line indicator (e.g. "3" for S3)
    planned_distant_endpoint: str = ""  # pde
    changed_distant_endpoint: str = ""  # cde
    distant_change: int | None = None  # dc
    hidden: bool = False  # hi: 1 = don't show boarding/alighting
    transition: str = ""  # tra: trip id of connecting trip
    wings: str = ""  # wings: pipe-separated trip ids
    messages: list[Message] = field(default_factory=list)

    @classmethod
    def from_xml(cls, element: ET.Element | None) -> ArrivalDeparture | None:
        if element is None:
            return None

        def split_path(raw: str | None) -> list[str]:
            return [s for s in (raw or "").split("|") if s]

        dc_raw = element.get("dc")
        return cls(
            planned_time=_parse_db_time(element.get("pt")),
            changed_time=_parse_db_time(element.get("ct")),
            planned_platform=element.get("pp", ""),
            changed_platform=element.get("cp", ""),
            planned_path=split_path(element.get("ppth")),
            changed_path=split_path(element.get("cpth")),
            planned_status=EventStatus(element.get("ps")) if element.get("ps") else None,
            changed_status=EventStatus(element.get("cs")) if element.get("cs") else None,
            cancellation_time=_parse_db_time(element.get("clt")),
            line=element.get("l", ""),
            planned_distant_endpoint=element.get("pde", ""),
            changed_distant_endpoint=element.get("cde", ""),
            distant_change=int(dc_raw) if dc_raw else None,
            hidden=element.get("hi", "0") == "1",
            transition=element.get("tra", ""),
            wings=element.get("wings", ""),
            messages=[Message.from_xml(m) for m in element.findall("m")],
        )

    @property
    def effective_time(self) -> datetime | None:
        return self.changed_time or self.planned_time

    @property
    def effective_platform(self) -> str:
        return self.changed_platform or self.planned_platform

    @property
    def is_cancelled(self) -> bool:
        return (
            self.changed_status == EventStatus.CANCELLED
            or self.planned_status == EventStatus.CANCELLED
        )

    @property
    def delay_minutes(self) -> int | None:
        if self.planned_time and self.changed_time:
            return int((self.changed_time - self.planned_time).total_seconds() / 60)
        return None


@dataclass
class HistoricDelay:
    """One entry in the delay history of a stop."""

    arrival_time: datetime | None = None  # ar
    departure_time: datetime | None = None  # dp
    source: str = ""  # src
    cause: str = ""  # cod
    timestamp: datetime | None = None  # ts

    @classmethod
    def from_xml(cls, element: ET.Element) -> HistoricDelay:
        return cls(
            arrival_time=_parse_db_time(element.get("ar")),
            departure_time=_parse_db_time(element.get("dp")),
            source=element.get("src", ""),
            cause=element.get("cod", ""),
            timestamp=_parse_db_time(element.get("ts")),
        )


@dataclass
class HistoricPlatformChange:
    """One entry in the platform-change history of a stop."""

    arrival_platform: str = ""  # ar
    departure_platform: str = ""  # dp
    cause: str = ""  # cot
    timestamp: datetime | None = None

    @classmethod
    def from_xml(cls, element: ET.Element) -> HistoricPlatformChange:
        return cls(
            arrival_platform=element.get("ar", ""),
            departure_platform=element.get("dp", ""),
            cause=element.get("cot", ""),
            timestamp=_parse_db_time(element.get("ts")),
        )


@dataclass
class Connection:
    """Information about a connecting train at a stop."""

    id: str = ""
    status: str = ""  # cs: w=WAITING, n=NO_WAIT, a=ALTERNATIVE
    eva: str = ""
    timestamp: datetime | None = None

    @classmethod
    def from_xml(cls, element: ET.Element) -> Connection:
        return cls(
            id=element.get("id", ""),
            status=element.get("cs", ""),
            eva=element.get("eva", ""),
            timestamp=_parse_db_time(element.get("ts")),
        )


@dataclass
class TimetableStop:
    """A single train stop within a timetable."""

    id: str
    eva: str = ""
    train_line: TrainLine | None = None
    arrival: ArrivalDeparture | None = None
    departure: ArrivalDeparture | None = None
    messages: list[Message] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    historic_delays: list[HistoricDelay] = field(default_factory=list)
    historic_platform_changes: list[HistoricPlatformChange] = field(default_factory=list)

    @classmethod
    def from_xml(cls, element: ET.Element, eva: str = "") -> TimetableStop:
        return cls(
            id=element.get("id", ""),
            eva=element.get("eva", eva),
            train_line=TrainLine.from_xml(element.find("tl")),
            arrival=ArrivalDeparture.from_xml(element.find("ar")),
            departure=ArrivalDeparture.from_xml(element.find("dp")),
            messages=[Message.from_xml(m) for m in element.findall("m")],
            connections=[Connection.from_xml(c) for c in element.findall("conn")],
            historic_delays=[HistoricDelay.from_xml(h) for h in element.findall("hd")],
            historic_platform_changes=[
                HistoricPlatformChange.from_xml(h) for h in element.findall("hpc")
            ],
        )

    @property
    def is_cancelled(self) -> bool:
        ar_cancelled = self.arrival.is_cancelled if self.arrival else False
        dp_cancelled = self.departure.is_cancelled if self.departure else False
        return ar_cancelled or dp_cancelled

    def merge_changes(self, changed: TimetableStop) -> None:
        """Apply a fchg/rchg stop onto this planned stop in-place."""
        if changed.train_line:
            self.train_line = changed.train_line
        if changed.arrival and self.arrival:
            _merge_event(self.arrival, changed.arrival)
        elif changed.arrival:
            self.arrival = changed.arrival
        if changed.departure and self.departure:
            _merge_event(self.departure, changed.departure)
        elif changed.departure:
            self.departure = changed.departure
        self.messages.extend(changed.messages)
        self.connections.extend(changed.connections)
        self.historic_delays.extend(changed.historic_delays)
        self.historic_platform_changes.extend(changed.historic_platform_changes)


def _merge_event(base: ArrivalDeparture, changed: ArrivalDeparture) -> None:
    if changed.changed_time:
        base.changed_time = changed.changed_time
    if changed.changed_platform:
        base.changed_platform = changed.changed_platform
    if changed.changed_path:
        base.changed_path = changed.changed_path
    if changed.changed_status:
        base.changed_status = changed.changed_status
    if changed.cancellation_time:
        base.cancellation_time = changed.cancellation_time
    if changed.changed_distant_endpoint:
        base.changed_distant_endpoint = changed.changed_distant_endpoint
    base.messages.extend(changed.messages)


@dataclass
class Timetable:
    station: str
    eva: str
    stops: list[TimetableStop] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)  # top-level disruption messages

    @classmethod
    def from_xml(cls, root: ET.Element) -> Timetable:
        timetable = cls(
            station=root.get("station", ""),
            eva=root.get("eva", ""),
            messages=[Message.from_xml(m) for m in root.findall("m")],
        )
        timetable.stops = [TimetableStop.from_xml(s, timetable.eva) for s in root.findall("s")]
        return timetable

    def merge_changes(self, changes: Timetable) -> None:
        """Merge fchg or rchg data into this timetable in-place."""
        stop_index = {s.id: s for s in self.stops}
        for changed_stop in changes.stops:
            if changed_stop.id in stop_index:
                stop_index[changed_stop.id].merge_changes(changed_stop)
            else:
                self.stops.append(changed_stop)
        self.messages.extend(changes.messages)
