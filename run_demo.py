"""Simple demo script to run one or more iterations of the EvoPrompt workflow."""

import asyncio
from evo_prompt.config import interactive_config_prompt, Config
from evo_prompt.prompt_store import PromptStore
from evo_prompt.clients import OpenAICompatibleClient
from evo_prompt.evaluator import Evaluator
from evo_prompt.optimizer import Optimizer
from evo_prompt.cache import Cache
from evo_prompt.workflow import Workflow


async def demo_loop(cfg: Config, prompt_name: str, input_text: str, rounds: int = 3):
    student = OpenAICompatibleClient(cfg.student_api_key or "", base_url=cfg.student_base_url, model=cfg.student_model)
    teacher = OpenAICompatibleClient(cfg.teacher_api_key or "", base_url=cfg.teacher_base_url, model=cfg.teacher_model)
    store = PromptStore(cfg.prompts_dir)
    evaluator = Evaluator(teacher)
    optimizer = Optimizer(store, evaluator)
    cache = Cache()
    wf = Workflow(student, teacher, store, evaluator, optimizer, cache)

    for i in range(rounds):
        print(f"\n=== Iteration {i+1} ===")
        res = await wf.run_iteration(prompt_name, input_text, use_teacher=True)
        score = res.get("evaluation", {}).get("score")
        print(f"Score: {score}")
        proposed = res.get("proposed", {})
        print("Proposed change:", proposed.get("change_summary"))
        apply_update = input("Apply proposed prompt update? (y/n/stop): ")
        if apply_update.strip().lower() == "y":
            new_text = proposed.get("new_prompt_text")
            if new_text:
                store.add_or_update_prompt(prompt_name, new_text, author="optimizer")
                print("Prompt updated.")
        elif apply_update.strip().lower() == "stop":
            break


def main():
    cfg = interactive_config_prompt()
    prompt_name = input("Prompt name to run [sample]: ") or "sample"
    input_text = input("Input text (or path to file): ")
    import pathlib

    p = pathlib.Path(input_text)
    if p.exists():
        input_text = p.read_text(encoding="utf-8")

    rounds = int(input("Number of rounds to run [3]: ") or 3)
    asyncio.run(demo_loop(cfg, prompt_name, input_text, rounds=rounds))


if __name__ == "__main__":
    main()


