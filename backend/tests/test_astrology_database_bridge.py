"""Tests for Astrologydatabase bridge fatalistic filtering."""

from engine.astrology_database_bridge import apply_editorial_overrides, build_section_overrides


def test_build_section_overrides_prefers_shadow_text() -> None:
    enrichment = {
        "rules": [
            {
                "priority": {
                    "rank": 1,
                    "total_score": 11.5,
                    "themes": ["shadow"],
                },
                "rule": {
                    "canonical_code": "SUN__PLANET_IN_SIGN__SCORPIO",
                    "blocks": [
                        {
                            "theme": "shadow",
                            "potency_central": "Identidade intensa.",
                            "poorly_expressed": "Controle, ciúme e autossabotagem tendem a dominar.",
                            "well_expressed": "Profundidade emocional madura.",
                        }
                    ],
                },
            }
        ]
    }

    overrides = build_section_overrides(enrichment)
    assert "core_wound" in overrides
    assert "autossabotagem" in overrides["core_wound"]["body"].lower()
    assert overrides["core_wound"]["certainty_level"] == "will"


def test_apply_editorial_overrides_patches_matching_section() -> None:
    sections = [
        {
            "id": "core_wound",
            "title": "Ferida principal",
            "summary": "Resumo antigo",
            "body": "Corpo antigo",
            "certainty_level": "tendency",
            "certainty_label": "Forte tendência",
            "evidence": [],
        }
    ]
    enrichment = {
        "rules": [
            {
                "priority": {"rank": 1, "total_score": 10.0, "themes": ["shadow"]},
                "rule": {
                    "canonical_code": "MOON__PLANET_IN_HOUSE__12",
                    "blocks": [
                        {
                            "theme": "shadow",
                            "poorly_expressed": "Ferida de abandono reaparece em todo vínculo.",
                        }
                    ],
                },
            }
        ]
    }

    patched = apply_editorial_overrides(sections, enrichment)
    assert "abandono" in patched[0]["body"].lower()
    assert patched[0]["certainty_level"] == "will"
