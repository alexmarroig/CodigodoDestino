from datetime import date

from engine.date_formatting import format_date_pt, format_month_year_pt, format_time_window_label


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
    assert "entre" in label
