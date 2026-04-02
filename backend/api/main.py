from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

from astro.aspects import calculate_aspects
from astro.ephemeris import calculate_ephemeris
from astro.signs import longitude_to_sign
from astro.time import convert_with_metadata, local_to_utc
from engine.events import generate_events
from engine.narrative import build_narrative_prompt
from numerologia.core import life_path_number, personal_year

app = FastAPI(title="Astrologia SaaS", version="1.0.0")


class MapaRequest(BaseModel):
    date: str = Field(..., examples=["1990-08-15"])
    time: str = Field(..., examples=["14:30:00"])
    timezone: str = Field(..., examples=["America/Sao_Paulo"])
    city: str = Field(..., examples=["São Paulo"])
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    orb_degrees: float = Field(default=6, ge=0, le=12)
    house_system: str = Field(default="P", min_length=1, max_length=1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/mapa")
def mapa(payload: MapaRequest) -> dict:
    utc_meta = convert_with_metadata(payload.date, payload.time, payload.timezone)
    dt_utc = local_to_utc(payload.date, payload.time, payload.timezone)

    eph = calculate_ephemeris(dt_utc, payload.lat, payload.lon, payload.house_system)
    planet_positions = {name: data["longitude"] for name, data in eph.planets.items()}
    aspects = calculate_aspects(planet_positions, payload.orb_degrees)

    signs = {
        name: longitude_to_sign(data["longitude"]).__dict__
        for name, data in eph.planets.items()
    }
    house_signs = [longitude_to_sign(cusp).__dict__ for cusp in eph.houses["cusps"]]
    angle_signs = {
        "ascendant": longitude_to_sign(eph.angles["ascendant"]).__dict__,
        "midheaven": longitude_to_sign(eph.angles["midheaven"]).__dict__,
    }

    numerology = {
        "birth_date": payload.date,
        "life_path_number": life_path_number(payload.date),
        "personal_year": personal_year(payload.date),
    }

    events = generate_events(aspects, eph.houses["cusps"], numerology)
    narrative = build_narrative_prompt(events)

    return {
        "request_id": str(uuid4()),
        "input": payload.model_dump(),
        "computed": {
            "utc": utc_meta.__dict__,
            "astrology": {
                "utc_datetime": eph.utc_datetime,
                "julian_day": eph.julian_day,
                "planets": eph.planets,
                "angles": eph.angles,
                "houses": eph.houses,
                "signs": signs,
                "house_signs": house_signs,
                "angle_signs": angle_signs,
            },
            "aspects": {"orb_degrees": payload.orb_degrees, "aspects": aspects},
            "numerology": numerology,
        },
        "events": events,
        "narrative": {"text": "", "prompt_payload": narrative},
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "version": "v1",
        },
    }
