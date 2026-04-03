from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EPHE_PATH = BASE_DIR / "ephe"

load_dotenv(BASE_DIR / ".env")


def _get_env(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def _get_int(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {key} must be an integer.") from exc


def _get_float(key: str, default: float) -> float:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {key} must be a float.") from exc


def _get_bool(key: str, default: bool = False) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_list(key: str, default: list[str]) -> list[str]:
    value = os.getenv(key)
    if value is None:
        return default

    parsed = [item.strip() for item in value.split(",")]
    return [item for item in parsed if item]


@dataclass(frozen=True)
class Settings:
    app_name: str = _get_env("APP_NAME", "Codigo do Destino API")
    app_version: str = _get_env("APP_VERSION", "3.0.0")
    engine_version: str = _get_env("ENGINE_VERSION", "engine-3.0.0")
    environment: str = _get_env("ENVIRONMENT", "development")
    debug: bool = _get_bool("DEBUG", True)

    database_url: str = _get_env(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/astrologia",
    )
    redis_url: str = _get_env("REDIS_URL", "redis://localhost:6379/0")

    map_cache_ttl: int = _get_int("MAP_CACHE_TTL", 60 * 60 * 24 * 7)
    computed_cache_ttl: int = _get_int("COMPUTED_CACHE_TTL", 60 * 60 * 24 * 90)
    ephemeris_cache_ttl: int = _get_int("EPHEMERIS_CACHE_TTL", 60 * 60 * 24 * 180)
    llm_cache_ttl: int = _get_int("LLM_CACHE_TTL", 60 * 60 * 24 * 30)
    local_cache_ttl_seconds: int = _get_int("LOCAL_CACHE_TTL_SECONDS", 20)
    cache_ttl_jitter_seconds: int = _get_int("CACHE_TTL_JITTER_SECONDS", 90)

    redis_socket_timeout_seconds: int = _get_int("REDIS_SOCKET_TIMEOUT_SECONDS", 2)
    auto_create_schema: bool = _get_bool("AUTO_CREATE_SCHEMA", True)

    db_pool_size: int = _get_int("DB_POOL_SIZE", 10)
    db_max_overflow: int = _get_int("DB_MAX_OVERFLOW", 20)
    db_pool_recycle_seconds: int = _get_int("DB_POOL_RECYCLE_SECONDS", 1800)

    swisseph_path: str = _get_env("SWISSEPH_PATH", str(DEFAULT_EPHE_PATH))

    max_events_in_response: int = _get_int("MAX_EVENTS_IN_RESPONSE", 6)
    max_events_in_prompt: int = _get_int("MAX_EVENTS_IN_PROMPT", 3)
    llm_complexity_threshold: float = _get_float("LLM_COMPLEXITY_THRESHOLD", 0.55)
    llm_min_high_intensity_events: int = _get_int("LLM_MIN_HIGH_INTENSITY_EVENTS", 1)
    llm_max_tokens: int = _get_int("LLM_MAX_TOKENS", 320)
    llm_force_for_master_numbers: bool = _get_bool("LLM_FORCE_FOR_MASTER_NUMBERS", True)

    openrouter_api_key: str = _get_env("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = _get_env(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    )
    openrouter_model: str = _get_env(
        "OPENROUTER_MODEL",
        "deepseek/deepseek-chat-v3.1",
    )
    openrouter_fallback_model: str = _get_env(
        "OPENROUTER_FALLBACK_MODEL",
        "deepseek/deepseek-v3.2",
    )
    openrouter_site_url: str = _get_env(
        "OPENROUTER_SITE_URL",
        "https://codigododestino.local",
    )
    openrouter_app_name: str = _get_env(
        "OPENROUTER_APP_NAME",
        "CodigodoDestino",
    )
    cors_allow_origins: list[str] = field(
        default_factory=lambda: _get_list(
            "CORS_ALLOW_ORIGINS",
            ["http://localhost:3000", "http://127.0.0.1:3000"],
        )
    )


settings = Settings()
