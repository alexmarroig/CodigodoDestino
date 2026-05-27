from __future__ import annotations

from typing import Any

from engine.astrology_database_client import AstrologyDatabaseClient
from engine.certainty import CERTAINTY_LABELS, apply_certainty_prefix, certainty_from_signal_count

FATALISTIC_THEMES = {
    "shadow",
    "transformation",
    "emotional",
    "relational",
    "family",
    "vocational",
    "financial",
}

THEME_TO_SECTION = {
    "identity": "personality",
    "mental": "personality",
    "emotional": "emotional_pattern",
    "shadow": "core_wound",
    "transformation": "core_wound",
    "relational": "relationships",
    "family": "family",
    "vocational": "career",
    "financial": "money",
    "body": "future_events",
    "spiritual": "critical_cycles",
}


def fetch_editorial_enrichment(payload: dict[str, Any]) -> dict[str, Any] | None:
    client = AstrologyDatabaseClient()
    return client.fetch_enrichment(payload)


def _score_to_certainty(total_score: float, rank: int) -> str:
    if total_score >= 12 or (rank == 1 and total_score >= 9):
        return "will"
    if total_score >= 9:
        return "must"
    if total_score >= 6:
        return "tendency"
    return "chance"


def _pick_fatalistic_text(block: dict[str, Any]) -> str:
    for key in ("poorly_expressed", "challenges", "potency_central", "well_expressed"):
        value = str(block.get(key) or "").strip()
        if value:
            return value
    return ""


def _extract_rule_lines(rule_bundle: dict[str, Any]) -> list[str]:
    priority = dict(rule_bundle.get("priority") or {})
    rule = dict(rule_bundle.get("rule") or {})
    blocks = list(rule.get("blocks") or [])
    themes = [str(theme) for theme in (priority.get("themes") or priority.get("matched_themes_json") or [])]

    selected_blocks = [
        block
        for block in blocks
        if str(block.get("theme") or "") in FATALISTIC_THEMES or str(block.get("theme") or "") in themes
    ]
    if not selected_blocks and blocks:
        selected_blocks = blocks[:2]

    lines: list[str] = []
    for block in selected_blocks[:2]:
        text = _pick_fatalistic_text(block)
        if text:
            lines.append(text)
    return lines


def build_section_overrides(enrichment: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not enrichment:
        return {}

    overrides: dict[str, dict[str, Any]] = {}
    for rule_bundle in enrichment.get("rules") or []:
        priority = dict(rule_bundle.get("priority") or {})
        rule = dict(rule_bundle.get("rule") or {})
        lines = _extract_rule_lines(rule_bundle)
        if not lines:
            continue

        themes = [str(theme) for theme in (priority.get("themes") or [])]
        section_id = None
        for theme in themes:
            section_id = THEME_TO_SECTION.get(theme)
            if section_id:
                break
        if section_id is None:
            section_id = "personality"

        certainty = _score_to_certainty(float(priority.get("total_score") or 0), int(priority.get("rank") or 99))
        summary = apply_certainty_prefix(lines[0], certainty)
        body = "\n\n".join(
            apply_certainty_prefix(line, certainty) if index == 0 else line for index, line in enumerate(lines)
        )

        current = overrides.get(section_id)
        if current and float(current.get("_score") or 0) >= float(priority.get("total_score") or 0):
            continue

        overrides[section_id] = {
            "_score": float(priority.get("total_score") or 0),
            "summary": summary[:280],
            "body": body,
            "certainty_level": certainty,
            "certainty_label": CERTAINTY_LABELS[certainty],
            "evidence": [str(rule.get("canonical_code") or "")],
        }

    for section in overrides.values():
        section.pop("_score", None)
    return overrides


def apply_editorial_overrides(
    sections: list[dict[str, Any]],
    enrichment: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    overrides = build_section_overrides(enrichment)
    if not overrides:
        return sections

    patched: list[dict[str, Any]] = []
    for section in sections:
        override = overrides.get(str(section.get("id")))
        if not override:
            patched.append(section)
            continue
        merged = dict(section)
        merged.update(
            {
                "summary": override["summary"],
                "body": override["body"],
                "certainty_level": override["certainty_level"],
                "certainty_label": override["certainty_label"],
                "evidence": list(dict.fromkeys([*(section.get("evidence") or []), *override["evidence"]])),
            }
        )
        patched.append(merged)
    return patched


def boost_predictive_from_clusters(
    analysis: dict[str, Any],
    enrichment: dict[str, Any] | None,
) -> None:
    if not enrichment:
        return

    snapshot = dict(enrichment.get("snapshot") or {})
    clusters = list(snapshot.get("clusters") or [])
    if not clusters:
        return

    top_cluster = max(clusters, key=lambda item: float(item.get("cluster_score") or 0))
    analysis.setdefault("astrology_database", enrichment)
    analysis["astrology_database"]["top_cluster"] = top_cluster

    predictive = dict(analysis.get("predictive_insights") or {})
    summary = dict(predictive.get("summary") or {})
    if top_cluster.get("summary"):
        summary["editorial_cluster"] = top_cluster["summary"]
    predictive["summary"] = summary
    analysis["predictive_insights"] = predictive
