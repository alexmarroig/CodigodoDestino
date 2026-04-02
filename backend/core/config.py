from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Astrologia SaaS")
    app_version: str = os.getenv("APP_VERSION", "2.0.0")
    engine_version: str = os.getenv("ENGINE_VERSION", "engine-2.0.0")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/astrologia")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


settings = Settings()
