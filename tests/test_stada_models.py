from deutsche_bahn.stada.models import (
    Address,
    Aufgabentraeger,
    DaySchedule,
    DoubleSchedule,
    EVANumber,
    GeographicPoint,
    LocalizedNames,
    MobilityServiceStaff,
    OpeningHours,
    RegionalBereich,
    RiL100Identifier,
    Schedule,
    StadaStation,
    StationManagement,
    StationQuery,
    SZentrale,
    SZentraleQuery,
    TimetableOffice,
    WirelessLan,
)


class TestAddress:
    def test_from_dict(self):
        a = Address.from_dict({"city": "Frankfurt", "houseNumber": "1", "street": "Bahnhofstr.", "zipcode": "60329"})
        assert a.city == "Frankfurt"
        assert a.house_number == "1"
        assert a.street == "Bahnhofstr."
        assert a.zipcode == "60329"

    def test_from_dict_empty(self):
        a = Address.from_dict({})
        assert a.city == ""
        assert a.house_number == ""


class TestGeographicPoint:
    def test_from_dict(self):
        gp = GeographicPoint.from_dict({"type": "Point", "coordinates": [8.6631, 50.1067]})
        assert gp.type == "Point"
        assert gp.coordinates == [8.6631, 50.1067]

    def test_from_dict_empty(self):
        gp = GeographicPoint.from_dict({})
        assert gp.type == ""
        assert gp.coordinates == []


class TestOpeningHours:
    def test_from_dict(self):
        oh = OpeningHours.from_dict({"fromTime": "07:00", "toTime": "22:00"})
        assert oh.from_time == "07:00"
        assert oh.to_time == "22:00"

    def test_from_dict_empty(self):
        oh = OpeningHours.from_dict({})
        assert oh.from_time == ""
        assert oh.to_time == ""


class TestDaySchedule:
    def test_from_dict_with_days(self):
        ds = DaySchedule.from_dict({
            "monday": {"fromTime": "07:00", "toTime": "22:00"},
            "saturday": {"fromTime": "08:00", "toTime": "20:00"},
        })
        assert ds.monday is not None
        assert ds.monday.from_time == "07:00"
        assert ds.saturday is not None
        assert ds.saturday.to_time == "20:00"
        assert ds.tuesday is None
        assert ds.sunday is None
        assert ds.holiday is None

    def test_from_dict_all_none(self):
        ds = DaySchedule.from_dict({})
        for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "holiday"):
            assert getattr(ds, day) is None


class TestDoubleSchedule:
    def test_from_dict(self):
        ds = DoubleSchedule.from_dict({
            "monday1": {"fromTime": "07:00", "toTime": "13:00"},
            "monday2": {"fromTime": "14:00", "toTime": "20:00"},
        })
        assert ds.monday1 is not None
        assert ds.monday1.from_time == "07:00"
        assert ds.monday2 is not None
        assert ds.monday2.to_time == "20:00"
        assert ds.tuesday1 is None

    def test_from_dict_empty(self):
        ds = DoubleSchedule.from_dict({})
        assert ds.monday1 is None
        assert ds.friday2 is None


class TestSchedule:
    def test_from_dict_with_availability(self):
        s = Schedule.from_dict({"availability": {"monday": {"fromTime": "07:00", "toTime": "22:00"}}})
        assert s.availability is not None
        assert s.availability.monday is not None
        assert s.availability.monday.from_time == "07:00"

    def test_from_dict_no_availability(self):
        s = Schedule.from_dict({})
        assert s.availability is None


class TestEVANumber:
    def test_from_dict_full(self):
        e = EVANumber.from_dict({
            "number": 8000105,
            "isMain": True,
            "geographicCoordinates": {"type": "Point", "coordinates": [8.6631, 50.1067]},
        })
        assert e.number == 8000105
        assert e.is_main is True
        assert e.geographic_coordinates is not None
        assert e.geographic_coordinates.coordinates == [8.6631, 50.1067]

    def test_from_dict_no_coordinates(self):
        e = EVANumber.from_dict({"number": 8000105, "isMain": False})
        assert e.geographic_coordinates is None

    def test_from_dict_defaults(self):
        e = EVANumber.from_dict({})
        assert e.number == 0
        assert e.is_main is False


