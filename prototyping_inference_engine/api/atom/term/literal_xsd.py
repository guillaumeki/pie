"""
XSD literal parsing and unparsing helpers.

Provides default parsing/unparsing rules for common XSD datatypes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal
import base64
import re
from typing import Callable, Optional, Iterable, cast


XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema#"
RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XSD_PREFIX = "xsd:"
RDF_PREFIX = "rdf:"

XSD_STRING = "string"
XSD_BOOLEAN = "boolean"
XSD_DECIMAL = "decimal"
XSD_DOUBLE = "double"
XSD_FLOAT = "float"
XSD_INTEGER = "integer"
RDF_LANG_STRING = "langString"

INTEGER_TYPES = {
    "integer",
    "nonPositiveInteger",
    "negativeInteger",
    "long",
    "int",
    "short",
    "byte",
    "nonNegativeInteger",
    "unsignedLong",
    "unsignedInt",
    "unsignedShort",
    "unsignedByte",
    "positiveInteger",
}

FLOAT_TYPES = {
    XSD_DECIMAL,
    XSD_FLOAT,
    XSD_DOUBLE,
}

DURATION_TYPES = {
    "duration",
    "yearMonthDuration",
    "dayTimeDuration",
}

DATETIME_TYPES = {
    "dateTime",
    "time",
    "date",
    "gYearMonth",
    "gYear",
    "gMonthDay",
    "gDay",
    "gMonth",
    "dateTimeStamp",
}

MULTIVALUE_STRING_TYPES = {
    "NMTOKENS",
    "IDREFS",
    "ENTITIES",
}

QNAME_TYPES = {
    "QName",
    "NOTATION",
}


@dataclass(frozen=True)
class XsdDuration:
    sign: int
    years: int
    months: int
    days: int
    hours: int
    minutes: int
    seconds: Decimal

    def to_lexical(self) -> str:
        sign = "-" if self.sign < 0 else ""
        parts = []
        if self.years:
            parts.append(f"{self.years}Y")
        if self.months:
            parts.append(f"{self.months}M")
        if self.days:
            parts.append(f"{self.days}D")
        time_parts = []
        if self.hours:
            time_parts.append(f"{self.hours}H")
        if self.minutes:
            time_parts.append(f"{self.minutes}M")
        if self.seconds:
            seconds_str = _decimal_to_lexical(self.seconds)
            time_parts.append(f"{seconds_str}S")
        if time_parts:
            parts.append("T" + "".join(time_parts))
        if not parts:
            parts.append("T0S")
        return f"{sign}P{''.join(parts)}"

    def __str__(self) -> str:
        return self.to_lexical()


@dataclass(frozen=True)
class XsdGYear:
    year: int
    tz: Optional[str]

    def to_lexical(self) -> str:
        return f"{self.year:04d}{self.tz or ''}"


@dataclass(frozen=True)
class XsdGYearMonth:
    year: int
    month: int
    tz: Optional[str]

    def to_lexical(self) -> str:
        return f"{self.year:04d}-{self.month:02d}{self.tz or ''}"


@dataclass(frozen=True)
class XsdGMonthDay:
    month: int
    day: int
    tz: Optional[str]

    def to_lexical(self) -> str:
        return f"--{self.month:02d}-{self.day:02d}{self.tz or ''}"


@dataclass(frozen=True)
class XsdGDay:
    day: int
    tz: Optional[str]

    def to_lexical(self) -> str:
        return f"---{self.day:02d}{self.tz or ''}"


@dataclass(frozen=True)
class XsdGMonth:
    month: int
    tz: Optional[str]

    def to_lexical(self) -> str:
        return f"--{self.month:02d}{self.tz or ''}"


def datatype_local_name(datatype: str) -> str:
    if datatype.startswith(XSD_NAMESPACE):
        return datatype[len(XSD_NAMESPACE) :]
    if datatype.startswith(XSD_PREFIX):
        return datatype[len(XSD_PREFIX) :]
    if datatype.startswith(RDF_NAMESPACE):
        return datatype[len(RDF_NAMESPACE) :]
    if datatype.startswith(RDF_PREFIX):
        return datatype[len(RDF_PREFIX) :]
    return datatype


def is_xsd_datatype(datatype: str) -> bool:
    return datatype.startswith(XSD_NAMESPACE) or datatype.startswith(XSD_PREFIX)


def is_rdf_datatype(datatype: str) -> bool:
    return datatype.startswith(RDF_NAMESPACE) or datatype.startswith(RDF_PREFIX)


def normalize_timezone_suffix(value: str) -> str:
    if value.endswith("Z"):
        return value[:-1] + "+00:00"
    return value


_DURATION_RE = re.compile(
    r"^(-)?P"
    r"(?:(\d+)Y)?"
    r"(?:(\d+)M)?"
    r"(?:(\d+)D)?"
    r"(?:T"
    r"(?:(\d+)H)?"
    r"(?:(\d+)M)?"
    r"(?:(\d+(?:\.\d+)?)S)?"
    r")?$"
)

_GYEAR_RE = re.compile(r"^(-?\d{4,})(Z|[+-]\d{2}:\d{2})?$")
_GYEARMONTH_RE = re.compile(r"^(-?\d{4,})-(\d{2})(Z|[+-]\d{2}:\d{2})?$")
_GMONTHDAY_RE = re.compile(r"^--(\d{2})-(\d{2})(Z|[+-]\d{2}:\d{2})?$")
_GDAY_RE = re.compile(r"^---(\d{2})(Z|[+-]\d{2}:\d{2})?$")
_GMONTH_RE = re.compile(r"^--(\d{2})(Z|[+-]\d{2}:\d{2})?$")


def parse_duration(lexical: str) -> XsdDuration:
    match = _DURATION_RE.match(lexical)
    if not match:
        raise ValueError(f"Invalid duration literal: {lexical}")
    sign = -1 if match.group(1) else 1
    years = int(match.group(2) or 0)
    months = int(match.group(3) or 0)
    days = int(match.group(4) or 0)
    hours = int(match.group(5) or 0)
    minutes = int(match.group(6) or 0)
    seconds = Decimal(match.group(7) or "0")
    return XsdDuration(sign, years, months, days, hours, minutes, seconds)


def parse_datetime(lexical: str) -> datetime:
    normalized = normalize_timezone_suffix(lexical)
    return datetime.fromisoformat(normalized)


def parse_date(lexical: str) -> date:
    normalized = normalize_timezone_suffix(lexical)
    return date.fromisoformat(normalized)


def parse_time(lexical: str) -> time:
    normalized = normalize_timezone_suffix(lexical)
    return time.fromisoformat(normalized)


def parse_g_year(lexical: str) -> XsdGYear:
    match = _GYEAR_RE.match(lexical)
    if not match:
        raise ValueError(f"Invalid gYear literal: {lexical}")
    return XsdGYear(int(match.group(1)), match.group(2))


def parse_g_year_month(lexical: str) -> XsdGYearMonth:
    match = _GYEARMONTH_RE.match(lexical)
    if not match:
        raise ValueError(f"Invalid gYearMonth literal: {lexical}")
    return XsdGYearMonth(int(match.group(1)), int(match.group(2)), match.group(3))


def parse_g_month_day(lexical: str) -> XsdGMonthDay:
    match = _GMONTHDAY_RE.match(lexical)
    if not match:
        raise ValueError(f"Invalid gMonthDay literal: {lexical}")
    return XsdGMonthDay(int(match.group(1)), int(match.group(2)), match.group(3))


def parse_g_day(lexical: str) -> XsdGDay:
    match = _GDAY_RE.match(lexical)
    if not match:
        raise ValueError(f"Invalid gDay literal: {lexical}")
    return XsdGDay(int(match.group(1)), match.group(2))


def parse_g_month(lexical: str) -> XsdGMonth:
    match = _GMONTH_RE.match(lexical)
    if not match:
        raise ValueError(f"Invalid gMonth literal: {lexical}")
    return XsdGMonth(int(match.group(1)), match.group(2))


def parse_boolean(lexical: str) -> bool:
    lowered = lexical.strip().lower()
    if lowered in {"true", "1"}:
        return True
    if lowered in {"false", "0"}:
        return False
    raise ValueError(f"Invalid boolean literal: {lexical}")


def parse_integer(lexical: str) -> int:
    return int(lexical.strip())


def parse_decimal(lexical: str, numeric_mode: str) -> object:
    if numeric_mode == "decimal":
        return Decimal(lexical.strip())
    return float(lexical.strip())


def parse_float(lexical: str, numeric_mode: str) -> object:
    if numeric_mode == "decimal":
        return Decimal(lexical.strip())
    return float(lexical.strip())


def parse_binary(lexical: str, is_hex: bool) -> bytes:
    cleaned = lexical.strip()
    if is_hex:
        return bytes.fromhex(cleaned)
    return base64.b64decode(cleaned.encode("ascii"))


def parse_qname(lexical: str) -> tuple[Optional[str], str]:
    if ":" in lexical:
        prefix, local = lexical.split(":", 1)
        return prefix, local
    return None, lexical


def _decimal_to_lexical(value: Decimal) -> str:
    if value == value.to_integral():
        return str(value.quantize(Decimal(1)))
    return format(value.normalize(), "f").rstrip("0").rstrip(".") or "0"


def unparse_boolean(value: bool) -> str:
    return "true" if value else "false"


def unparse_integer(value: int) -> str:
    return str(value)


def unparse_decimal(value: object) -> str:
    if isinstance(value, Decimal):
        return _decimal_to_lexical(value)
    if isinstance(value, float):
        return format(value, ".15g")
    return str(value)


def unparse_float(value: object) -> str:
    if isinstance(value, Decimal):
        return _decimal_to_lexical(value)
    if isinstance(value, float):
        return format(value, ".15g")
    return str(value)


def unparse_duration(value: XsdDuration) -> str:
    return value.to_lexical()


def unparse_datetime(value: datetime) -> str:
    if value.tzinfo is timezone.utc:
        return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return value.isoformat()


def unparse_date(value: date) -> str:
    return value.isoformat()


def unparse_time(value: time) -> str:
    return value.isoformat()


def unparse_g_year(value: XsdGYear) -> str:
    return value.to_lexical()


def unparse_g_year_month(value: XsdGYearMonth) -> str:
    return value.to_lexical()


def unparse_g_month_day(value: XsdGMonthDay) -> str:
    return value.to_lexical()


def unparse_g_day(value: XsdGDay) -> str:
    return value.to_lexical()


def unparse_g_month(value: XsdGMonth) -> str:
    return value.to_lexical()


def unparse_binary(value: bytes, is_hex: bool) -> str:
    if is_hex:
        return value.hex()
    return base64.b64encode(value).decode("ascii")


def unparse_qname(value: tuple[Optional[str], str]) -> str:
    prefix, local = value
    return f"{prefix}:{local}" if prefix else local


def default_type_parsers(numeric_mode: str) -> dict[str, Callable[[str], object]]:
    return {
        XSD_BOOLEAN: parse_boolean,
        XSD_STRING: lambda s: s,
        RDF_LANG_STRING: lambda s: s,
        "byte": parse_integer,
        "short": parse_integer,
        "int": parse_integer,
        "long": parse_integer,
        "integer": parse_integer,
        "nonPositiveInteger": parse_integer,
        "negativeInteger": parse_integer,
        "nonNegativeInteger": parse_integer,
        "unsignedLong": parse_integer,
        "unsignedInt": parse_integer,
        "unsignedShort": parse_integer,
        "unsignedByte": parse_integer,
        "positiveInteger": parse_integer,
        XSD_DECIMAL: lambda s: parse_decimal(s, numeric_mode),
        XSD_FLOAT: lambda s: parse_float(s, numeric_mode),
        XSD_DOUBLE: lambda s: parse_float(s, numeric_mode),
        "duration": parse_duration,
        "yearMonthDuration": parse_duration,
        "dayTimeDuration": parse_duration,
        "dateTime": parse_datetime,
        "time": parse_time,
        "date": parse_date,
        "gYearMonth": parse_g_year_month,
        "gYear": parse_g_year,
        "gMonthDay": parse_g_month_day,
        "gDay": parse_g_day,
        "gMonth": parse_g_month,
        "dateTimeStamp": parse_datetime,
        "hexBinary": lambda s: parse_binary(s, True),
        "base64Binary": lambda s: parse_binary(s, False),
        "anyURI": lambda s: s,
        "QName": parse_qname,
        "NOTATION": parse_qname,
        "NMTOKENS": lambda s: tuple(s.split()),
        "IDREFS": lambda s: tuple(s.split()),
        "ENTITIES": lambda s: tuple(s.split()),
    }


def default_type_unparsers(numeric_mode: str) -> dict[str, Callable[[object], str]]:
    return cast(
        dict[str, Callable[[object], str]],
        {
            XSD_BOOLEAN: unparse_boolean,
            XSD_STRING: lambda v: str(v),
            RDF_LANG_STRING: lambda v: str(v),
            "byte": unparse_integer,
            "short": unparse_integer,
            "int": unparse_integer,
            "long": unparse_integer,
            "integer": unparse_integer,
            "nonPositiveInteger": unparse_integer,
            "negativeInteger": unparse_integer,
            "nonNegativeInteger": unparse_integer,
            "unsignedLong": unparse_integer,
            "unsignedInt": unparse_integer,
            "unsignedShort": unparse_integer,
            "unsignedByte": unparse_integer,
            "positiveInteger": unparse_integer,
            XSD_DECIMAL: unparse_decimal,
            XSD_FLOAT: unparse_float,
            XSD_DOUBLE: unparse_float,
            "duration": unparse_duration,
            "yearMonthDuration": unparse_duration,
            "dayTimeDuration": unparse_duration,
            "dateTime": unparse_datetime,
            "time": unparse_time,
            "date": unparse_date,
            "gYearMonth": unparse_g_year_month,
            "gYear": unparse_g_year,
            "gMonthDay": unparse_g_month_day,
            "gDay": unparse_g_day,
            "gMonth": unparse_g_month,
            "dateTimeStamp": unparse_datetime,
            "hexBinary": lambda v: unparse_binary(cast(bytes, v), True),
            "base64Binary": lambda v: unparse_binary(cast(bytes, v), False),
            "anyURI": lambda v: str(v),
            "QName": unparse_qname,
            "NOTATION": unparse_qname,
            "NMTOKENS": lambda v: " ".join(cast(Iterable[str], v)),
            "IDREFS": lambda v: " ".join(cast(Iterable[str], v)),
            "ENTITIES": lambda v: " ".join(cast(Iterable[str], v)),
        },
    )
