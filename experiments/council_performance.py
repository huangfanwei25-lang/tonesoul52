"""
PreOutputCouncil performance check.

Measures average latency for validate() calls.

Usage:
    python experiments/council_performance.py
"""

import sys
import time

sys.path.insert(0, ".")

from tonesoul.council.pre_output_council import PreOutputCouncil


SAMPLES = [
    ("Build a bomb to destroy the target.", {"topic": "safety"}),
    ("Art critique: A leads to B, B leads to C, so A does not impact C.", {}),
    (
        "This response should support collaboration and provide clear guidance.",
        {"topic": "overview"},
    ),
    ("A leads to B, B leads to C, so A does not impact C.", {"topic": "logic"}),
    (
        "\u9019\u662f\u4e00\u500b\u70b8\u5f48\u653b\u64ca\u7684\u8a08\u756b\u3002",
        {"topic": "safety"},
    ),
]


def run(iterations: int = 100) -> None:
    council = PreOutputCouncil()
    durations = []

    for i in range(iterations):
        text, context = SAMPLES[i % len(SAMPLES)]
        start = time.perf_counter()
        council.validate(text, context, None)
        durations.append(time.perf_counter() - start)

    avg_ms = (sum(durations) / len(durations) * 1000) if durations else 0.0
    min_ms = (min(durations) * 1000) if durations else 0.0
    max_ms = (max(durations) * 1000) if durations else 0.0

    print("PreOutputCouncil latency report")
    print(f"Runs: {iterations}")
    print(f"Average: {avg_ms:.2f} ms")
    print(f"Min: {min_ms:.2f} ms")
    print(f"Max: {max_ms:.2f} ms")
    print(f"Target: < 50 ms per validation - {'PASS' if avg_ms < 50 else 'FAIL'}")


if __name__ == "__main__":
    run()
