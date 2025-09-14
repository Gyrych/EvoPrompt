import asyncio
from evo_prompt.prompt_store import PromptStore
from evo_prompt.mock_clients import MockClient
from evo_prompt.evaluator import Evaluator
from evo_prompt.optimizer import Optimizer
from evo_prompt.cache import Cache
from evo_prompt.workflow import Workflow


async def run_smoke():
    store = PromptStore("prompts")
    student = MockClient(name="student", text="Student output: key points A, B, C.")
    teacher = MockClient(name="teacher", text='{"score": 75, "criteria": {"relevance":80, "correctness":70, "conciseness":75}, "feedback":"Good summary.", "suggested_prompt": null}')
    evaluator = Evaluator(teacher)
    optimizer = Optimizer(store, evaluator)
    cache = Cache(".cache", ttl_seconds=1)
    wf = Workflow(student, teacher, store, evaluator, optimizer, cache)

    res = await wf.run_iteration("sample", "Here is a short article to summarize.")
    print("Smoke test result score:", res.get("evaluation", {}).get("score"))
    print("Proposed change:", res.get("proposed", {}).get("change_summary"))


if __name__ == "__main__":
    asyncio.run(run_smoke())


