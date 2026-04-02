from __future__ import annotations

from pydantic import BaseModel, Field


class MapaRequest(BaseModel):
    date: str = Field(..., examples=["1990-08-15"])
    time: str = Field(..., examples=["14:30:00"])
    timezone: str = Field(..., examples=["America/Sao_Paulo"])
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    orb_degrees: float = Field(default=6.0, ge=0, le=12)
    house_system: str = Field(default="P", min_length=1, max_length=1)
    reference_date: str = Field(..., examples=["2026-04-02"])
    user_id: int | None = None