class TestRiL100Identifier:
    def test_from_dict_full(self):
        r = RiL100Identifier.from_dict({
            "rilIdentifier": "FF",
            "isMain": True,
            "primaryLocationCode": "DE12345",
            "steamPermission": "no",
            "geographicCoordinates": {"type": "Point", "coordinates": [8.6631, 50.1067]},
        })
        assert r.ril_identifier == "FF"
        assert r.is_main is True
        assert r.primary_location_code == "DE12345"
        assert r.steam_permission == "no"
        assert r.geographic_coordinates is not None

    def test_from_dict_no_coordinates(self):
        r = RiL100Identifier.from_dict({"rilIdentifier": "FF"})
        assert r.geographic_coordinates is None


class TestAufgabentraeger:
    def test_from_dict(self):
        a = Aufgabentraeger.from_dict({"name": "Rhein-Main-Verkehrsverbund", "shortName": "RMV"})
        assert a.name == "Rhein-Main-Verkehrsverbund"
        assert a.short_name == "RMV"


class TestRegionalBereich:
    def test_from_dict(self):
        rb = RegionalBereich.from_dict({"name": "Mitte", "number": 3, "shortName": "Mi"})
        assert rb.name == "Mitte"
        assert rb.number == 3
        assert rb.short_name == "Mi"


class TestStationManagement:
    def test_from_dict(self):
        sm = StationManagement.from_dict({"name": "Frankfurt", "number": 123})
        assert sm.name == "Frankfurt"
        assert sm.number == 123


class TestTimetableOffice:
    def test_from_dict(self):
        to = TimetableOffice.from_dict({"name": "Frankfurt", "email": "tf@db.com"})
        assert to.name == "Frankfurt"
        assert to.email == "tf@db.com"


class TestWirelessLan:
    def test_from_dict(self):
        wl = WirelessLan.from_dict({"amount": 10, "installDate": "2015-01-01", "product": "DB WiFi"})
        assert wl.amount == 10
        assert wl.install_date == "2015-01-01"
        assert wl.product == "DB WiFi"


class TestMobilityServiceStaff:
    def test_from_dict_full(self):
        ms = MobilityServiceStaff.from_dict({
            "meetingPoint": "Haupteingang",
            "serviceOnBehalf": True,
            "staffOnSite": True,
            "availability": {
                "monday1": {"fromTime": "07:00", "toTime": "13:00"},
                "monday2": {"fromTime": "14:00", "toTime": "20:00"},
            },
        })
        assert ms.meeting_point == "Haupteingang"
        assert ms.service_on_behalf is True
        assert ms.staff_on_site is True
        assert ms.availability is not None
        assert ms.availability.monday1 is not None

    def test_from_dict_no_availability(self):
        ms = MobilityServiceStaff.from_dict({})
        assert ms.availability is None


class TestLocalizedNames:
    def test_from_dict(self):
        ln = LocalizedNames.from_dict({"dan": "Flensborg", "dsb": "", "frr": "", "hsb": "", "nds": ""})
        assert ln.dan == "Flensborg"
        assert ln.dsb == ""

    def test_from_dict_empty(self):
        ln = LocalizedNames.from_dict({})
        assert ln.dan == ""
        assert ln.nds == ""


class TestSZentrale:
    def test_from_dict_full(self):
        sz = SZentrale.from_dict({
            "number": 50,
            "name": "Frankfurt 3-S-Zentrale",
            "publicPhoneNumber": "069 130 12345",
            "publicFaxNumber": "069 130 12346",
            "internalPhoneNumber": "12345",
            "internalFaxNumber": "12346",
            "mobilePhoneNumber": "0170 12345",
            "email": "3sz@db.com",
            "address": {"city": "Frankfurt", "houseNumber": "1", "street": "Bahnhofstr.", "zipcode": "60329"},
        })
        assert sz.number == 50
        assert sz.name == "Frankfurt 3-S-Zentrale"
        assert sz.public_phone_number == "069 130 12345"
        assert sz.email == "3sz@db.com"
        assert sz.address is not None
        assert sz.address.city == "Frankfurt"

    def test_from_dict_no_address(self):
        sz = SZentrale.from_dict({"number": 50, "name": "Test"})
        assert sz.address is None


