from __future__ import annotations

from pathlib import Path
import json
import hashlib
from typing import Any
from datetime import datetime, timedelta


class Cache:
    def __init__(self, cache_dir: Path | str = ".cache", ttl_seconds: int = 3600) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds

    def _key_for(self, prompt: str, model: str, params: dict) -> str:
        h = hashlib.sha256()
        h.update(prompt.encode("utf-8"))
        h.update(model.encode("utf-8"))
        h.update(json.dumps(params, sort_keys=True).encode("utf-8"))
        return h.hexdigest()

    def get(self, prompt: str, model: str, params: dict) -> Any | None:
        key = self._key_for(prompt, model, params)
        path = self.cache_dir / f"{key}.json"
        if not path.exists():
            return None
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            ts = obj.get("timestamp")
            if ts:
                t = datetime.fromisoformat(ts)
                if datetime.utcnow() - t > timedelta(seconds=self.ttl):
                    return None
            return obj.get("value")
        except Exception:
            return None

    def set(self, prompt: str, model: str, params: dict, value: Any) -> None:
        key = self._key_for(prompt, model, params)
        path = self.cache_dir / f"{key}.json"
        obj = {"timestamp": datetime.utcnow().isoformat(), "value": value}
        path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


