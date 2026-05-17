from __future__ import annotations

import requests

from .exceptions import AuthenticationError, DBApiError, NotFoundError, RateLimitError
from .models import StationQuery, SZentraleQuery

BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/station-data/v2"


class StaDaClient:
    """Client for the Deutsche Bahn StaDa Station Data API (v2.11.0).

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
                "Accept": "application/json",
            }
        )
        self._timeout = timeout

    def get_stations(
        self,
        *,
        searchstring: str | None = None,
        category: str | None = None,
        federalstate: str | None = None,
        eva: int | None = None,
        ril: str | None = None,
        logicaloperator: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> StationQuery:
        """Search for stations with optional filters.

        Args:
            searchstring: Station name pattern. Supports wildcards * and ?.
            category: Filter by category range or list (e.g. "1-3" or "1,3,5").
            federalstate: Filter by federal state (e.g. "bayern,hamburg").
            eva: Filter by EVA number.
            ril: Filter by Ril100 identifier.
            logicaloperator: Combine filters with "and" (default) or "or".
            offset: Pagination offset.
            limit: Maximum results to return (hard cap 10000).

        Returns:
            StationQuery with matching stations and pagination metadata.
        """
        params = {
            k: v
            for k, v in {
                "searchstring": searchstring,
                "category": category,
                "federalstate": federalstate,
                "eva": eva,
                "ril": ril,
                "logicaloperator": logicaloperator,
                "offset": offset,
                "limit": limit,
            }.items()
            if v is not None
        }
        return StationQuery.from_dict(self._get_json("/stations", params or None))

    def get_station(self, station_id: int) -> StationQuery:
        """Fetch a single station by its Bahnhofsnummer (station ID).

        Args:
            station_id: DB station number (Bahnhofsnummer).

        Returns:
            StationQuery whose result list contains at most one station.
        """
        return StationQuery.from_dict(self._get_json(f"/stations/{station_id}"))

    def get_szentralen(
        self, *, offset: int | None = None, limit: int | None = None
    ) -> SZentraleQuery:
        """Fetch all 3-S-Zentralen with optional pagination.

        Args:
            offset: Pagination offset.
            limit: Maximum results to return.

        Returns:
            SZentraleQuery with all matching 3-S-Zentralen.
        """
        params = {
            k: v for k, v in {"offset": offset, "limit": limit}.items() if v is not None
        }
        return SZentraleQuery.from_dict(self._get_json("/szentralen", params or None))

    def get_szentrale(self, szentrale_id: int) -> SZentraleQuery:
        """Fetch a single 3-S-Zentrale by its ID.

        Args:
            szentrale_id: Unique identifier of the 3-S-Zentrale.

        Returns:
            SZentraleQuery whose result list contains at most one entry.
        """
        return SZentraleQuery.from_dict(self._get_json(f"/szentralen/{szentrale_id}"))

    def _get(self, path: str, params: dict | None = None) -> requests.Response:
        url = BASE_URL + path
        try:
            response = self._session.get(url, params=params, timeout=self._timeout)
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

    def _get_json(self, path: str, params: dict | None = None) -> dict:
        response = self._get(path, params)
        try:
            return response.json()
        except Exception as exc:
            raise DBApiError(f"Failed to parse JSON response: {exc}") from exc