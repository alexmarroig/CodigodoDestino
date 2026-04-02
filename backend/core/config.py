from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# -----------------------------------
# LOAD ENV (.env)
# -----------------------------------

load_dotenv()


# -----------------------------------
# HELPERS
# -----------------------------------

def _get_env(key: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(key, default)

    if required and (value is None or value.strip() == ""):
        raise RuntimeError(f"Variável de ambiente obrigatória não definida: {key}")

    return value


def _get_int(key: str, default: int) -> int:
    value = os.getenv(key)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Variável {key} deve ser um inteiro") from exc


def _get_bool(key: str, default: bool = False) -> bool:
    value = os.getenv(key)

    if value is None:
        return default

    return value.lower() in ("1", "true", "yes", "on")


# -----------------------------------
# SETTINGS
# -----------------------------------

@dataclass(frozen=True)
class Settings:
    # -----------------------------------
    # APP
    # -----------------------------------

    app_name: str = _get_env("APP_NAME", "Astrologia SaaS")
    app_version: str = _get_env("APP_VERSION", "2.1.0")
    engine_version: str = _get_env("ENGINE_VERSION", "engine-2.1.0")
    environment: str = _get_env("ENVIRONMENT", "development")
    debug: bool = _get_bool("DEBUG", True)

    # -----------------------------------
    # INFRA
    # -----------------------------------

    database_url: str = _get_env(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/astrologia",
    )

    redis_url: str = _get_env(
        "REDIS_URL",
        "redis://localhost:6379/0",
    )

    # -----------------------------------
    # CACHE (segundos)
    # -----------------------------------

    map_cache_ttl: int = _get_int("MAP_CACHE_TTL", 60 * 60 * 24 * 30)        # 30 dias
    ephemeris_cache_ttl: int = _get_int("EPHEMERIS_CACHE_TTL", 60 * 60 * 24 * 180)  # 6 meses
    llm_cache_ttl: int = _get_int("LLM_CACHE_TTL", 60 * 60 * 24 * 7)          # 7 dias

    # -----------------------------------
    # OPENROUTER (IA)
    # -----------------------------------

    openrouter_api_key: str = _get_env("OPENROUTER_API_KEY", required=True)

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


# -----------------------------------
# SINGLETON
# -----------------------------------

settings = Settings()
