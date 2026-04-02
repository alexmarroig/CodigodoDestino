from __future__ import annotations


def build_narrative_prompt(events: list[dict]) -> str:
    lines: list[str] = [
        "Crie uma narrativa em português sem termos técnicos.",
        "Organize por tempo e intensidade.",
        "Eventos:",
    ]
    for event in events:
        lines.append(
            f"- {event['event']} | categoria={event['category']} | intensidade={event['intensity']} | periodo={event['time_window']['start']}"
        )
    return "\n".join(lines)
