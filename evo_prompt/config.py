from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json
import getpass


@dataclass
class Config:
    student_api_key: Optional[str] = None
    student_base_url: Optional[str] = None
    student_model: str = "gpt-4"

    teacher_api_key: Optional[str] = None
    teacher_base_url: Optional[str] = None
    teacher_model: str = "gpt-4"

    prompts_dir: str = "prompts"
    logs_dir: str = "logs"
    results_dir: str = "results"

    temperature: float = 0.0
    max_tokens: int = 512


def load_config(path: Path | str) -> Config:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    data = json.loads(p.read_text(encoding="utf-8"))
    return Config(**data)


def interactive_config_prompt() -> Config:
    print("Interactive config setup — enter API keys and preferences.\nPress Enter to skip a value.")
    student_api_key = input("Student (DeepSeek) API key: ") or None
    student_base_url = input("Student base URL (leave empty for OpenAI): ") or None
    student_model = input("Student model name [gpt-4]: ") or "gpt-4"

    teacher_api_key = input("Teacher (GPT-4) API key: ") or None
    teacher_base_url = input("Teacher base URL (leave empty for OpenAI): ") or None
    teacher_model = input("Teacher model name [gpt-4]: ") or "gpt-4"

    cfg = Config(
        student_api_key=student_api_key,
        student_base_url=student_base_url,
        student_model=student_model,
        teacher_api_key=teacher_api_key,
        teacher_base_url=teacher_base_url,
        teacher_model=teacher_model,
    )
    return cfg


