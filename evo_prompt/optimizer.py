from __future__ import annotations

from typing import Dict, Any
from .prompt_store import PromptStore
from .evaluator import Evaluator


class Optimizer:
    def __init__(self, prompt_store: PromptStore, evaluator: Evaluator) -> None:
        self.prompt_store = prompt_store
        self.evaluator = evaluator

    async def propose_improvement(self, prompt_name: str, student_output: str, eval_feedback: Dict[str, Any]) -> Dict[str, Any]:
        # If teacher suggested prompt is present, prefer it
        suggested = eval_feedback.get("suggested_prompt")
        if suggested:
            return {"new_prompt_text": suggested, "change_summary": "Adopted teacher suggested prompt.", "diff": {}}

        # Otherwise, make a conservative improvement: append a clarifying instruction
        current = self.prompt_store.get_prompt(prompt_name)
        if not current:
            return {"new_prompt_text": None, "change_summary": "Prompt not found.", "diff": {}}

        base_text = current.get("text", "")
        addition = "\nPlease be more specific about structure, include examples and required format."
        new_text = base_text + addition

        diff = {"added": addition}
        return {"new_prompt_text": new_text, "change_summary": "Appended clarifying constraints.", "diff": diff}


