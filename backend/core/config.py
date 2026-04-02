from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Astrologia SaaS")
    app_version: str = os.getenv("APP_VERSION", "2.1.0")
    engine_version: str = os.getenv("ENGINE_VERSION", "engine-2.1.0")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/astrologia")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    map_cache_ttl: int = int(os.getenv("MAP_CACHE_TTL", "2592000"))
    ephemeris_cache_ttl: int = int(os.getenv("EPHEMERIS_CACHE_TTL", "15552000"))
    llm_cache_ttl: int = int(os.getenv("LLM_CACHE_TTL", "604800"))

    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3.1")
    openrouter_fallback_model: str = os.getenv("OPENROUTER_FALLBACK_MODEL", "deepseek/deepseek-v3.2")
    openrouter_site_url: str = os.getenv("OPENROUTER_SITE_URL", "https://codigododestino.local")
    openrouter_app_name: str = os.getenv("OPENROUTER_APP_NAME", "CodigodoDestino")


settings = Settings()