class TestStadaStation:
    _FULL = {
        "number": 1071,
        "name": "Frankfurt(Main)Hbf",
        "category": 1,
        "priceCategory": 1,
        "federalState": "Hessen",
        "federalStateCode": "HE",
        "countryCode": "DE",
        "municipalityCode": "06412000",
        "ifopt": "de:06412:10",
        "hasWiFi": True,
        "hasDBLounge": True,
        "hasTravelCenter": True,
        "hasLockerSystem": True,
        "hasPublicFacilities": True,
        "hasLocalPublicTransport": True,
        "hasTaxiRank": True,
        "hasParking": True,
        "hasBicycleParking": True,
        "hasCarRental": True,
        "hasRailwayMission": True,
        "hasLostAndFound": True,
        "hasTravelNecessities": True,
        "hasSteplessAccess": "yes",
        "hasMobilityService": "partial",
        "evaNumbers": [
            {"number": 8000105, "isMain": True, "geographicCoordinates": {"type": "Point", "coordinates": [8.6631, 50.1067]}}
        ],
        "ril100Identifiers": [
            {"rilIdentifier": "FF", "isMain": True, "primaryLocationCode": "DE12345", "steamPermission": "no"}
        ],
        "mailingAddress": {"city": "Frankfurt", "houseNumber": "1", "street": "Bahnhofstr.", "zipcode": "60329"},
        "regionalbereich": {"name": "Mitte", "number": 3, "shortName": "Mi"},
        "stationManagement": {"name": "Frankfurt", "number": 123},
        "szentrale": {"number": 50, "name": "3-S-Zentrale Frankfurt"},
        "aufgabentraeger": {"name": "RMV", "shortName": "RMV"},
        "timeTableOffice": {"name": "Frankfurt", "email": "tf@db.com"},
        "wirelessLan": {"amount": 10, "installDate": "2015-01-01", "product": "DB WiFi"},
        "localServiceStaff": {"availability": {"monday": {"fromTime": "07:00", "toTime": "22:00"}}},
        "DBinformation": {"availability": {"tuesday": {"fromTime": "08:00", "toTime": "21:00"}}},
        "mobilityServiceStaff": {
            "meetingPoint": "Haupteingang",
            "serviceOnBehalf": True,
            "staffOnSite": True,
            "availability": {"monday1": {"fromTime": "07:00", "toTime": "13:00"}},
        },
        "localizedNames": {"dan": "", "dsb": "", "frr": "", "hsb": "", "nds": ""},
    }

    def test_basic_fields(self):
        s = StadaStation.from_dict(self._FULL)
        assert s.number == 1071
        assert s.name == "Frankfurt(Main)Hbf"
        assert s.category == 1
        assert s.price_category == 1
        assert s.federal_state == "Hessen"
        assert s.federal_state_code == "HE"
        assert s.country_code == "DE"
        assert s.municipality_code == "06412000"
        assert s.ifopt == "de:06412:10"

    def test_boolean_amenities(self):
        s = StadaStation.from_dict(self._FULL)
        assert s.has_wifi is True
        assert s.has_db_lounge is True
        assert s.has_travel_center is True
        assert s.has_locker_system is True
        assert s.has_public_facilities is True
        assert s.has_local_public_transport is True
        assert s.has_taxi_rank is True
        assert s.has_parking is True
        assert s.has_bicycle_parking is True
        assert s.has_car_rental is True
        assert s.has_railway_mission is True
        assert s.has_lost_and_found is True
        assert s.has_travel_necessities is True

    def test_string_amenities(self):
        s = StadaStation.from_dict(self._FULL)
        assert s.has_stepless_access == "yes"
        assert s.has_mobility_service == "partial"

    def test_eva_numbers(self):
        s = StadaStation.from_dict(self._FULL)
        assert len(s.eva_numbers) == 1
        assert s.eva_numbers[0].number == 8000105
        assert s.eva_numbers[0].is_main is True

    def test_ril100_identifiers(self):
        s = StadaStation.from_dict(self._FULL)
        assert len(s.ril100_identifiers) == 1
        assert s.ril100_identifiers[0].ril_identifier == "FF"

    def test_nested_objects(self):
        s = StadaStation.from_dict(self._FULL)
        assert s.mailing_address is not None
        assert s.mailing_address.city == "Frankfurt"
        assert s.regional_bereich is not None
        assert s.regional_bereich.short_name == "Mi"
        assert s.station_management is not None
        assert s.station_management.number == 123
        assert s.szentrale is not None
        assert s.szentrale.number == 50
        assert s.aufgabentraeger is not None
        assert s.aufgabentraeger.short_name == "RMV"
        assert s.timetable_office is not None
        assert s.timetable_office.email == "tf@db.com"
        assert s.wireless_lan is not None
        assert s.wireless_lan.amount == 10

    def test_schedules(self):
        s = StadaStation.from_dict(self._FULL)
        assert s.local_service_staff is not None
        assert s.local_service_staff.availability is not None
        assert s.local_service_staff.availability.monday is not None
        assert s.local_service_staff.availability.monday.from_time == "07:00"
        assert s.db_information is not None
        assert s.db_information.availability is not None
        assert s.db_information.availability.tuesday is not None

    def test_mobility_service_staff(self):
        s = StadaStation.from_dict(self._FULL)
        assert s.mobility_service_staff is not None
        assert s.mobility_service_staff.meeting_point == "Haupteingang"
        assert s.mobility_service_staff.availability is not None
        assert s.mobility_service_staff.availability.monday1 is not None

    def test_localized_names(self):
        s = StadaStation.from_dict(self._FULL)
        assert s.localized_names is not None
        assert s.localized_names.dan == ""

    def test_optional_fields_absent(self):
        s = StadaStation.from_dict({"number": 1, "name": "Minimal"})
        assert s.mailing_address is None
        assert s.regional_bereich is None
        assert s.station_management is None
        assert s.szentrale is None
        assert s.aufgabentraeger is None
        assert s.timetable_office is None
        assert s.wireless_lan is None
        assert s.local_service_staff is None
        assert s.db_information is None
        assert s.mobility_service_staff is None
        assert s.localized_names is None
        assert s.eva_numbers == []
        assert s.ril100_identifiers == []

    def test_boolean_defaults_false(self):
        s = StadaStation.from_dict({})
        assert s.has_wifi is False
        assert s.has_parking is False


