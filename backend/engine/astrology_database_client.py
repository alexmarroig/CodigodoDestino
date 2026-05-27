from __future__ import annotations

import logging
from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

HOUSE_SYSTEM_MAP = {
    "P": "placidus",
    "K": "koch",
    "W": "whole_sign",
    "E": "equal",
    "R": "regiomontanus",
    "C": "campanus",
    "O": "porphyry",
}


def _parse_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _parse_time(value: Any) -> time:
    if isinstance(value, time):
        return value
    raw = str(value)
    if len(raw.split(":")) == 2:
        raw = f"{raw}:00"
    return time.fromisoformat(raw)


def _timezone_offset_minutes(date_value: date, time_value: time, timezone_name: str) -> int:
    local_dt = datetime.combine(date_value, time_value, tzinfo=ZoneInfo(timezone_name))
    offset = local_dt.utcoffset()
    if offset is None:
        return 0
    return int(offset.total_seconds() // 60)


def build_natal_chart_payload(payload: dict[str, Any]) -> dict[str, Any]:
    birth_date = _parse_date(payload["date"])
    birth_time = _parse_time(payload.get("time") or "12:00:00")
    timezone_name = str(payload["timezone"])
    house_system = HOUSE_SYSTEM_MAP.get(str(payload.get("house_system") or "P").upper(), "placidus")

    return {
        "name": payload.get("name") or "Leitura Codigo do Destino",
        "birth_date_local": birth_date.isoformat(),
        "birth_time_local": birth_time.isoformat(),
        "timezone_offset_minutes": _timezone_offset_minutes(birth_date, birth_time, timezone_name),
        "location_name": payload.get("current_city") or payload.get("location_name"),
        "latitude": float(payload["lat"]),
        "longitude": float(payload["lon"]),
        "house_system": house_system,
        "metadata": {
            "source": "codigododestino",
            "timezone": timezone_name,
        },
    }


class AstrologyDatabaseClient:
    def __init__(
        self,
        base_url: str | None = None,
        *,
        school_code: str | None = None,
        timeout_seconds: float = 45.0,
    ) -> None:
        self.base_url = (base_url or settings.astrology_database_url or "").rstrip("/")
        self.school_code = school_code or settings.astrology_school_code
        self.timeout_seconds = timeout_seconds

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def _request(self, method: str, path: str, *, json: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("AstrologyDatabase client is disabled.")

        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.request(method, url, json=json)
            response.raise_for_status()
            return response.json()

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def create_natal_chart(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = build_natal_chart_payload(payload)
        return self._request("POST", "/api/v1/charts/natal", json=body)

    def calculate_interpretive_priority(self, chart_id: str) -> dict[str, Any]:
        return self._request("POST", f"/api/v1/charts/{chart_id}/interpretive-priority")

    def get_rule(self, rule_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/editorial/rules/{rule_id}")

    def fetch_enrichment(self, payload: dict[str, Any], *, top_rules: int = 8) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        try:
            chart = self.create_natal_chart(payload)
            snapshot = self.calculate_interpretive_priority(str(chart["id"]))
            priorities = list(snapshot.get("priorities") or [])[:top_rules]

            rules: list[dict[str, Any]] = []
            for priority in priorities:
                rule_id = priority.get("rule_id") or priority.get("rule", {}).get("id")
                if not rule_id:
                    continue
                rule = self.get_rule(str(rule_id))
                rules.append(
                    {
                        "priority": priority,
                        "rule": rule,
                    }
                )

            return {
                "chart_id": str(chart["id"]),
                "school_code": snapshot.get("school_code") or self.school_code,
                "snapshot": snapshot,
                "rules": rules,
            }
        except Exception as exc:
            logger.warning(
                "astrology_database_enrichment_failed",
                extra={"error": str(exc), "base_url": self.base_url},
            )
            return None
