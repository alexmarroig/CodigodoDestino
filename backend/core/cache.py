from __future__ import annotations

import json
from typing import Any

from redis import Redis


class CacheClient:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def get_cache(self, key: str) -> dict[str, Any] | None:
        raw = self.redis.get(key)
        if not raw:
            return None
        return json.loads(raw)

    def set_cache(self, key: str, value: dict[str, Any], ttl: int = 86400) -> None:
        self.redis.setex(key, ttl, json.dumps(value, ensure_ascii=False))
