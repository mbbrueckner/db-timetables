import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from db_timetables.models import (
    ArrivalDeparture,
    Connection,
    DistributorMessage,
    EventStatus,
    HistoricDelay,
    HistoricPlatformChange,
    Message,
    Station,
    Timetable,
    TimetableStop,
    TrainLine,
)


# Station
class TestStation:
    def test_from_xml(self):
        el = ET.fromstring('<station eva="8000105" name="Frankfurt(Main)Hbf" ds100="FF" lat="50.1067" lon="8.6631"/>')
        s = Station.from_xml(el)
        assert s.eva == "8000105"
        assert s.name == "Frankfurt(Main)Hbf"
        assert s.ds100 == "FF"
        assert s.lat == pytest.approx(50.1067)
        assert s.lon == pytest.approx(8.6631)

    def test_from_xml_missing_coords(self):
        el = ET.fromstring('<station eva="8000105" name="Frankfurt(Main)Hbf"/>')
        s = Station.from_xml(el)
        assert s.lat == 0.0
        assert s.lon == 0.0


# TrainLine
class TestTrainLine:
    def test_from_xml(self):
        el = ET.fromstring('<tl t="p" c="ICE" n="9551" o="80" f=""/>')
        tl = TrainLine.from_xml(el)
        assert tl.category == "ICE"
        assert tl.number == "9551"
        assert tl.owner == "80"
        assert tl.display_name == "ICE 9551"

    def test_display_name_no_number(self):
        el = ET.fromstring('<tl c="S"/>')
        tl = TrainLine.from_xml(el)
        assert tl.display_name == "S"

    def test_from_xml_none(self):
        assert TrainLine.from_xml(None) is None


# ArrivalDeparture

class TestArrivalDeparture:
    def _make(self, xml: str) -> ArrivalDeparture:
        return ArrivalDeparture.from_xml(ET.fromstring(xml))

    def test_planned_time_parsed(self):
        ad = self._make('<dp pt="2605141430" pp="7"/>')
        assert ad.planned_time == datetime(2026, 5, 14, 14, 30)
        assert ad.planned_platform == "7"

    def test_changed_time_parsed(self):
        ad = self._make('<dp pt="2605141430" ct="2605141445" pp="7"/>')
        assert ad.changed_time == datetime(2026, 5, 14, 14, 45)

    def test_effective_time_prefers_changed(self):
        ad = self._make('<dp pt="2605141430" ct="2605141445"/>')
        assert ad.effective_time == datetime(2026, 5, 14, 14, 45)

    def test_effective_time_falls_back_to_planned(self):
        ad = self._make('<dp pt="2605141430"/>')
        assert ad.effective_time == datetime(2026, 5, 14, 14, 30)

    def test_effective_platform_prefers_changed(self):
        ad = self._make('<dp pp="7" cp="8"/>')
        assert ad.effective_platform == "8"

    def test_effective_platform_falls_back_to_planned(self):
        ad = self._make('<dp pp="7"/>')
        assert ad.effective_platform == "7"

    def test_delay_minutes(self):
        ad = self._make('<dp pt="2605141430" ct="2605141445"/>')
        assert ad.delay_minutes == 15

    def test_delay_minutes_none_when_on_time(self):
        ad = self._make('<dp pt="2605141430"/>')
        assert ad.delay_minutes is None

    def test_is_cancelled_via_changed_status(self):
        ad = self._make('<dp pt="2605141430" cs="c"/>')
        assert ad.is_cancelled is True

    def test_is_cancelled_via_planned_status(self):
        ad = self._make('<dp pt="2605141430" ps="c"/>')
        assert ad.is_cancelled is True

    def test_not_cancelled(self):
        ad = self._make('<dp pt="2605141430" ps="p"/>')
        assert ad.is_cancelled is False

    def test_path_parsed(self):
        ad = self._make('<dp ppth="Hamburg Hbf|Berlin Hbf|München Hbf"/>')
        assert ad.planned_path == ["Hamburg Hbf", "Berlin Hbf", "München Hbf"]

    def test_hidden_flag(self):
        ad = self._make('<dp hi="1"/>')
        assert ad.hidden is True

    def test_from_xml_none(self):
        assert ArrivalDeparture.from_xml(None) is None

    def test_status_enum_type(self):
        ad = self._make('<dp ps="p" cs="c"/>')
        assert ad.planned_status == EventStatus.PLANNED
        assert ad.changed_status == EventStatus.CANCELLED


