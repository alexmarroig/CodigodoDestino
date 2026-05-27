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


def _long_window_broad_label(start: date, end: date) -> str:
    return (
        f"tema sensível de {PORTUGUESE_MONTHS[start.month]} de {start.year} "
        f"a {PORTUGUESE_MONTHS[end.month]} de {end.year}"
    )


def _should_suppress_peak_for_long_window(
    start: date | None,
    end: date | None,
    peak: date | None,
    reference_date: date | None,
) -> bool:
    if not (peak and reference_date and start and end):
        return False
    duration_days = (end - start).days
    if duration_days <= 180:
        return False
    return abs((peak - reference_date).days) <= 7


def _format_range_clause(
    start: date | None,
    end: date | None,
    *,
    fallback: date | None = None,
) -> str:
    anchor = fallback or start or end
    if start and end:
        if start == end:
            return f"em {format_date_pt(start)}"
        if start.year == end.year and start.month == end.month:
            return (
                f"de {start.day} a {end.day} de "
                f"{PORTUGUESE_MONTHS[start.month]} de {start.year}"
            )
        return f"de {format_date_pt(start)} a {format_date_pt(end)}"
    if anchor:
        return f"em {format_date_pt(anchor)}"
    return ""


def _peak_relative_clause(
    peak: date,
    reference_date: date,
    *,
    range_clause: str,
) -> str:
    days_to_peak = (peak - reference_date).days
    peak_date = format_date_pt(peak)
    prefix = f"{range_clause} — " if range_clause else ""

    if days_to_peak == 0:
        return f"{prefix}intensidade máxima hoje ({peak_date})"
    if 1 <= days_to_peak <= 7:
        return f"{prefix}pico em {peak_date} (nesta semana)"
    if 8 <= days_to_peak <= 45:
        return f"{prefix}pico em {peak_date}"
    if days_to_peak < 0:
        return f"{prefix}pico em {peak_date}"
    return f"{prefix}pico em {peak_date}"


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

    if start and end and (end - start).days > 180:
        return _long_window_broad_label(start, end)

    if _should_suppress_peak_for_long_window(start, end, peak, reference_date):
        peak = None

    if peak and reference_date is not None:
        range_clause = _format_range_clause(start, end, fallback=peak)
        relative = _peak_relative_clause(peak, reference_date, range_clause=range_clause)
        if relative:
            return relative

    if start and end:
        if start == end:
            if peak and peak != start:
                return f"em {format_date_pt(start)}, pico em {format_date_pt(peak)}"
            return f"em {format_date_pt(start)}"

        base = _format_range_clause(start, end)
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
    Compact when-label for human summaries (month names spelled out).

    Examples:
      - "janeiro de 2026, pico em 15 de janeiro"
      - "março a abril de 2026"
      - "5 de setembro de 2026"
    """
    if not window:
        return "período ainda em formação"

    start = parse_iso_date(window.get("start"))
    end = parse_iso_date(window.get("end"))
    peak = parse_iso_date(window.get("peak"))

    if peak is None and start is None and end is None:
        label = window.get("label")
        return str(label) if label else "período ainda em formação"

    if _should_suppress_peak_for_long_window(start, end, peak, reference_date):
        peak = None

    peak_clause = ""
    if peak:
        if start and end and start.year == end.year and start.month == end.month:
            peak_clause = f", pico em {peak.day} de {PORTUGUESE_MONTHS[peak.month]}"
        else:
            peak_clause = f", pico em {format_date_pt(peak)}"

    if start and end:
        if (end - start).days > 180:
            return _long_window_broad_label(start, end)
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
        return format_date_pt(peak)
    if start:
        return f"a partir de {PORTUGUESE_MONTHS[start.month]} de {start.year}"
    return "período ainda em formação"
