from importlib.metadata import version

__version__ = version("deutsche-bahn")

from . import stada, timetables
from .exceptions import AuthenticationError, DBApiError, NotFoundError, RateLimitError

__all__ = [
    "__version__",
    "timetables",
    "stada",
    "DBApiError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
]
