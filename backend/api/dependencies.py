from __future__ import annotations

from core.cache import CacheClient
from db.session import get_cache_client, get_db
from sqlalchemy.orm import Session


def db_dependency() -> Session:
    return next(get_db())


def cache_dependency() -> CacheClient:
    return get_cache_client()
