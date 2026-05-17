from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Address:
    city: str = ""
    house_number: str = ""
    street: str = ""
    zipcode: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Address:
        return cls(
            city=d.get("city", ""),
            house_number=d.get("houseNumber", ""),
            street=d.get("street", ""),
            zipcode=d.get("zipcode", ""),
        )


@dataclass
class GeographicPoint:
    """GeoJSON point (WGS84). coordinates = [longitude, latitude]."""

    type: str = ""
    coordinates: list[float] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> GeographicPoint:
        return cls(type=d.get("type", ""), coordinates=d.get("coordinates", []))


@dataclass
class OpeningHours:
    from_time: str = ""
    to_time: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> OpeningHours:
        return cls(from_time=d.get("fromTime", ""), to_time=d.get("toTime", ""))


def _oh(d: dict, key: str) -> OpeningHours | None:
    v = d.get(key)
    return OpeningHours.from_dict(v) if v else None


@dataclass
class DaySchedule:
    monday: OpeningHours | None = None
    tuesday: OpeningHours | None = None
    wednesday: OpeningHours | None = None
    thursday: OpeningHours | None = None
    friday: OpeningHours | None = None
    saturday: OpeningHours | None = None
    sunday: OpeningHours | None = None
    holiday: OpeningHours | None = None

    @classmethod
    def from_dict(cls, d: dict) -> DaySchedule:
        return cls(
            monday=_oh(d, "monday"),
            tuesday=_oh(d, "tuesday"),
            wednesday=_oh(d, "wednesday"),
            thursday=_oh(d, "thursday"),
            friday=_oh(d, "friday"),
            saturday=_oh(d, "saturday"),
            sunday=_oh(d, "sunday"),
            holiday=_oh(d, "holiday"),
        )


@dataclass
class Schedule:
    availability: DaySchedule | None = None

    @classmethod
    def from_dict(cls, d: dict) -> Schedule:
        avail = d.get("availability")
        return cls(availability=DaySchedule.from_dict(avail) if avail else None)


@dataclass
class DoubleSchedule:
    """Two opening-hours ranges per weekday (used in MobilityServiceStaff)."""

    monday1: OpeningHours | None = None
    monday2: OpeningHours | None = None
    tuesday1: OpeningHours | None = None
    tuesday2: OpeningHours | None = None
    wednesday1: OpeningHours | None = None
    wednesday2: OpeningHours | None = None
    thursday1: OpeningHours | None = None
    thursday2: OpeningHours | None = None
    friday1: OpeningHours | None = None
    friday2: OpeningHours | None = None
    saturday1: OpeningHours | None = None
    saturday2: OpeningHours | None = None
    sunday1: OpeningHours | None = None
    sunday2: OpeningHours | None = None

    @classmethod
    def from_dict(cls, d: dict) -> DoubleSchedule:
        return cls(
            monday1=_oh(d, "monday1"),
            monday2=_oh(d, "monday2"),
            tuesday1=_oh(d, "tuesday1"),
            tuesday2=_oh(d, "tuesday2"),
            wednesday1=_oh(d, "wednesday1"),
            wednesday2=_oh(d, "wednesday2"),
            thursday1=_oh(d, "thursday1"),
            thursday2=_oh(d, "thursday2"),
            friday1=_oh(d, "friday1"),
            friday2=_oh(d, "friday2"),
            saturday1=_oh(d, "saturday1"),
            saturday2=_oh(d, "saturday2"),
            sunday1=_oh(d, "sunday1"),
            sunday2=_oh(d, "sunday2"),
        )


@dataclass
class Aufgabentraeger:
    """Local public-sector entity responsible for short-distance public transport."""

    name: str = ""
    short_name: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> Aufgabentraeger:
        return cls(name=d.get("name", ""), short_name=d.get("shortName", ""))


@dataclass
class EVANumber:
    number: int = 0
    is_main: bool = False
    geographic_coordinates: GeographicPoint | None = None

    @classmethod
    def from_dict(cls, d: dict) -> EVANumber:
        gc = d.get("geographicCoordinates")
        return cls(
            number=d.get("number", 0),
            is_main=d.get("isMain", False),
            geographic_coordinates=GeographicPoint.from_dict(gc) if gc else None,
        )


