import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from deutsche_bahn.stada import StaDaClient
from deutsche_bahn.stada.exceptions import (
    AuthenticationError,
    DBApiError,
    NotFoundError,
    RateLimitError,
)


def _make_response(status_code: int, body: dict | None = None) -> MagicMock:
    r = MagicMock()
    r.status_code = status_code
    r.ok = status_code < 400
    raw = json.dumps(body).encode() if body is not None else b""
    r.text = raw.decode()
    r.json.return_value = body
    if body is None:
        r.json.side_effect = ValueError("no body")
    return r


@pytest.fixture
def client():
    return StaDaClient(client_id="test-id", api_key="test-key")


_STATION_DICT = {
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
    "hasMobilityService": "yes",
    "evaNumbers": [
        {
            "number": 8000105,
            "isMain": True,
            "geographicCoordinates": {"type": "Point", "coordinates": [8.6631, 50.1067]},
        }
    ],
    "ril100Identifiers": [
        {
            "rilIdentifier": "FF",
            "isMain": True,
            "primaryLocationCode": "DE12345",
            "steamPermission": "no",
            "geographicCoordinates": {"type": "Point", "coordinates": [8.6631, 50.1067]},
        }
    ],
    "mailingAddress": {"city": "Frankfurt", "houseNumber": "1", "street": "Am Hauptbahnhof", "zipcode": "60329"},
    "regionalbereich": {"name": "Mitte", "number": 3, "shortName": "Mi"},
    "stationManagement": {"name": "Frankfurt", "number": 123},
    "szentrale": {
        "number": 50,
        "name": "Frankfurt 3-S-Zentrale",
        "publicPhoneNumber": "069 130 12345",
        "publicFaxNumber": "",
        "internalPhoneNumber": "",
        "internalFaxNumber": "",
        "mobilePhoneNumber": "",
        "email": "3sz-frankfurt@deutschebahn.com",
        "address": {"city": "Frankfurt", "houseNumber": "1", "street": "Am Hauptbahnhof", "zipcode": "60329"},
    },
    "aufgabentraeger": {"name": "Rhein-Main-Verkehrsverbund", "shortName": "RMV"},
    "timeTableOffice": {"name": "Frankfurt", "email": "tf-frankfurt@deutschebahn.com"},
    "wirelessLan": {"amount": 10, "installDate": "2015-01-01", "product": "DB WiFi"},
    "localServiceStaff": {"availability": {"monday": {"fromTime": "07:00", "toTime": "22:00"}}},
    "DBinformation": {"availability": {"monday": {"fromTime": "07:00", "toTime": "22:00"}}},
    "mobilityServiceStaff": {
        "meetingPoint": "Haupteingang",
        "serviceOnBehalf": True,
        "staffOnSite": True,
        "availability": {"monday1": {"fromTime": "07:00", "toTime": "13:00"}, "monday2": {"fromTime": "14:00", "toTime": "20:00"}},
    },
    "localizedNames": {"dan": "", "dsb": "", "frr": "", "hsb": "", "nds": ""},
}

_STATION_QUERY = {"total": 1, "offset": 0, "limit": 10, "result": [_STATION_DICT]}

_SZENTRALE_DICT = {
    "number": 50,
    "name": "Frankfurt 3-S-Zentrale",
    "publicPhoneNumber": "069 130 12345",
    "publicFaxNumber": "",
    "internalPhoneNumber": "",
    "internalFaxNumber": "",
    "mobilePhoneNumber": "",
    "email": "3sz-frankfurt@deutschebahn.com",
    "address": {"city": "Frankfurt", "houseNumber": "1", "street": "Am Hauptbahnhof", "zipcode": "60329"},
}

_SZENTRALE_QUERY = {"total": 1, "offset": 0, "limit": 10, "result": [_SZENTRALE_DICT]}


class TestStaDaClientErrorHandling:
    def test_401_raises_authentication_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(401)):
            with pytest.raises(AuthenticationError) as exc:
                client.get_stations()
            assert exc.value.status_code == 401

    def test_403_raises_authentication_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(403)):
            with pytest.raises(AuthenticationError) as exc:
                client.get_stations()
            assert exc.value.status_code == 403

    def test_404_raises_not_found_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(404)):
            with pytest.raises(NotFoundError) as exc:
                client.get_station(9999)
            assert exc.value.status_code == 404

    def test_429_raises_rate_limit_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(429)):
            with pytest.raises(RateLimitError) as exc:
                client.get_stations()
            assert exc.value.status_code == 429

    def test_500_raises_db_api_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(500)):
            with pytest.raises(DBApiError) as exc:
                client.get_stations()
            assert exc.value.status_code == 500

    def test_connection_error_raises_db_api_error(self, client):
        with patch.object(client._session, "get", side_effect=requests.ConnectionError("unreachable")):
            with pytest.raises(DBApiError, match="Connection failed"):
                client.get_stations()

    def test_timeout_raises_db_api_error(self, client):
        with patch.object(client._session, "get", side_effect=requests.Timeout()):
            with pytest.raises(DBApiError, match="timed out"):
                client.get_stations()

    def test_invalid_json_raises_db_api_error(self, client):
        r = MagicMock()
        r.status_code = 200
        r.ok = True
        r.text = "not json"
        r.json.side_effect = ValueError("invalid json")
        with patch.object(client._session, "get", return_value=r):
            with pytest.raises(DBApiError, match="Failed to parse JSON"):
                client.get_stations()


