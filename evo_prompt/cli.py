from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from .config import interactive_config_prompt, Config
from .prompt_store import PromptStore
from .clients import OpenAICompatibleClient
from .evaluator import Evaluator
from .optimizer import Optimizer
from .cache import Cache
from .workflow import Workflow


async def run_once(config: Config, prompt_name: str, input_text: str) -> None:
    student = OpenAICompatibleClient(config.student_api_key or "", base_url=config.student_base_url, model=config.student_model)
    teacher = OpenAICompatibleClient(config.teacher_api_key or "", base_url=config.teacher_base_url, model=config.teacher_model)
    store = PromptStore(config.prompts_dir)
    evaluator = Evaluator(teacher)
    optimizer = Optimizer(store, evaluator)
    cache = Cache()
    wf = Workflow(student, teacher, store, evaluator, optimizer, cache)

    result = await wf.run_iteration(prompt_name, input_text, use_teacher=True)
    print("Evaluation score:", result.get("evaluation", {}).get("score"))
    print("Suggested prompt change summary:", result.get("proposed", {}).get("change_summary"))


def main() -> None:
    parser = argparse.ArgumentParser("evo-prompt")
    parser.add_argument("--init", action="store_true", help="Run interactive config and create sample files")
    parser.add_argument("--prompt", type=str, help="Prompt name to run")
    parser.add_argument("--input", type=str, help="Input text or path to file")

    args = parser.parse_args()
    if args.init:
        cfg = interactive_config_prompt()
        print("Config collected. Run with --prompt and --input to execute an iteration.")
        return

    if not args.prompt or not args.input:
        parser.print_help()
        return

    input_text = args.input
    p = Path(input_text)
    if p.exists():
        input_text = p.read_text(encoding="utf-8")

    cfg = interactive_config_prompt()
    asyncio.run(run_once(cfg, args.prompt, input_text))


if __name__ == "__main__":
    main()


