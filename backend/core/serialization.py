from __future__ import annotations

import hashlib
from typing import Any

import orjson

ORJSON_SORTED = orjson.OPT_SORT_KEYS


def json_dumps(data: Any, *, sort_keys: bool = False) -> bytes:
    option = ORJSON_SORTED if sort_keys else 0
    return orjson.dumps(data, option=option)


def json_dumps_text(data: Any, *, sort_keys: bool = False) -> str:
    return json_dumps(data, sort_keys=sort_keys).decode("utf-8")


def json_loads(data: bytes | bytearray | memoryview | str) -> Any:
    if isinstance(data, str):
        return orjson.loads(data)
    return orjson.loads(bytes(data))


def stable_hash(data: Any) -> str:
    return hashlib.sha256(json_dumps(data, sort_keys=True)).hexdigest()
