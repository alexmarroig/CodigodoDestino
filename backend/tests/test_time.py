from astro.time import local_to_utc, utc_isoformat_z


def test_local_to_utc() -> None:
    dt = local_to_utc("1990-08-15", "14:30:00", "America/Sao_Paulo")
    assert utc_isoformat_z(dt).endswith("Z")
