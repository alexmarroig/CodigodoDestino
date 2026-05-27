from __future__ import annotations

from datetime import date as DateType
from datetime import time as TimeType
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserContextRequest(BaseModel):
    relationship_status: Literal[
        "single",
        "dating",
        "engaged",
        "married",
        "separated",
        "divorced",
        "widowed",
        "unknown",
    ] | None = None
    current_partner_role: Literal[
        "girlfriend",
        "boyfriend",
        "wife",
        "husband",
        "partner",
        "unknown",
    ] | None = None
    employment_status: Literal[
        "employed",
        "unemployed",
        "self_employed",
        "student",
        "retired",
    ] | None = None
    has_children: bool | None = None
    father_status: Literal["alive", "deceased", "unknown"] | None = None
    mother_status: Literal["alive", "deceased", "unknown"] | None = None
    current_city: str | None = Field(default=None, max_length=120)
    lives_alone: bool | None = None
    living_situation: Literal["alone", "with_partner", "with_family", "shared"] | None = None
    father_present: bool | None = None
    mother_present: bool | None = None
    father_relationship: Literal[
        "close",
        "distant",
        "conflict",
        "absent",
        "unknown",
    ] | None = None
    mother_relationship: Literal[
        "close",
        "distant",
        "conflict",
        "absent",
        "unknown",
    ] | None = None
    has_siblings: bool | None = None
    experienced_adoption: bool | None = None
    experienced_abandonment: bool | None = None
    major_trauma_notes: str | None = Field(default=None, max_length=500)
    major_loss_notes: str | None = Field(default=None, max_length=500)
    marked_separation: bool | None = None
    experienced_betrayal: bool | None = None
    experienced_depression: bool | None = None
    recurring_feeling: str | None = Field(default=None, max_length=200)
    city_change: bool | None = None
    country_change: bool | None = None
    financial_crisis: bool | None = None
    important_death: str | None = Field(default=None, max_length=200)

    @field_validator("living_situation", mode="before")
    @classmethod
    def normalize_living_situation(cls, value: object) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip().lower()
        allowed = {"alone", "with_partner", "with_family", "shared"}
        if normalized in allowed:
            return normalized
        if "sozinho" in normalized:
            return "alone"
        if any(token in normalized for token in ("parceiro", "cônjuge", "conjuge", "casal")):
            return "with_partner"
        if "família" in normalized or "familia" in normalized:
            return "with_family"
        if "compartilh" in normalized or "shared" in normalized:
            return "shared"
        return None


class RelatedPersonRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    relation: Literal[
        "spouse",
        "partner",
        "boyfriend",
        "girlfriend",
        "father",
        "mother",
        "child",
        "friend",
        "sibling",
        "in_law",
        "other",
    ]
    birth_date: DateType | None = None
    birth_time: TimeType | None = None
    birth_time_precision: Literal["exact", "window", "unknown"] | None = None


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
    user_context: UserContextRequest | None = None
    related_people: list[RelatedPersonRequest] | None = None

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


class LifeEventRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "relationship_start",
                "event_date": "2024-08-10",
                "description": "Comecei um relacionamento importante.",
                "birth_date": "1995-03-10",
                "birth_time": "14:30",
                "birth_lat": -23.55,
                "birth_lon": -46.63,
                "birth_timezone": "America/Sao_Paulo",
            }
        }
    )

    event_type: str = Field(..., min_length=3, max_length=64)
    event_date: DateType = Field(..., description="Life event date in ISO format.")
    event_time: TimeType | None = Field(default=None, description="Optional life event time.")
    description: str | None = Field(default=None, max_length=1000)
    user_id: int | None = None

    birth_date: DateType
    birth_time: TimeType | None = None
    birth_lat: float = Field(..., ge=-90, le=90)
    birth_lon: float = Field(..., ge=-180, le=180)
    birth_timezone: str
    birth_time_precision: Literal["exact", "window", "unknown"] | None = Field(default=None)
    birth_time_window: Literal["morning", "afternoon", "evening"] | None = Field(default=None)
    house_system: str = Field(default="P", min_length=1, max_length=1)
    orb_degrees: float = Field(default=6.0, ge=0.0, le=12.0)

    event_lat: float | None = Field(default=None, ge=-90, le=90)
    event_lon: float | None = Field(default=None, ge=-180, le=180)
    event_timezone: str | None = Field(default=None)

    @field_validator("birth_timezone")
    @classmethod
    def validate_birth_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unsupported timezone: {value}") from exc
        return value

    @field_validator("event_timezone")
    @classmethod
    def validate_event_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unsupported timezone: {value}") from exc
        return value

    @field_validator("house_system")
    @classmethod
    def validate_life_event_house_system(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 1:
            raise ValueError("house_system must contain exactly one character.")
        return normalized


class FeedbackEventRequest(LifeEventRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "career_change",
                "event_date": "2025-11-14",
                "real_intensity": 4,
                "predicted": True,
                "description": "Troquei de trabalho depois de um periodo de pressao.",
                "birth_date": "1995-03-10",
                "birth_time": "14:30",
                "birth_lat": -23.55,
                "birth_lon": -46.63,
                "birth_timezone": "America/Sao_Paulo",
            }
        }
    )

    predicted: bool = Field(default=False)
    real_intensity: int = Field(default=3, ge=1, le=5)
