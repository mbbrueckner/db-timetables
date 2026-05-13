from importlib.metadata import version

__version__ = version("db-timetables")

from .client import TimetablesClient
from .models import (
    Station,
    Timetable,
    TimetableStop,
    TrainLine,
    ArrivalDeparture,
    Message,
    DistributorMessage,
    Connection,
    HistoricDelay,
    HistoricPlatformChange,
    MessageType,
    EventStatus,
    ConnectionStatus,
    DistributorType,
    DelaySource,
)
from .exceptions import (
    DBApiError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
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