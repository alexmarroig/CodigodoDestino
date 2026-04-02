from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class UtcConversion:
    input_local: dict[str, str]
    utc_datetime: str
    offset_applied: str
    is_dst: bool


def local_to_utc(date_str: str, time_str: str, tz_name: str) -> datetime:
    local_naive = datetime.fromisoformat(f"{date_str}T{time_str}")
    local_dt = local_naive.replace(tzinfo=ZoneInfo(tz_name))
    return local_dt.astimezone(timezone.utc)


def utc_isoformat_z(dt_utc: datetime) -> str:
    return dt_utc.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def convert_with_metadata(date_str: str, time_str: str, tz_name: str) -> UtcConversion:
    local_naive = datetime.fromisoformat(f"{date_str}T{time_str}")
    local_dt = local_naive.replace(tzinfo=ZoneInfo(tz_name))
    utc_dt = local_dt.astimezone(timezone.utc)
    offset = local_dt.utcoffset()
    return UtcConversion(
        input_local={"date": date_str, "time": time_str, "timezone": tz_name},
        utc_datetime=utc_isoformat_z(utc_dt),
        offset_applied=(str(offset) if offset is not None else "+00:00"),
        is_dst=bool(local_dt.dst() and local_dt.dst().total_seconds() != 0),
    )
