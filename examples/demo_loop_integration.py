"""Demo: conversational loop integration with UnifiedPipeline."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tonesoul.unified_pipeline import UnifiedPipeline


def _append_history(history: list[dict[str, object]], user_message: str, response: str) -> None:
    history.append({"role": "user", "parts": [user_message]})
    history.append({"role": "model", "parts": [response]})


def demo_pipeline_loop() -> None:
    print("=" * 70)
    print("  ToneSoul UnifiedPipeline Loop Demo")
    print("=" * 70)

    pipeline = UnifiedPipeline(mirror_enabled=False)
    history: list[dict[str, object]] = []
    prompts = [
        "Summarize a cautious rollout plan for a new feature.",
        "Refine it with one rollback checkpoint and an accountability note.",
    ]

    for index, prompt in enumerate(prompts, start=1):
        print(f"\n[{index}] User: {prompt}")
        result = pipeline.process(user_message=prompt, history=history)

        print(f"Response: {result.response}")
        print(f"Council verdict: {result.council_verdict.get('verdict')}")
        print(f"Dispatch route: {result.dispatch_trace.get('route')}")

        _append_history(history, prompt, result.response)

    print("\nDemo complete.")


if __name__ == "__main__":
    demo_pipeline_loop()
