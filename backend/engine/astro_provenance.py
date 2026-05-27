"""
Structured astrological provenance for predictions (traceable drivers + exclusions).
"""

from __future__ import annotations

from typing import Any

from engine.astro_confirmation import (
    filter_generational_pairs,
    filter_self_aspects,
    score_signal,
)
from engine.cluster_convergence import compute_cluster_metrics
from engine.signal_enrichment import format_brady_por_que_line, has_hard_slow_transit, soft_aspect_opportunity_note
from engine.portuguese_text import polish_portuguese


def _weight_reason(signal: dict[str, Any]) -> str:
    ev = signal.get("evidence") or {}
    parts: list[str] = []
    pa = str(ev.get("planet_a") or "").replace("_", " ")
    if pa.lower() in {"saturn", "uranus", "neptune", "pluto", "jupiter"}:
        parts.append("planeta lento")
    orb = ev.get("orb_degrees")
    if isinstance(orb, (int, float)) and float(orb) < 1.0:
        parts.append("orbe < 1°")
    th = ev.get("transit_house")
    nh = ev.get("natal_house")
    if th in {1, 4, 7, 10} or nh in {1, 4, 7, 10}:
        parts.append("casa angular")
    if ev.get("dignity_downgrade"):
        parts.append("dignidade fraca no receptor")
    if ev.get("natal_dignity_supports_gain"):
        parts.append("dignidade forte no receptor")
    return "; ".join(parts) if parts else "sinal ponderado pelo motor"


def _driver_from_signal(signal: dict[str, Any]) -> dict[str, Any]:
    ev = dict(signal.get("evidence") or {})
    brady = format_brady_por_que_line(ev)
    return {
        "technique": str(signal.get("technique") or ""),
        "label": str(signal.get("label") or ""),
        "aspect": str(ev.get("aspect") or ""),
        "planet_a": str(ev.get("planet_a") or ""),
        "planet_b": str(ev.get("planet_b") or ""),
        "orb_degrees": ev.get("orb_degrees"),
        "transit_house": ev.get("transit_house"),
        "natal_house": ev.get("natal_house"),
        "brady_line": brady,
        "weight_reason": _weight_reason(signal),
        "score": round(score_signal(signal), 3),
    }


def _exclusion_reason(signal: dict[str, Any]) -> str | None:
    ev = signal.get("evidence") or {}
    pa = str(ev.get("planet_a") or "")
    pb = str(ev.get("planet_b") or "")
    if pa and pa == pb:
        return f"{signal.get('label', pa)} — auto-aspecto, não sustenta evento concreto"
    aspect = str(ev.get("aspect") or "")
    if aspect in {"trine", "sextile"}:
        slow = pa.replace("_", " ").lower() in {"saturn", "uranus", "neptune", "pluto", "jupiter"}
        if slow or str(signal.get("technique")) == "transits":
            return f"{signal.get('label', '')} — aspecto de fluxo/oportunidade, não crise isolada"
    planets = {pa.replace("_", " ").lower(), pb.replace("_", " ").lower()}
    outer = {"uranus", "neptune", "pluto"}
    if planets <= outer or (planets & outer and len(planets) == 2):
        gen = filter_generational_pairs([signal])
        if not gen:
            return f"{signal.get('label', '')} — par geracional, não evento pessoal datável"
    return None


def _timing_from_window(time_window: dict[str, Any] | None) -> dict[str, Any]:
    if not time_window:
        return {"mode": "periodo_em_formacao"}
    ev_mode = str(time_window.get("precision") or "")
    if time_window.get("trigger_label"):
        return {
            "mode": "pico_datado",
            "peak": time_window.get("peak"),
            "trigger": time_window.get("trigger_label"),
        }
    if ev_mode == "trigger" or time_window.get("trigger_planet_scan"):
        return {
            "mode": "pico_datado",
            "peak": time_window.get("peak"),
            "trigger": time_window.get("trigger_label") or "planeta rápido",
        }
    duration = int(time_window.get("duration_days") or 0)
    if duration > 180:
        return {
            "mode": "tema_no_periodo",
            "start": time_window.get("start"),
            "end": time_window.get("end"),
        }
    return {
        "mode": "janela",
        "start": time_window.get("start"),
        "end": time_window.get("end"),
        "peak": time_window.get("peak"),
    }


