from importlib.metadata import version

__version__ = version("db-timetables")

from .client import TimetablesClient
from .exceptions import (
    AuthenticationError,
    DBApiError,
    NotFoundError,
    RateLimitError,
)
from .models import (
    ArrivalDeparture,
    Connection,
    ConnectionStatus,
    DelaySource,
    DistributorMessage,
    DistributorType,
    EventStatus,
    HistoricDelay,
    HistoricPlatformChange,
    Message,
    MessageType,
    Station,
    Timetable,
    TimetableStop,
    TrainLine,
)

__all__ = [
    "__version__",
    "TimetablesClient",
    "Station",
    "Timetable",
    "TimetableStop",
    "TrainLine",
    "ArrivalDeparture",
    "Message",
    "DistributorMessage",
    "Connection",
    "HistoricDelay",
    "HistoricPlatformChange",
    "MessageType",
    "EventStatus",
    "ConnectionStatus",
    "DistributorType",
    "DelaySource",
    "DBApiError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
]
