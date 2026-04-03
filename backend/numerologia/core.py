from __future__ import annotations

from datetime import date, datetime

MASTER_NUMBERS = {11, 22, 33}
DateLike = date | str


def _coerce_date(value: DateLike) -> date:
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(value).date()
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date: {value}") from exc


def _reduce_number(value: int) -> int:
    while value > 9 and value not in MASTER_NUMBERS:
        value = sum(int(char) for char in str(value))
    return value


def life_path_number(birth_date: DateLike) -> int:
    parsed_birth_date = _coerce_date(birth_date)
    digits = parsed_birth_date.strftime("%Y%m%d")
    return _reduce_number(sum(int(char) for char in digits))


def personal_year(birth_date: DateLike, reference_date: DateLike) -> dict[str, int | bool]:
    parsed_birth_date = _coerce_date(birth_date)
    parsed_reference_date = _coerce_date(reference_date)

    digits = f"{parsed_birth_date.day:02d}{parsed_birth_date.month:02d}{parsed_reference_date.year}"
    value = _reduce_number(sum(int(char) for char in digits))

    return {
        "reference_year": parsed_reference_date.year,
        "value": value,
        "is_master": value in MASTER_NUMBERS,
    }
