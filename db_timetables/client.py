from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime

import requests

from .exceptions import AuthenticationError, DBApiError, NotFoundError, RateLimitError
from .models import Station, Timetable

BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"


class TimetablesClient:
    """Client for the Deutsche Bahn Timetables API.
    Args:
        client_id: DB-Client-Id from the DB API Marketplace.
        api_key: DB-Api-Key from the DB API Marketplace.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(self, client_id: str, api_key: str, timeout: int = 10):
        self._session = requests.Session()
        self._session.headers.update(
            {
                "DB-Client-Id": client_id,
                "DB-Api-Key": api_key,
                "Accept": "application/xml",
            }
        )
        self._timeout = timeout


    def get_station(self, pattern: str) -> list[Station]:
        """Search for stations by name pattern.

        Args:
            pattern: Station name or partial name (e.g. "Frankfurt").

        Returns:
            List of matching Station objects.
        """
        root = self._get_xml(f"/station/{pattern}")
        return [Station.from_xml(el) for el in root.findall("station")]

    def get_plan(self, eva: str, date: datetime | None = None, hour: int | None = None) -> Timetable:
        """Fetch the planned timetable for a station at a given date and hour.

        Args:
            eva: EVA station number (e.g. "8000105" for Frankfurt Hbf).
            date: Date to query. Defaults to today.
            hour: Hour of day (0-23). Defaults to the current hour.

        Returns:
            Timetable with planned stops for the given hour.
        """
        now = datetime.now()
        date = date or now
        hour = hour if hour is not None else now.hour
        date_str = date.strftime("%y%m%d")
        hour_str = f"{hour:02d}"
        root = self._get_xml(f"/plan/{eva}/{date_str}/{hour_str}")
        return Timetable.from_xml(root)

    def get_full_changes(self, eva: str) -> Timetable:
        """Fetch all current deviations from the planned timetable (fchg).

        This returns the full set of changes for all trains at the station,
        including delays, platform changes, and cancellations.

        Args:
            eva: EVA station number.

        Returns:
            Timetable containing only changed stops (no planned data).
        """
        root = self._get_xml(f"/fchg/{eva}")
        return Timetable.from_xml(root)

    def get_recent_changes(self, eva: str) -> Timetable:
        """Fetch recent changes since the last request (rchg).

        Returns only changes that occurred since the last polling call.
        Useful for efficient polling when you already have a baseline timetable.

        Args:
            eva: EVA station number.

        Returns:
            Timetable containing only recently changed stops.
        """
        root = self._get_xml(f"/rchg/{eva}")
        return Timetable.from_xml(root)

    def get_timetable_with_changes(
        self,
        eva: str,
        date: datetime | None = None,
        hour: int | None = None,
    ) -> Timetable:
        """Fetch the planned timetable and merge all current changes into it.

        Convenience method combining get_plan() and get_full_changes().

        Args:
            eva: EVA station number.
            date: Date to query. Defaults to today.
            hour: Hour of day (0-23). Defaults to the current hour.

        Returns:
            Timetable with planned stops updated to reflect current reality.
        """
        plan = self.get_plan(eva, date, hour)
        changes = self.get_full_changes(eva)
        plan.merge_changes(changes)
        return plan


    def _get(self, path: str) -> requests.Response:
        url = BASE_URL + path
        try:
            response = self._session.get(url, timeout=self._timeout)
        except requests.ConnectionError as exc:
            raise DBApiError(f"Connection failed: {exc}") from exc
        except requests.Timeout as exc:
            raise DBApiError(f"Request timed out after {self._timeout}s") from exc

        if response.status_code == 401:
            raise AuthenticationError("Invalid credentials (401)", status_code=401)
        if response.status_code == 403:
            raise AuthenticationError("Access denied (403)", status_code=403)
        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {path}", status_code=404)
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded (429)", status_code=429)
        if not response.ok:
            raise DBApiError(
                f"API error {response.status_code}: {response.text[:200]}",
                status_code=response.status_code,
            )

        return response

    def _get_xml(self, path: str) -> ET.Element:
        response = self._get(path)
        try:
            return ET.fromstring(response.content)
        except ET.ParseError as exc:
            raise DBApiError(f"Failed to parse XML response: {exc}") from exc