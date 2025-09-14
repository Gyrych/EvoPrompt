from __future__ import annotations

from typing import Any, Dict
from .clients import ModelClient


class MockClient(ModelClient):
    def __init__(self, name: str = "mock", text: str | None = None) -> None:
        self.name = name
        self.text = text or "This is a mock response."

    async def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {"text": self.text, "raw": {"mock": True, "prompt_len": len(prompt)}, "usage": {}}

    def close(self) -> None:
        return None