@dataclass
class RiL100Identifier:
    ril_identifier: str = ""
    is_main: bool = False
    primary_location_code: str = ""
    steam_permission: str = ""
    geographic_coordinates: GeographicPoint | None = None

    @classmethod
    def from_dict(cls, d: dict) -> RiL100Identifier:
        gc = d.get("geographicCoordinates")
        return cls(
            ril_identifier=d.get("rilIdentifier", ""),
            is_main=d.get("isMain", False),
            primary_location_code=d.get("primaryLocationCode", ""),
            steam_permission=d.get("steamPermission", ""),
            geographic_coordinates=GeographicPoint.from_dict(gc) if gc else None,
        )


@dataclass
class RegionalBereich:
    name: str = ""
    number: int = 0
    short_name: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> RegionalBereich:
        return cls(
            name=d.get("name", ""),
            number=d.get("number", 0),
            short_name=d.get("shortName", ""),
        )


@dataclass
class StationManagement:
    name: str = ""
    number: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> StationManagement:
        return cls(name=d.get("name", ""), number=d.get("number", 0))


@dataclass
class TimetableOffice:
    name: str = ""
    email: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> TimetableOffice:
        return cls(name=d.get("name", ""), email=d.get("email", ""))


@dataclass
class WirelessLan:
    amount: int = 0
    install_date: str = ""
    product: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> WirelessLan:
        return cls(
            amount=d.get("amount", 0),
            install_date=d.get("installDate", ""),
            product=d.get("product", ""),
        )


@dataclass
class MobilityServiceStaff:
    meeting_point: str = ""
    service_on_behalf: bool = False
    staff_on_site: bool = False
    availability: DoubleSchedule | None = None

    @classmethod
    def from_dict(cls, d: dict) -> MobilityServiceStaff:
        avail = d.get("availability")
        return cls(
            meeting_point=d.get("meetingPoint", ""),
            service_on_behalf=d.get("serviceOnBehalf", False),
            staff_on_site=d.get("staffOnSite", False),
            availability=DoubleSchedule.from_dict(avail) if avail else None,
        )


@dataclass
class LocalizedNames:
    """Official station secondary names in local minority languages (ISO 639-2)."""

    dan: str = ""  # Danish
    dsb: str = ""  # Lower Sorbian
    frr: str = ""  # North Frisian
    hsb: str = ""  # Upper Sorbian
    nds: str = ""  # Low German

    @classmethod
    def from_dict(cls, d: dict) -> LocalizedNames:
        return cls(
            dan=d.get("dan", ""),
            dsb=d.get("dsb", ""),
            frr=d.get("frr", ""),
            hsb=d.get("hsb", ""),
            nds=d.get("nds", ""),
        )


@dataclass
class SZentrale:
    """3-S-Zentrale: a 24/7 operations centre for german railway stations."""

    number: int = 0
    name: str = ""
    public_phone_number: str = ""
    public_fax_number: str = ""
    internal_phone_number: str = ""
    internal_fax_number: str = ""
    mobile_phone_number: str = ""
    email: str = ""
    address: Address | None = None

    @classmethod
    def from_dict(cls, d: dict) -> SZentrale:
        addr = d.get("address")
        return cls(
            number=d.get("number", 0),
            name=d.get("name", ""),
            public_phone_number=d.get("publicPhoneNumber", ""),
            public_fax_number=d.get("publicFaxNumber", ""),
            internal_phone_number=d.get("internalPhoneNumber", ""),
            internal_fax_number=d.get("internalFaxNumber", ""),
            mobile_phone_number=d.get("mobilePhoneNumber", ""),
            email=d.get("email", ""),
            address=Address.from_dict(addr) if addr else None,
        )


