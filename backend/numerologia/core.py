from __future__ import annotations

from datetime import date, datetime


def _reduce_number(value: int) -> int:
    while value > 9:
        value = sum(int(char) for char in str(value))
    return value


def life_path_number(birth_date: str) -> int:
    dt = datetime.fromisoformat(birth_date).date()
    total = sum(int(c) for c in dt.strftime("%Y%m%d"))
    return _reduce_number(total)


def personal_year(birth_date: str, reference_year: int | None = None) -> dict[str, int]:
    dt = datetime.fromisoformat(birth_date).date()
    year = reference_year if reference_year is not None else date.today().year
    total = sum(int(c) for c in f"{dt.day:02d}{dt.month:02d}{year}")
    return {"reference_year": year, "value": _reduce_number(total)}
