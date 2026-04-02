from __future__ import annotations

from datetime import date, datetime


def _reduce_number(value: int) -> int:
    while value > 9:
        value = sum(int(char) for char in str(value))
    return value


def life_path_number(birth_date: str) -> int:
    dt = datetime.fromisoformat(birth_date).date()
    return _reduce_number(sum(int(c) for c in dt.strftime("%Y%m%d")))


def personal_year(birth_date: str, reference_date: str) -> dict[str, int]:
    dt = datetime.fromisoformat(birth_date).date()
    ref = date.fromisoformat(reference_date)
    total = sum(int(c) for c in f"{dt.day:02d}{dt.month:02d}{ref.year}")
    return {"reference_year": ref.year, "value": _reduce_number(total)}
