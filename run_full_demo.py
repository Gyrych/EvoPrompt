"""Run a full automated demo non-interactively using provided keys and base_url.

This script does NOT persist API keys to disk. It will run N rounds and automatically
apply optimizer updates to the prompt store.
"""

import asyncio
from evo_prompt.config import Config
from evo_prompt.prompt_store import PromptStore
from evo_prompt.clients import OpenAICompatibleClient
from evo_prompt.evaluator import Evaluator
from evo_prompt.optimizer import Optimizer
from evo_prompt.cache import Cache
from evo_prompt.workflow import Workflow
import pathlib
import os


async def run_full_demo(api_key: str, base_url: str, prompt_name: str = "sample", input_path: str = "data/input.txt", rounds: int = 3):
    # allow overriding model via env var DEEPSEEK_MODEL, default to deepseek-chat
    import os

    model_name = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    cfg = Config(
        student_api_key=api_key,
        student_base_url=base_url,
        student_model=model_name,
        teacher_api_key=api_key,
        teacher_base_url=base_url,
        teacher_model=model_name,
    )

    store = PromptStore(cfg.prompts_dir)
    student = OpenAICompatibleClient(cfg.student_api_key or "", base_url=cfg.student_base_url, model=cfg.student_model)
    teacher = OpenAICompatibleClient(cfg.teacher_api_key or "", base_url=cfg.teacher_base_url, model=cfg.teacher_model)
    evaluator = Evaluator(teacher)
    optimizer = Optimizer(store, evaluator)
    cache = Cache()
    wf = Workflow(student, teacher, store, evaluator, optimizer, cache)

    # read input
    p = pathlib.Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    input_text = p.read_text(encoding="utf-8")

    for i in range(rounds):
        print(f"\n--- ROUND {i+1} ---")
        res = await wf.run_iteration(prompt_name, input_text, use_teacher=True)
        score = res.get("evaluation", {}).get("score")
        print(f"Evaluation score: {score}")
        proposed = res.get("proposed", {})
        summary = proposed.get("change_summary")
        new_text = proposed.get("new_prompt_text")
        print("Proposed change:", summary)
        if new_text:
            # apply update automatically
            store.add_or_update_prompt(prompt_name, new_text, author="auto_optimizer", reason=f"auto-round-{i+1}")
            print("Applied new prompt version.")

    # close clients
    student.close()
    teacher.close()


if __name__ == "__main__":
    # parameters — replace API_KEY and BASE_URL as needed
    API_KEY = os.environ.get("DEEPSEEK_API_KEY") or ""
    BASE_URL = os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"
    if not API_KEY:
        raise SystemExit("DEEPSEEK_API_KEY environment variable not set. Set it or modify the script to include the key.")

    # ensure data dir exists
    pathlib.Path("data").mkdir(exist_ok=True)
    # default input file
    input_file = "data/input.txt"
    # create a default input if missing
    if not pathlib.Path(input_file).exists():
        pathlib.Path(input_file).write_text("这是用于演示的示例文章内容。\n请根据 sample 提示词生成摘要。", encoding="utf-8")

    asyncio.run(run_full_demo(API_KEY, BASE_URL, prompt_name="sample", input_path=input_file, rounds=3))