class TestStaDaClientParsing:
    def test_get_stations_returns_query(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _STATION_QUERY)):
            result = client.get_stations(searchstring="Frankfurt")
        assert result.total == 1
        assert len(result.result) == 1
        station = result.result[0]
        assert station.number == 1071
        assert station.name == "Frankfurt(Main)Hbf"
        assert station.has_wifi is True
        assert station.federal_state == "Hessen"

    def test_get_stations_maps_eva_numbers(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _STATION_QUERY)):
            result = client.get_stations()
        eva = result.result[0].eva_numbers[0]
        assert eva.number == 8000105
        assert eva.is_main is True
        assert eva.geographic_coordinates is not None
        assert eva.geographic_coordinates.coordinates == [8.6631, 50.1067]

    def test_get_stations_maps_ril100(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _STATION_QUERY)):
            result = client.get_stations()
        ril = result.result[0].ril100_identifiers[0]
        assert ril.ril_identifier == "FF"
        assert ril.is_main is True

    def test_get_stations_maps_nested_objects(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _STATION_QUERY)):
            result = client.get_stations()
        station = result.result[0]
        assert station.mailing_address is not None
        assert station.mailing_address.city == "Frankfurt"
        assert station.regional_bereich is not None
        assert station.regional_bereich.short_name == "Mi"
        assert station.station_management is not None
        assert station.station_management.number == 123
        assert station.szentrale is not None
        assert station.szentrale.number == 50
        assert station.aufgabentraeger is not None
        assert station.aufgabentraeger.short_name == "RMV"
        assert station.timetable_office is not None
        assert station.timetable_office.email == "tf-frankfurt@deutschebahn.com"
        assert station.wireless_lan is not None
        assert station.wireless_lan.amount == 10

    def test_get_stations_maps_schedules(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _STATION_QUERY)):
            result = client.get_stations()
        station = result.result[0]
        assert station.local_service_staff is not None
        assert station.local_service_staff.availability is not None
        assert station.local_service_staff.availability.monday is not None
        assert station.local_service_staff.availability.monday.from_time == "07:00"
        assert station.db_information is not None
        assert station.mobility_service_staff is not None
        assert station.mobility_service_staff.staff_on_site is True
        assert station.mobility_service_staff.availability is not None
        assert station.mobility_service_staff.availability.monday1 is not None

    def test_get_station_by_id(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _STATION_QUERY)):
            result = client.get_station(1071)
        assert result.result[0].number == 1071

    def test_get_stations_empty_result(self, client):
        body = {"total": 0, "offset": 0, "limit": 10, "result": []}
        with patch.object(client._session, "get", return_value=_make_response(200, body)):
            result = client.get_stations(searchstring="nonexistent")
        assert result.total == 0
        assert result.result == []

    def test_get_szentralen_returns_query(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _SZENTRALE_QUERY)):
            result = client.get_szentralen()
        assert result.total == 1
        assert len(result.result) == 1
        sz = result.result[0]
        assert sz.number == 50
        assert sz.name == "Frankfurt 3-S-Zentrale"
        assert sz.email == "3sz-frankfurt@deutschebahn.com"
        assert sz.address is not None
        assert sz.address.city == "Frankfurt"

    def test_get_szentrale_by_id(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _SZENTRALE_QUERY)):
            result = client.get_szentrale(50)
        assert result.result[0].number == 50

    def test_get_stations_passes_filter_params(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _STATION_QUERY)) as mock_get:
            client.get_stations(searchstring="Frankfurt", category="1-3", federalstate="hessen", limit=5)
        _, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        assert params["searchstring"] == "Frankfurt"
        assert params["category"] == "1-3"
        assert params["federalstate"] == "hessen"
        assert params["limit"] == 5

    def test_get_stations_omits_none_params(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, _STATION_QUERY)) as mock_get:
            client.get_stations(searchstring="Frankfurt")
        _, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        assert "category" not in params
        assert "federalstate" not in params