from __future__ import annotations


class DBApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(DBApiError):
    pass


class NotFoundError(DBApiError):
    pass


class RateLimitError(DBApiError):
    pass
