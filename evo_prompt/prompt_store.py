from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


@dataclass
class PromptMetadata:
    name: str
    version: int
    created_at: str
    updated_at: str
    history: list
    meta: Dict[str, Any]


class PromptStore:
    """Simple JSON-backed prompt store with version history."""

    def __init__(self, store_dir: Path | str = "prompts") -> None:
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, name: str) -> Path:
        return self.store_dir / f"{name}.json"

    def list_prompts(self) -> list[str]:
        return [p.stem for p in self.store_dir.glob("*.json")]

    def get_prompt(self, name: str) -> Dict[str, Any] | None:
        path = self._path_for(name)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def add_or_update_prompt(self, name: str, text: str, author: str = "user", reason: str = "update") -> Dict[str, Any]:
        path = self._path_for(name)
        now = datetime.utcnow().isoformat() + "Z"
        if path.exists():
            obj = json.loads(path.read_text(encoding="utf-8"))
            version = obj.get("version", 1) + 1
            history = obj.get("history", [])
        else:
            version = 1
            history = []

        entry = {"version": version, "text": text, "author": author, "timestamp": now, "reason": reason}
        history.append(entry)

        out = {
            "name": name,
            "version": version,
            "text": text,
            "history": history,
            "meta": {"last_updated": now, "author": author},
        }

        path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        return out

    def save_version(self, name: str, text: str, reason: str = "save") -> None:
        # alias
        self.add_or_update_prompt(name, text, reason=reason)

    def export_all(self, out_path: Path) -> None:
        out = {}
        for name in self.list_prompts():
            out[name] = self.get_prompt(name)
        Path(out_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