@dataclass
class StadaStation:
    """Master data for a german railway station managed by DB InfraGo AG."""

    number: int = 0
    name: str = ""
    category: int = 0
    price_category: int = 0
    federal_state: str = ""
    federal_state_code: str = ""
    country_code: str = ""
    municipality_code: str = ""
    ifopt: str = ""
    has_wifi: bool = False
    has_db_lounge: bool = False
    has_travel_center: bool = False
    has_locker_system: bool = False
    has_public_facilities: bool = False
    has_local_public_transport: bool = False
    has_taxi_rank: bool = False
    has_parking: bool = False
    has_bicycle_parking: bool = False
    has_car_rental: bool = False
    has_railway_mission: bool = False
    has_lost_and_found: bool = False
    has_travel_necessities: bool = False
    has_stepless_access: str = ""  # "yes", "no", or "partial"
    has_mobility_service: str = ""
    eva_numbers: list[EVANumber] = field(default_factory=list)
    ril100_identifiers: list[RiL100Identifier] = field(default_factory=list)
    mailing_address: Address | None = None
    regional_bereich: RegionalBereich | None = None
    station_management: StationManagement | None = None
    szentrale: SZentrale | None = None
    aufgabentraeger: Aufgabentraeger | None = None
    timetable_office: TimetableOffice | None = None
    wireless_lan: WirelessLan | None = None
    local_service_staff: Schedule | None = None
    db_information: Schedule | None = None
    mobility_service_staff: MobilityServiceStaff | None = None
    localized_names: LocalizedNames | None = None

    @classmethod
    def from_dict(cls, d: dict) -> StadaStation:
        def sched(key: str) -> Schedule | None:
            v = d.get(key)
            return Schedule.from_dict(v) if v else None

        ma = d.get("mailingAddress")
        rb = d.get("regionalbereich")
        sm = d.get("stationManagement")
        sz = d.get("szentrale")
        at = d.get("aufgabentraeger")
        to = d.get("timeTableOffice")
        wl = d.get("wirelessLan")
        ms = d.get("mobilityServiceStaff")
        ln = d.get("localizedNames")

        return cls(
            number=d.get("number", 0),
            name=d.get("name", ""),
            category=d.get("category", 0),
            price_category=d.get("priceCategory", 0),
            federal_state=d.get("federalState", ""),
            federal_state_code=d.get("federalStateCode", ""),
            country_code=d.get("countryCode", ""),
            municipality_code=d.get("municipalityCode", ""),
            ifopt=d.get("ifopt", ""),
            has_wifi=d.get("hasWiFi", False),
            has_db_lounge=d.get("hasDBLounge", False),
            has_travel_center=d.get("hasTravelCenter", False),
            has_locker_system=d.get("hasLockerSystem", False),
            has_public_facilities=d.get("hasPublicFacilities", False),
            has_local_public_transport=d.get("hasLocalPublicTransport", False),
            has_taxi_rank=d.get("hasTaxiRank", False),
            has_parking=d.get("hasParking", False),
            has_bicycle_parking=d.get("hasBicycleParking", False),
            has_car_rental=d.get("hasCarRental", False),
            has_railway_mission=d.get("hasRailwayMission", False),
            has_lost_and_found=d.get("hasLostAndFound", False),
            has_travel_necessities=d.get("hasTravelNecessities", False),
            has_stepless_access=d.get("hasSteplessAccess", ""),
            has_mobility_service=d.get("hasMobilityService", ""),
            eva_numbers=[EVANumber.from_dict(e) for e in d.get("evaNumbers", [])],
            ril100_identifiers=[
                RiL100Identifier.from_dict(r) for r in d.get("ril100Identifiers", [])
            ],
            mailing_address=Address.from_dict(ma) if ma else None,
            regional_bereich=RegionalBereich.from_dict(rb) if rb else None,
            station_management=StationManagement.from_dict(sm) if sm else None,
            szentrale=SZentrale.from_dict(sz) if sz else None,
            aufgabentraeger=Aufgabentraeger.from_dict(at) if at else None,
            timetable_office=TimetableOffice.from_dict(to) if to else None,
            wireless_lan=WirelessLan.from_dict(wl) if wl else None,
            local_service_staff=sched("localServiceStaff"),
            db_information=sched("DBinformation"),
            mobility_service_staff=MobilityServiceStaff.from_dict(ms) if ms else None,
            localized_names=LocalizedNames.from_dict(ln) if ln else None,
        )


@dataclass
class StationQuery:
    total: int = 0
    offset: int = 0
    limit: int = 0
    result: list[StadaStation] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> StationQuery:
        return cls(
            total=d.get("total", 0),
            offset=d.get("offset", 0),
            limit=d.get("limit", 0),
            result=[StadaStation.from_dict(s) for s in d.get("result", [])],
        )


@dataclass
class SZentraleQuery:
    total: int = 0
    offset: int = 0
    limit: int = 0
    result: list[SZentrale] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> SZentraleQuery:
        return cls(
            total=d.get("total", 0),
            offset=d.get("offset", 0),
            limit=d.get("limit", 0),
            result=[SZentrale.from_dict(s) for s in d.get("result", [])],
        )
