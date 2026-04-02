from __future__ import annotations

from datetime import date, datetime
from typing import Dict


# -----------------------------------
# UTILS
# -----------------------------------

def _reduce_number(value: int) -> int:
    """
    Reduz número até um dígito (numerologia clássica).
    """
    while value > 9:
        value = sum(int(char) for char in str(value))
    return value


def _parse_date(date_str: str) -> date:
    try:
        return datetime.fromisoformat(date_str).date()
    except Exception as exc:
        raise ValueError(f"Data inválida: {date_str}") from exc


# -----------------------------------
# CORE
# -----------------------------------

def life_path_number(birth_date: str) -> int:
    """
    Número de vida (Life Path).
    """
    dt = _parse_date(birth_date)

    total = sum(int(c) for c in dt.strftime("%Y%m%d"))
    return _reduce_number(total)


def personal_year(
    birth_date: str,
    reference_date: date,
) -> Dict[str, int]:
    """
    Ano pessoal (determinístico).
    """
    dt = _parse_date(birth_date)

    total = sum(
        int(c)
        for c in f"{dt.day:02d}{dt.month:02d}{reference_date.year}"
    )

    return {
        "reference_year": reference_date.year,
        "value": _reduce_number(total),
    }