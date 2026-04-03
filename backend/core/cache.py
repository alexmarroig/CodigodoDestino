from __future__ import annotations

import random
import time
from threading import RLock
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from core.config import settings
from core.serialization import json_dumps, json_loads


class CacheClient:
    enabled = True
    _memory_cache: dict[str, tuple[float, bytes]] = {}
    _memory_lock = RLock()

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def _ttl_with_jitter(self, ttl: int) -> int:
        if ttl <= 0:
            return ttl
        jitter = settings.cache_ttl_jitter_seconds
        if jitter <= 0:
            return ttl
        return max(1, ttl + random.randint(0, jitter))

    def _get_memory(self, key: str) -> bytes | None:
        now = time.monotonic()
        with self._memory_lock:
            cached = self._memory_cache.get(key)
            if cached is None:
                return None
            expires_at, payload = cached
            if expires_at <= now:
                self._memory_cache.pop(key, None)
                return None
            return payload

    def _set_memory(self, key: str, payload: bytes, ttl: int) -> None:
        ttl_seconds = min(ttl, settings.local_cache_ttl_seconds)
        if ttl_seconds <= 0:
            return
        expires_at = time.monotonic() + ttl_seconds
        with self._memory_lock:
            self._memory_cache[key] = (expires_at, payload)

    def get_cache(self, key: str) -> dict[str, Any] | None:
        raw = self._get_memory(key)
        if raw is None:
            try:
                raw = self.redis.get(key)
            except RedisError:
                return None
            if raw is None:
                return None
            self._set_memory(key, raw, settings.local_cache_ttl_seconds)

        try:
            loaded = json_loads(raw)
        except ValueError:
            return None

        if isinstance(loaded, dict):
            return loaded
        return None

    def set_cache(self, key: str, value: dict[str, Any], ttl: int = 86400) -> None:
        try:
            payload = json_dumps(value)
        except TypeError:
            return None

        effective_ttl = self._ttl_with_jitter(ttl)
        self._set_memory(key, payload, effective_ttl)

        try:
            self.redis.setex(key, effective_ttl, payload)
        except RedisError:
            return None

    def ping(self) -> bool:
        try:
            return bool(self.redis.ping())
        except RedisError:
            return False


class NullCacheClient(CacheClient):
    enabled = False

    def __init__(self):
        self.redis = None

    def get_cache(self, key: str) -> dict[str, Any] | None:
        return None

    def set_cache(self, key: str, value: dict[str, Any], ttl: int = 86400) -> None:
        return None

    def ping(self) -> bool:
        return False