# Message
class TestMessage:
    def test_from_xml_basic(self):
        el = ET.fromstring('<m id="1" t="d" ts="2605141200" c="42" ext="Delay due to track works" int="internal note"/>')
        m = Message.from_xml(el)
        assert m.id == "1"
        assert m.code == 42
        assert m.external_text == "Delay due to track works"
        assert m.text == "internal note"

    def test_text_falls_back_to_external(self):
        el = ET.fromstring('<m id="1" ext="external only"/>')
        m = Message.from_xml(el)
        assert m.text == "external only"

    def test_deleted_flag(self):
        el = ET.fromstring('<m id="1" del="1"/>')
        assert Message.from_xml(el).deleted is True

    def test_trip_labels_parsed(self):
        el = ET.fromstring('<m id="1"><tl c="ICE" n="9551"/><tl c="IC" n="123"/></m>')
        m = Message.from_xml(el)
        assert len(m.trip_labels) == 2
        assert m.trip_labels[0].category == "ICE"


# TimetableStop
class TestTimetableStop:
    def _stop_xml(self, extra: str = "") -> ET.Element:
        return ET.fromstring(
            f'<s id="1234567890123456789-2605141430-5">'
            f'<tl t="p" c="ICE" n="9551" o="80"/>'
            f'<dp pt="2605141430" pp="7"/>'
            f'<ar pt="2605141425" pp="7"/>'
            f'{extra}'
            f'</s>'
        )

    def test_basic_parsing(self):
        stop = TimetableStop.from_xml(self._stop_xml())
        assert stop.train_line.display_name == "ICE 9551"
        assert stop.departure.planned_platform == "7"
        assert stop.arrival.planned_time == datetime(2026, 5, 14, 14, 25)

    def test_is_cancelled_false(self):
        stop = TimetableStop.from_xml(self._stop_xml())
        assert stop.is_cancelled is False

    def test_is_cancelled_true(self):
        el = ET.fromstring(
            '<s id="abc">'
            '<tl c="RE" n="1"/>'
            '<dp pt="2605141430" cs="c"/>'
            '</s>'
        )
        stop = TimetableStop.from_xml(el)
        assert stop.is_cancelled is True

    def test_merge_changes_delay(self):
        planned = TimetableStop.from_xml(self._stop_xml())
        changed_el = ET.fromstring(
            '<s id="1234567890123456789-2605141430-5">'
            '<dp ct="2605141450" cp="8"/>'
            '</s>'
        )
        changed = TimetableStop.from_xml(changed_el)
        planned.merge_changes(changed)
        assert planned.departure.changed_time == datetime(2026, 5, 14, 14, 50)
        assert planned.departure.changed_platform == "8"
        assert planned.departure.delay_minutes == 20

    def test_merge_changes_cancellation(self):
        planned = TimetableStop.from_xml(self._stop_xml())
        changed_el = ET.fromstring(
            '<s id="1234567890123456789-2605141430-5">'
            '<dp cs="c"/>'
            '</s>'
        )
        planned.merge_changes(TimetableStop.from_xml(changed_el))
        assert planned.is_cancelled is True


# Timetable
class TestTimetable:
    def _timetable_xml(self) -> str:
        return (
            '<timetable station="Frankfurt(Main)Hbf" eva="8000105">'
            '<s id="stop-1"><tl c="ICE" n="9551"/><dp pt="2605141430" pp="7"/></s>'
            '<s id="stop-2"><tl c="RE" n="1"/><dp pt="2605141445" pp="3"/></s>'
            '</timetable>'
        )

    def test_from_xml(self):
        tt = Timetable.from_xml(ET.fromstring(self._timetable_xml()))
        assert tt.station == "Frankfurt(Main)Hbf"
        assert tt.eva == "8000105"
        assert len(tt.stops) == 2

    def test_merge_changes_updates_existing_stop(self):
        tt = Timetable.from_xml(ET.fromstring(self._timetable_xml()))
        changes_xml = (
            '<timetable station="Frankfurt(Main)Hbf" eva="8000105">'
            '<s id="stop-1"><dp ct="2605141445"/></s>'
            '</timetable>'
        )
        tt.merge_changes(Timetable.from_xml(ET.fromstring(changes_xml)))
        stop = next(s for s in tt.stops if s.id == "stop-1")
        assert stop.departure.delay_minutes == 15

    def test_merge_changes_appends_new_stop(self):
        tt = Timetable.from_xml(ET.fromstring(self._timetable_xml()))
        changes_xml = (
            '<timetable station="Frankfurt(Main)Hbf" eva="8000105">'
            '<s id="stop-99"><tl c="S" n="1"/><dp pt="2605141500"/></s>'
            '</timetable>'
        )
        tt.merge_changes(Timetable.from_xml(ET.fromstring(changes_xml)))
        assert len(tt.stops) == 3