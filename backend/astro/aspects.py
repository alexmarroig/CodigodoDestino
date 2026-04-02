from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations

ASPECTS = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}


@dataclass(frozen=True)
class AspectResult:
    planet_a: str
    planet_b: str
    aspect: str
    target_angle: float
    exact_angle: float
    orb: float


def angular_distance(a: float, b: float) -> float:
    diff = abs((a - b) % 360.0)
    return min(diff, 360.0 - diff)


def calculate_aspects(positions: dict[str, float], orb_degrees: float = 6.0) -> list[dict]:
    found: list[AspectResult] = []
    for p1, p2 in combinations(sorted(positions.keys()), 2):
        angle = angular_distance(positions[p1], positions[p2])
        for aspect_name, target in ASPECTS.items():
            orb = abs(angle - target)
            if orb <= orb_degrees:
                found.append(
                    AspectResult(
                        planet_a=p1,
                        planet_b=p2,
                        aspect=aspect_name,
                        target_angle=target,
                        exact_angle=round(angle, 6),
                        orb=round(orb, 6),
                    )
                )
    return [asdict(item) for item in found]
