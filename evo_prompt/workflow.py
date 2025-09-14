from __future__ import annotations

from .clients import ModelClient
from .prompt_store import PromptStore
from .evaluator import Evaluator
from .optimizer import Optimizer
from .cache import Cache
from .logger import log_response, setup_file_logger
from pathlib import Path
from typing import Dict, Any
import uuid
import json


class Workflow:
    def __init__(
        self,
        student_client: ModelClient,
        teacher_client: ModelClient,
        prompt_store: PromptStore,
        evaluator: Evaluator,
        optimizer: Optimizer,
        cache: Cache | None = None,
        logs_dir: str | Path = "logs",
        results_dir: str | Path = "results",
    ) -> None:
        self.student = student_client
        self.teacher = teacher_client
        self.prompt_store = prompt_store
        self.evaluator = evaluator
        self.optimizer = optimizer
        self.cache = cache or Cache()
        self.logs_dir = Path(logs_dir)
        self.results_dir = Path(results_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logger = setup_file_logger(self.logs_dir)

    async def run_iteration(self, prompt_name: str, input_context: str, use_teacher: bool = True) -> Dict[str, Any]:
        prompt_obj = self.prompt_store.get_prompt(prompt_name)
        if not prompt_obj:
            raise ValueError(f"Prompt not found: {prompt_name}")

        prompt_text = prompt_obj.get("text", "") + "\n\n" + input_context

        params = {"temperature": 0.0}
        cached = self.cache.get(prompt_text, getattr(self.student, "model", "unknown"), params)
        if cached:
            student_resp = cached
            self.logger.info("Cache hit for student generation")
        else:
            student_resp = await self.student.generate(prompt_text, **params)
            self.cache.set(prompt_text, getattr(self.student, "model", "unknown"), params, student_resp)

        # log student response
        resp_id = uuid.uuid4().hex
        log_response(self.logs_dir, f"{resp_id}_student.jsonl", {"prompt_name": prompt_name, "prompt": prompt_text, "response": student_resp})

        # evaluate
        eval_result = None
        if use_teacher:
            eval_result = await self.evaluator.evaluate(student_resp.get("text", ""), instruction=prompt_text)
            log_response(self.logs_dir, f"{resp_id}_evaluation.jsonl", {"eval": eval_result})

        # propose improvement
        proposed = await self.optimizer.propose_improvement(prompt_name, student_resp.get("text", ""), eval_result or {})

        out = {
            "prompt_name": prompt_name,
            "student_response": student_resp,
            "evaluation": eval_result,
            "proposed": proposed,
        }

        # save results
        out_path = self.results_dir / f"{resp_id}_result.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

        return out


