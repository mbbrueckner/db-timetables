from importlib.metadata import version

__version__ = version("deutsche-bahn-py")

from .client import StaDaClient
from .exceptions import AuthenticationError, DBApiError, NotFoundError, RateLimitError
from .models import (
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

__all__ = [
    "__version__",
    "StaDaClient",
    "StadaStation",
    "StationQuery",
    "SZentrale",
    "SZentraleQuery",
    "Address",
    "GeographicPoint",
    "OpeningHours",
    "DaySchedule",
    "Schedule",
    "DoubleSchedule",
    "EVANumber",
    "RiL100Identifier",
    "Aufgabentraeger",
    "RegionalBereich",
    "StationManagement",
    "TimetableOffice",
    "WirelessLan",
    "MobilityServiceStaff",
    "LocalizedNames",
    "DBApiError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
]
