from __future__ import annotations

import logging
import os
from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from core.cache import CacheClient, NullCacheClient
from core.config import settings
from db.base import Base
from db import models  # noqa: F401

logger = logging.getLogger(__name__)

DEFAULT_DEV_SQLITE_PATH = Path(__file__).resolve().parents[1] / "codigodestino.dev.db"
DEFAULT_DEV_SQLITE_URL = f"sqlite:///{DEFAULT_DEV_SQLITE_PATH.as_posix()}"
DATABASE_URL_IS_EXPLICIT = os.getenv("DATABASE_URL") is not None


def _build_engine(url: str) -> Engine:
    engine_kwargs: dict[str, object] = {
        "pool_pre_ping": True,
        "pool_recycle": settings.db_pool_recycle_seconds,
    }

    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_size"] = settings.db_pool_size
        engine_kwargs["max_overflow"] = settings.db_max_overflow
        engine_kwargs["connect_args"] = {"connect_timeout": 3}

    return create_engine(url, **engine_kwargs)


engine = _build_engine(settings.database_url)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def _rebind_engine(url: str) -> None:
    global engine

    engine = _build_engine(url)
    SessionLocal.configure(bind=engine)


def initialize_database() -> None:
    if not settings.auto_create_schema:
        return

    try:
        Base.metadata.create_all(bind=engine)
    except (OperationalError, SQLAlchemyError) as exc:
        can_fallback = not DATABASE_URL_IS_EXPLICIT and not str(engine.url).startswith("sqlite")
        if not can_fallback:
          raise

        logger.warning(
            "database_unavailable_falling_back_to_sqlite",
            extra={
                "database_url": settings.database_url,
                "sqlite_url": DEFAULT_DEV_SQLITE_URL,
            },
        )
        _rebind_engine(DEFAULT_DEV_SQLITE_URL)
        Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache(maxsize=1)
def _build_redis_client() -> Redis:
    return Redis.from_url(
        settings.redis_url,
        decode_responses=False,
        socket_connect_timeout=settings.redis_socket_timeout_seconds,
        socket_timeout=settings.redis_socket_timeout_seconds,
    )


def get_cache_client() -> CacheClient:
    try:
        redis_client = _build_redis_client()
        redis_client.ping()
        return CacheClient(redis_client)
    except RedisError:
        logger.warning("redis_unavailable_falling_back_to_null_cache")
        return NullCacheClient()
