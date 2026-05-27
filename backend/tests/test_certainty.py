from engine.certainty import certainty_with_aspects


def test_certainty_will_with_tense_aspect():
    signals = [{"evidence": {"aspect": "square"}} for _ in range(4)]
    assert certainty_with_aspects(4, signals) == "will"


def test_certainty_must_without_tense_aspect():
    signals = [{"evidence": {"aspect": "trine"}} for _ in range(4)]
    assert certainty_with_aspects(4, signals) == "must"


def test_certainty_must_three_signals_tense():
    signals = [{"evidence": {"aspect": "opposition"}} for _ in range(3)]
    assert certainty_with_aspects(3, signals) == "must"


def test_certainty_tendency_two_signals():
    signals = [{"evidence": {"aspect": "square"}} for _ in range(2)]
    assert certainty_with_aspects(2, signals) == "tendency"


def test_certainty_chance_one_signal():
    signals = [{"evidence": {"aspect": "square"}}]
    assert certainty_with_aspects(1, signals) == "chance"


def test_certainty_numerology_only_caps_at_must():
    signals = [{"technique": "numerology", "evidence": {}} for _ in range(5)]
    assert certainty_with_aspects(5, signals) == "must"
