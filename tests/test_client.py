from unittest.mock import MagicMock, patch

import pytest

from deutsche_bahn.timetables import TimetablesClient
from deutsche_bahn.timetables.exceptions import (
    AuthenticationError,
    DBApiError,
    NotFoundError,
    RateLimitError,
)


def _make_response(status_code: int, content: bytes = b"") -> MagicMock:
    r = MagicMock()
    r.status_code = status_code
    r.ok = status_code < 400
    r.content = content
    r.text = content.decode("utf-8", errors="replace")
    return r


@pytest.fixture
def client():
    return TimetablesClient(client_id="test-id", api_key="test-key")


class TestClientErrorHandling:
    def test_401_raises_authentication_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(401)):
            with pytest.raises(AuthenticationError) as exc:
                client.get_station("Frankfurt")
            assert exc.value.status_code == 401

    def test_403_raises_authentication_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(403)):
            with pytest.raises(AuthenticationError) as exc:
                client.get_station("Frankfurt")
            assert exc.value.status_code == 403

    def test_404_raises_not_found_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(404)):
            with pytest.raises(NotFoundError) as exc:
                client.get_station("Frankfurt")
            assert exc.value.status_code == 404

    def test_429_raises_rate_limit_error(self, client):
        with patch.object(client._session, "get", return_value=_make_response(429)):
            with pytest.raises(RateLimitError) as exc:
                client.get_station("Frankfurt")
            assert exc.value.status_code == 429

    def test_500_raises_db_api_error(self, client):
        with patch.object(
            client._session, "get", return_value=_make_response(500, b"Internal Server Error")
        ):
            with pytest.raises(DBApiError) as exc:
                client.get_station("Frankfurt")
            assert exc.value.status_code == 500

    def test_connection_error_raises_db_api_error(self, client):
        import requests

        with patch.object(
            client._session, "get", side_effect=requests.ConnectionError("unreachable")
        ):
            with pytest.raises(DBApiError, match="Connection failed"):
                client.get_station("Frankfurt")

    def test_timeout_raises_db_api_error(self, client):
        import requests

        with patch.object(client._session, "get", side_effect=requests.Timeout()):
            with pytest.raises(DBApiError, match="timed out"):
                client.get_station("Frankfurt")


class TestClientParsing:
    _STATION_XML = (
        b'<?xml version="1.0"?><stations>'
        b'<station eva="8000105" name="Frankfurt(Main)Hbf" ds100="FF" lat="50.1067" lon="8.6631"/>'
        b"</stations>"
    )
    _PLAN_XML = (
        b'<?xml version="1.0"?>'
        b'<timetable station="Frankfurt(Main)Hbf" eva="8000105">'
        b'<s id="stop-1"><tl c="ICE" n="9551"/><dp pt="2605141430" pp="7"/></s>'
        b"</timetable>"
    )

    def test_get_station_returns_stations(self, client):
        with patch.object(
            client._session, "get", return_value=_make_response(200, self._STATION_XML)
        ):
            stations = client.get_station("Frankfurt")
        assert len(stations) == 1
        assert stations[0].eva == "8000105"
        assert stations[0].name == "Frankfurt(Main)Hbf"

    def test_get_plan_returns_timetable(self, client):
        with patch.object(client._session, "get", return_value=_make_response(200, self._PLAN_XML)):
            plan = client.get_plan("8000105")
        assert plan.station == "Frankfurt(Main)Hbf"
        assert len(plan.stops) == 1

    def test_invalid_xml_raises_db_api_error(self, client):
        with patch.object(
            client._session, "get", return_value=_make_response(200, b"not xml at all")
        ):
            with pytest.raises(DBApiError, match="Failed to parse XML"):
                client.get_station("Frankfurt")
