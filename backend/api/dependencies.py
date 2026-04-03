from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from core.cache import CacheClient
from db.session import get_cache_client, get_db


def db_dependency(db: Session = Depends(get_db)) -> Session:
    return db


def cache_dependency(cache: CacheClient = Depends(get_cache_client)) -> CacheClient:
    return cache
