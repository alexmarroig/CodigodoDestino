from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class UtcConversion:
    input_local: dict[str, str]
    utc_datetime: str
    offset_applied: str
    is_dst: bool


def _parse_local_datetime(date_str: str, time_str: str) -> datetime:
    return datetime.fromisoformat(f"{date_str}T{time_str}")


def _format_offset(offset: timedelta | None) -> str:
    if offset is None:
        return "+00:00"

    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    absolute_minutes = abs(total_minutes)
    hours, minutes = divmod(absolute_minutes, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def local_to_utc(date_str: str, time_str: str, tz_name: str) -> datetime:
    local_naive = _parse_local_datetime(date_str, time_str)
    local_dt = local_naive.replace(tzinfo=ZoneInfo(tz_name))
    return local_dt.astimezone(timezone.utc)


def utc_isoformat_z(dt_utc: datetime) -> str:
    return dt_utc.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def convert_with_metadata(date_str: str, time_str: str, tz_name: str) -> UtcConversion:
    local_naive = _parse_local_datetime(date_str, time_str)
    local_dt = local_naive.replace(tzinfo=ZoneInfo(tz_name))
    utc_dt = local_dt.astimezone(timezone.utc)

    return UtcConversion(
        input_local={"date": date_str, "time": time_str, "timezone": tz_name},
        utc_datetime=utc_isoformat_z(utc_dt),
        offset_applied=_format_offset(local_dt.utcoffset()),
        is_dst=bool(local_dt.dst() and local_dt.dst().total_seconds() != 0),
    )