def build_astro_provenance(
    *,
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]] | None = None,
    time_window: dict[str, Any] | None = None,
    certainty_level: str = "tendency",
    category_key: str = "",
    cluster_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    clean = filter_generational_pairs(filter_self_aspects(list(signals)))
    ranked = sorted(clean, key=lambda s: -score_signal(s))

    drivers = [_driver_from_signal(s) for s in ranked[:3]]
    excluded: list[str] = []
    used_labels = {d["label"] for d in drivers}
    for signal in signals:
        if signal.get("label") in used_labels:
            continue
        reason = _exclusion_reason(signal)
        if reason:
            excluded.append(reason)

    metrics = cluster_metrics or compute_cluster_metrics(clean, rule_hits)
    confidence_caps: list[str] = []
    if not has_hard_slow_transit(clean) and category_key in {
        "rupture", "health", "major_transitions", "career", "finance",
    }:
        confidence_caps.append(
            "Sem aspecto duro de planeta lento — certeza limitada a tendência ou oportunidade"
        )
    if int(metrics.get("theme_convergence") or 0) < 2:
        confidence_caps.append(
            "Pouca convergência temática — técnicas podem apontar o mesmo eixo"
        )
    if certainty_level in {"must", "will"} and confidence_caps:
        confidence_caps.append(
            f"Rótulo de certeza '{certainty_level}' já foi rebaixado pelo motor quando aplicável"
        )

    soft_note = soft_aspect_opportunity_note(clean)
    dignity_notes = []
    for s in ranked[:4]:
        ev = s.get("evidence") or {}
        if ev.get("dignity_downgrade"):
            dignity_notes.append(
                "Trânsito de apoio com receptor debilitado — conforto ilusório, não ganho estrutural"
            )
            break
        if ev.get("natal_dignity_supports_gain"):
            dignity_notes.append("Receptor com dignidade forte — maior chance de manifestação real")
            break

    return {
        "primary_drivers": drivers,
        "supporting_techniques": metrics.get("techniques", []),
        "cluster": {
            "technique_count": metrics.get("technique_count", 0),
            "theme_convergence": metrics.get("theme_convergence", 0),
            "effective_independent_signals": metrics.get("effective_independent_signals", 0),
            "rule_hits": [str(h.get("code") or "") for h in (rule_hits or [])[:5]],
        },
        "dignity_note": dignity_notes[0] if dignity_notes else None,
        "timing": _timing_from_window(time_window),
        "excluded": excluded[:6],
        "confidence_caps": confidence_caps,
        "soft_aspect_note": soft_note,
    }


def format_provenance_technical_block(provenance: dict[str, Any]) -> str:
    """Human-readable block for accordion."""
    lines: list[str] = []
    drivers = list(provenance.get("primary_drivers") or [])
    if drivers:
        lines.append("Drivers principais do mapa:")
        for i, d in enumerate(drivers, 1):
            orb = d.get("orb_degrees")
            orb_s = f", orbe {float(orb):.2f}°" if isinstance(orb, (int, float)) else ""
            lines.append(
                f"{i}. [{d.get('technique')}] {d.get('label')}{orb_s} — {d.get('weight_reason')}"
            )
            if d.get("brady_line"):
                lines.append(f"   {d['brady_line']}")
    cluster = provenance.get("cluster") or {}
    if cluster:
        lines.append(
            f"\nConvergência: {cluster.get('technique_count')} técnica(s), "
            f"{cluster.get('theme_convergence')} alvo(s) temático(s), "
            f"efetivo={cluster.get('effective_independent_signals')}."
        )
    timing = provenance.get("timing") or {}
    if timing.get("mode") == "tema_no_periodo":
        lines.append("\nTiming: ciclo longo — tema sensível no período (sem data exata fechada).")
    elif timing.get("mode") == "pico_datado":
        lines.append(
            f"\nTiming: pico em {timing.get('peak')} ({timing.get('trigger', 'gatilho rápido')})."
        )
    if provenance.get("dignity_note"):
        lines.append(f"\nDignidade: {provenance['dignity_note']}")
    if provenance.get("soft_aspect_note"):
        lines.append(f"\n{provenance['soft_aspect_note']}")
    excluded = list(provenance.get("excluded") or [])
    if excluded:
        lines.append("\nSinais não usados como causa principal:")
        for item in excluded:
            lines.append(f"• {item}")
    caps = list(provenance.get("confidence_caps") or [])
    if caps:
        lines.append("\nLimites de interpretação:")
        for cap in caps:
            lines.append(f"• {cap}")
    return polish_portuguese("\n".join(lines))


def build_human_por_que_from_provenance(provenance: dict[str, Any]) -> str:
    drivers = list(provenance.get("primary_drivers") or [])
    if not drivers:
        return ""
    cluster = provenance.get("cluster") or {}
    eff = cluster.get("effective_independent_signals", 0)
    parts: list[str] = []
    d0 = drivers[0]
    if d0.get("brady_line"):
        parts.append(d0["brady_line"])
    else:
        parts.append(str(d0.get("label") or ""))
    if eff >= 2:
        parts.append(
            f"{eff} camadas técnicas convergem ({', '.join((provenance.get('supporting_techniques') or [])[:3])})"
        )
    return "; ".join(p for p in parts if p)
