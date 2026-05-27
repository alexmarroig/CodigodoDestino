from __future__ import annotations

from datetime import date, datetime

PORTUGUESE_MONTHS = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}


def parse_iso_date(value: str | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(str(value)).date()


def format_date_pt(value: str | date | None) -> str:
    parsed = parse_iso_date(value)
    if parsed is None:
        return "data em formação"
    return f"{parsed.day} de {PORTUGUESE_MONTHS[parsed.month]} de {parsed.year}"


def format_month_year_pt(value: str | date | None) -> str:
    parsed = parse_iso_date(value)
    if parsed is None:
        return "período em formação"
    return f"{PORTUGUESE_MONTHS[parsed.month]} de {parsed.year}"


def format_month_range_pt(start: str | date | None, end: str | date | None) -> str:
    start_date = parse_iso_date(start)
    end_date = parse_iso_date(end)
    if start_date is None or end_date is None:
        return "período em formação"
    if start_date.year == end_date.year and start_date.month == end_date.month:
        return format_month_year_pt(start_date)
    if start_date.year == end_date.year:
        return (
            f"{PORTUGUESE_MONTHS[start_date.month]} a "
            f"{PORTUGUESE_MONTHS[end_date.month]} de {start_date.year}"
        )
    return (
        f"{PORTUGUESE_MONTHS[start_date.month]} de {start_date.year} a "
        f"{PORTUGUESE_MONTHS[end_date.month]} de {end_date.year}"
    )


def format_time_window_label(
    window: dict[str, object] | None,
    *,
    reference_date: date | None = None,
) -> str:
    if not window:
        return "período ainda em formação"

    start = parse_iso_date(window.get("start"))
    end = parse_iso_date(window.get("end"))
    peak = parse_iso_date(window.get("peak"))

    if start is None and end is None and peak is None:
        label = window.get("label")
        return str(label) if label else "período ainda em formação"

    if peak and reference_date is not None:
        days_to_peak = (peak - reference_date).days
        if 0 <= days_to_peak <= 14:
            return f"entre {format_date_pt(start or peak)} e {format_date_pt(end or peak)}, pico em {format_date_pt(peak)} (nos próximos {days_to_peak} dias)"
        if 15 <= days_to_peak <= 45:
            return f"entre {format_date_pt(start or peak)} e {format_date_pt(end or peak)}, pico em {format_date_pt(peak)} (aproximadamente em {days_to_peak} dias)"

    if start and end:
        if start == end:
            return f"em {format_date_pt(start)}"
        if start.year == end.year and start.month == end.month:
            base = f"entre {start.day} e {end.day} de {PORTUGUESE_MONTHS[start.month]} de {start.year}"
            if peak:
                return f"{base}, pico em {format_date_pt(peak)}"
            return base
        base = f"entre {format_date_pt(start)} e {format_date_pt(end)}"
        if peak:
            return f"{base}, pico em {format_date_pt(peak)}"
        return base

    if peak:
        return f"pico em {format_date_pt(peak)}"
    if start:
        return f"a partir de {format_date_pt(start)}"
    return "nos próximos meses"


def format_assertive_when_label(
    window: dict[str, object] | None,
    *,
    reference_date: date | None = None,
) -> str:
    """
    Always produces a readable, assertive label with month spelled out in full.

    Examples:
      - "janeiro de 2026, pico em 15 de janeiro"
      - "março a abril de 2026"
      - "pico em 5 de setembro de 2026"
    """
    if not window:
        return "período ainda em formação"

    start = parse_iso_date(window.get("start"))
    end = parse_iso_date(window.get("end"))
    peak = parse_iso_date(window.get("peak"))

    if peak is None and start is None and end is None:
        label = window.get("label")
        return str(label) if label else "período ainda em formação"

    peak_clause = f", pico em {peak.day} de {PORTUGUESE_MONTHS[peak.month]}" if peak else ""

    if start and end:
        if start.year == end.year and start.month == end.month:
            return f"{PORTUGUESE_MONTHS[start.month]} de {start.year}{peak_clause}"
        if start.year == end.year:
            return (
                f"{PORTUGUESE_MONTHS[start.month]} a "
                f"{PORTUGUESE_MONTHS[end.month]} de {start.year}{peak_clause}"
            )
        return (
            f"{PORTUGUESE_MONTHS[start.month]} de {start.year} a "
            f"{PORTUGUESE_MONTHS[end.month]} de {end.year}{peak_clause}"
        )

    if peak:
        return f"{peak.day} de {PORTUGUESE_MONTHS[peak.month]} de {peak.year}"
    if start:
        return f"a partir de {PORTUGUESE_MONTHS[start.month]} de {start.year}"
    return "período ainda em formação"
