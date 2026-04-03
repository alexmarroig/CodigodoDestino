from __future__ import annotations

from datetime import date as DateType
from datetime import time as TimeType
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MapaRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "1995-03-10",
                "time": "14:30",
                "lat": -23.55,
                "lon": -46.63,
                "timezone": "America/Sao_Paulo",
            }
        }
    )

    date: DateType = Field(..., description="Birth date in ISO format.")
    time: TimeType | None = Field(default=None, description="Birth time in HH:MM or HH:MM:SS.")
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    timezone: str = Field(..., description="IANA timezone.")
    orb_degrees: float = Field(default=6.0, ge=0.0, le=12.0)
    house_system: str = Field(default="P", min_length=1, max_length=1)
    birth_time_precision: Literal["exact", "window", "unknown"] | None = Field(
        default=None,
        description="Quality hint for the birth time.",
    )
    birth_time_window: Literal["morning", "afternoon", "evening"] | None = Field(
        default=None,
        description="Approximate birth-time window when exact time is unavailable.",
    )
    reference_date: DateType | None = Field(default=None, description="Optional forecast anchor date.")
    user_id: int | None = None

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unsupported timezone: {value}") from exc
        return value

    @field_validator("house_system")
    @classmethod
    def validate_house_system(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 1:
            raise ValueError("house_system must contain exactly one character.")
        return normalized


class HoraryRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "Vou conseguir essa vaga de emprego?",
                "date": "2026-04-02",
                "time": "14:30",
                "lat": -23.55,
                "lon": -46.63,
                "timezone": "America/Sao_Paulo",
            }
        }
    )

    question: str = Field(..., min_length=4, description="Objective horary question.")
    date: DateType = Field(..., description="Question date in ISO format.")
    time: TimeType = Field(..., description="Question time in HH:MM or HH:MM:SS.")
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    timezone: str = Field(..., description="IANA timezone.")
    orb_degrees: float = Field(default=4.0, ge=0.0, le=8.0)
    house_system: str = Field(default="P", min_length=1, max_length=1)

    @field_validator("timezone")
    @classmethod
    def validate_horary_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unsupported timezone: {value}") from exc
        return value

    @field_validator("house_system")
    @classmethod
    def validate_horary_house_system(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 1:
            raise ValueError("house_system must contain exactly one character.")
        return normalized
