from __future__ import annotations

from typing import Dict, Any
from .clients import ModelClient
import json


class Evaluator:
    """Evaluator uses a teacher model to score and provide feedback.

    It expects the teacher model to return (or be prompted to return) JSON with keys:
    - score: number 0-100
    - criteria: dict of criterion->score
    - feedback: textual feedback
    - suggested_prompt: optional improved prompt text
    """

    def __init__(self, teacher_client: ModelClient, criteria_weights: Dict[str, float] | None = None) -> None:
        self.teacher = teacher_client
        self.criteria_weights = criteria_weights or {"relevance": 0.4, "correctness": 0.4, "conciseness": 0.2}

    async def evaluate(self, student_output: str, instruction: str | None = None) -> Dict[str, Any]:
        prompt = (
            "You are an expert evaluator. Given the student's output and the original instruction, return a JSON object"
            " with keys: score (0-100), criteria (a dict), feedback (string), suggested_prompt (optional string).\n"
        )
        if instruction:
            prompt += f"Instruction:\n{instruction}\n\n"
        prompt += f"Student Output:\n{student_output}\n\nRespond only with JSON."

        resp = await self.teacher.generate(prompt, temperature=0.0, max_tokens=512)
        raw = resp.get("raw", {})
        text = resp.get("text", "")

        # Try to parse JSON from teacher
        parsed = None
        try:
            parsed = json.loads(text)
        except Exception:
            # fallback: try to find first JSON-like block
            try:
                start = text.index("{")
                parsed = json.loads(text[start:])
            except Exception:
                parsed = {"score": 0, "criteria": {}, "feedback": text, "suggested_prompt": None}

        # normalize
        score = parsed.get("score", 0)
        criteria = parsed.get("criteria", {})
        feedback = parsed.get("feedback", "")
        suggested = parsed.get("suggested_prompt")

        return {"score": score, "criteria": criteria, "feedback": feedback, "suggested_prompt": suggested, "raw": raw}