class TestStationQuery:
    def test_from_dict(self):
        q = StationQuery.from_dict({
            "total": 2,
            "offset": 0,
            "limit": 10,
            "result": [
                {"number": 1, "name": "Bahnhof A"},
                {"number": 2, "name": "Bahnhof B"},
            ],
        })
        assert q.total == 2
        assert q.offset == 0
        assert q.limit == 10
        assert len(q.result) == 2
        assert q.result[0].name == "Bahnhof A"
        assert q.result[1].number == 2

    def test_from_dict_empty_result(self):
        q = StationQuery.from_dict({"total": 0, "offset": 0, "limit": 10, "result": []})
        assert q.result == []

    def test_from_dict_defaults(self):
        q = StationQuery.from_dict({})
        assert q.total == 0
        assert q.result == []


class TestSZentraleQuery:
    def test_from_dict(self):
        q = SZentraleQuery.from_dict({
            "total": 1,
            "offset": 0,
            "limit": 10,
            "result": [{"number": 50, "name": "Frankfurt 3-S-Zentrale"}],
        })
        assert q.total == 1
        assert len(q.result) == 1
        assert q.result[0].number == 50

    def test_from_dict_defaults(self):
        q = SZentraleQuery.from_dict({})
        assert q.total == 0
        assert q.result == []