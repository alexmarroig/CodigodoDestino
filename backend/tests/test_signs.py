from astro.signs import longitude_to_sign


def test_sign_conversion() -> None:
    result = longitude_to_sign(130)
    assert result.sign == "Leão"
    assert int(result.degree_in_sign) == 10
