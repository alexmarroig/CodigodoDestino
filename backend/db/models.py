from __future__ import annotations

from datetime import datetime
from datetime import date as DateType
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

JSON_PAYLOAD = JSON().with_variant(JSONB, "postgresql")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    map_requests: Mapped[list["MapRequest"]] = relationship(back_populates="user")
    life_events: Mapped[list["UserLifeEvent"]] = relationship(back_populates="user")
    feedback_events: Mapped[list["UserFeedbackEvent"]] = relationship(back_populates="user")
    rule_weights: Mapped[list["UserRuleWeight"]] = relationship(back_populates="user")


class MapRequest(Base):
    __tablename__ = "map_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    input_data: Mapped[dict[str, Any]] = mapped_column(JSON_PAYLOAD, nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(JSON_PAYLOAD, nullable=False)
    engine_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped[User | None] = relationship(back_populates="map_requests")


class UserLifeEvent(Base):
    __tablename__ = "user_life_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_date: Mapped[DateType] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    natal_input: Mapped[dict[str, Any]] = mapped_column(JSON_PAYLOAD, nullable=False)
    transits: Mapped[list[dict[str, Any]]] = mapped_column(JSON_PAYLOAD, nullable=False, default=list)
    progressions: Mapped[list[dict[str, Any]]] = mapped_column(JSON_PAYLOAD, nullable=False, default=list)
    solar_arc: Mapped[list[dict[str, Any]]] = mapped_column(JSON_PAYLOAD, nullable=False, default=list)
    rule_hits: Mapped[list[dict[str, Any]]] = mapped_column(JSON_PAYLOAD, nullable=False, default=list)
    special_analysis: Mapped[dict[str, Any]] = mapped_column(JSON_PAYLOAD, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped[User | None] = relationship(back_populates="life_events")


class UserFeedbackEvent(Base):
    __tablename__ = "user_feedback_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_date: Mapped[DateType] = mapped_column(Date, nullable=False, index=True)
    predicted: Mapped[bool] = mapped_column(nullable=False, default=False)
    real_intensity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    natal_input: Mapped[dict[str, Any]] = mapped_column(JSON_PAYLOAD, nullable=False)
    transits: Mapped[list[dict[str, Any]]] = mapped_column(JSON_PAYLOAD, nullable=False, default=list)
    progressions: Mapped[list[dict[str, Any]]] = mapped_column(JSON_PAYLOAD, nullable=False, default=list)
    solar_arc: Mapped[list[dict[str, Any]]] = mapped_column(JSON_PAYLOAD, nullable=False, default=list)
    rule_hits: Mapped[list[dict[str, Any]]] = mapped_column(JSON_PAYLOAD, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user: Mapped[User | None] = relationship(back_populates="feedback_events")


class UserRuleWeight(Base):
    __tablename__ = "user_rule_weights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    rule_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_intensity: Mapped[float] = mapped_column(nullable=False, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user: Mapped[User | None] = relationship(back_populates="rule_weights")
