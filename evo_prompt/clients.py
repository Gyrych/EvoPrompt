from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
import asyncio
import json

import httpx


class ModelClient(ABC):
    """Abstract model client interface."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate text for a given prompt. Returns a standardized dict.

        Standard return shape:
        { "text": str, "raw": dict, "usage": dict }
        """

    @abstractmethod
    def close(self) -> None:
        """Cleanup resources if needed."""


@dataclass
class OpenAICompatibleClient(ModelClient):
    api_key: str
    base_url: Optional[str] = None
    model: str = "gpt-4"
    timeout: int = 60

    def __post_init__(self) -> None:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        self._client = httpx.AsyncClient(timeout=self.timeout, headers=headers)
        # default to OpenAI API base if not provided
        self.base_url = self.base_url or "https://api.openai.com/v1"

    async def generate(self, prompt: str, temperature: float = 0.0, max_tokens: int = 512, **kwargs: Any) -> Dict[str, Any]:
        # Use chat completions if available
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        # merge any additional kwargs into payload
        payload.update(kwargs)

        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        # Normalize output
        text = ""
        try:
            # chat completions shape
            choices = data.get("choices", [])
            if choices:
                # join assistant content if multiple
                parts = []
                for c in choices:
                    msg = c.get("message") or {}
                    content = msg.get("content") or c.get("text")
                    if content:
                        parts.append(content)
                text = "\n".join(parts)
        except Exception:
            text = data.get("text") or ""

        usage = data.get("usage", {})
        return {"text": text, "raw": data, "usage": usage}

    def close(self) -> None:
        # Synchronous wrapper that schedules an async close safely.
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # schedule async close without awaiting (best-effort)
                loop.create_task(self._client.aclose())
            else:
                loop.run_until_complete(self._client.aclose())
        except RuntimeError:
            # No running loop; create a new one to close
            try:
                asyncio.run(self._client.aclose())
            except Exception:
                pass
        except Exception:
            pass


