from datetime import date

from numerologia.core import life_path_number, personal_year


def test_life_path_number_is_deterministic() -> None:
    assert life_path_number("1995-03-10") == 1


def test_personal_year_structure() -> None:
    result = personal_year("1995-03-10", date(2026, 4, 2))
    assert result == {"reference_year": 2026, "value": 5, "is_master": False}
