from datetime import date

from engine.date_formatting import (
    format_assertive_when_label,
    format_date_pt,
    format_month_year_pt,
    format_time_window_label,
)


def test_format_date_pt() -> None:
    assert format_date_pt("2026-07-02") == "2 de julho de 2026"


def test_format_month_year_pt() -> None:
    assert format_month_year_pt(date(2026, 5, 1)) == "maio de 2026"


def test_format_time_window_label_with_peak() -> None:
    label = format_time_window_label(
        {
            "start": "2026-04-12",
            "end": "2026-04-28",
            "peak": "2026-04-18",
        },
        reference_date=date(2026, 4, 4),
    )
    assert "18 de abril de 2026" in label
    assert "de " in label
    assert " a " in label


def test_assertive_label_with_peak():
    window = {"start": "2026-01-10", "end": "2026-02-05", "peak": "2026-01-15"}
    result = format_assertive_when_label(window)
    assert "janeiro" in result
    assert "15 de janeiro" in result


def test_assertive_label_no_peak():
    window = {"start": "2026-03-01", "end": "2026-04-30"}
    result = format_assertive_when_label(window)
    assert "março" in result
    assert "abril" in result


def test_assertive_label_single_month():
    window = {"start": "2026-06-10", "end": "2026-06-28", "peak": "2026-06-20"}
    result = format_assertive_when_label(window)
    assert "junho de 2026" in result
    assert "20 de junho" in result


def test_assertive_label_none_window():
    result = format_assertive_when_label(None)
    assert result == "período ainda em formação"


def test_assertive_label_peak_only():
    window = {"peak": "2026-09-05"}
    result = format_assertive_when_label(window)
    assert "5 de setembro de 2026" in result


def test_format_time_window_label_peak_today_says_hoje() -> None:
    """Bug fix: days_to_peak == 0 must NOT produce 'nos próximos 0 dias'."""
    today = date(2026, 5, 27)
    label = format_time_window_label(
        {"start": "2026-05-25", "end": "2026-05-30", "peak": "2026-05-27"},
        reference_date=today,
    )
    assert "0 dias" not in label, f"Got: {label}"
    assert "hoje" in label.lower(), f"Expected 'hoje' in: {label}"
    assert "27 de maio de 2026" in label


def test_format_time_window_label_peak_this_week_says_nesta_semana() -> None:
    label = format_time_window_label(
        {"start": "2026-05-25", "end": "2026-06-01", "peak": "2026-05-29"},
        reference_date=date(2026, 5, 27),
    )
    assert "nesta semana" in label.lower(), f"Got: {label}"
    assert "pico em 29 de maio" in label


def test_long_window_suppresses_misleading_peak_today() -> None:
    label = format_time_window_label(
        {
            "start": "2026-05-27",
            "end": "2028-05-17",
            "peak": "2026-05-27",
        },
        reference_date=date(2026, 5, 27),
    )
    assert "pico hoje" not in label.lower(), f"Got: {label}"
    assert "intensidade máxima hoje" not in label.lower(), f"Got: {label}"
    assert "tema sensível" in label.lower()


def test_format_time_window_label_peak_in_14_days() -> None:
    label = format_time_window_label(
        {"start": "2026-05-27", "end": "2026-06-15", "peak": "2026-06-10"},
        reference_date=date(2026, 5, 27),
    )
    assert "pico em 10 de junho de 2026" in label, f"Got: {label}"
    assert "0 dias" not in label, f"Got: {label}"


def test_format_time_window_label_uses_de_a_range() -> None:
    label = format_time_window_label(
        {"start": "2026-03-10", "end": "2026-04-22"},
        reference_date=date(2026, 3, 1),
    )
    assert label.startswith("de 10 de março de 2026 a 22 de abril de 2026")


def test_assertive_long_window_suppresses_peak_near_reference() -> None:
    label = format_assertive_when_label(
        {
            "start": "2026-05-27",
            "end": "2028-05-17",
            "peak": "2026-05-27",
        },
        reference_date=date(2026, 5, 27),
    )
    assert "pico" not in label.lower()
    assert "maio de 2026" in label
