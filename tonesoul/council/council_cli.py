"""
Council CLI — Node.js-callable entry point for ToneSoul Council deliberation.

Usage:
    python -m tonesoul.council.council_cli --draft "agent output text" --intent "user goal" --mode local

Output (stdout): JSON with verdict, divergence_analysis, quality band.

This module is designed to be invoked by Elisa's `councilBridge.ts` via
`child_process.execFile`. It writes only valid JSON to stdout so the
TypeScript side can parse the result reliably.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any, Dict

# Suppress all logging to stderr so stdout stays clean JSON
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

_VALID_MODES = {"local", "hybrid", "rules", "full_llm"}
_FALLBACK_REASON_MARKERS = (
    "[fallback_to_rules]",
    "vtp philosopher fallback to rules",
    "fallback to rules",
)


def _build_council_request(
    draft: str,
    intent: str,
    mode: str,
    visual_context: str = "",
) -> Dict[str, Any]:
    """Build kwargs suitable for CouncilRuntime.deliberate()."""
    from .model_registry import get_council_config
    from .runtime import CouncilRequest

    config = get_council_config(mode=mode)
    context_dict = {"source": "elisa_bridge", "council_mode_override": mode}
    if visual_context:
        context_dict["visual_context"] = visual_context

    return CouncilRequest(
        draft_output=draft,
        context=context_dict,
        user_intent=intent,
        perspective_config=config,
        coherence_threshold=0.6,
        block_threshold=0.3,
    )


def _fallback_triggered_from_votes(votes: Any) -> bool:
    if not isinstance(votes, list):
        return False
    for vote in votes:
        reasoning = getattr(vote, "reasoning", "")
        if not isinstance(reasoning, str):
            continue
        normalized = reasoning.lower()
        if any(marker in normalized for marker in _FALLBACK_REASON_MARKERS):
            return True
    return False


def _run_council(draft: str, intent: str, mode: str, visual_context: str = "") -> Dict[str, Any]:
    """Execute council deliberation and return a serialisable result dict."""
    from .runtime import CouncilRuntime

    runtime = CouncilRuntime()
    request = _build_council_request(draft, intent, mode, visual_context)
    verdict = runtime.deliberate(request)
    fallback_triggered = _fallback_triggered_from_votes(getattr(verdict, "votes", []))

    # Extract quality from divergence_analysis
    divergence = verdict.divergence_analysis or {}
    quality = divergence.get("quality", {})
    quality_score = quality.get("score", 0.0) if isinstance(quality, dict) else 0.0
    quality_band = quality.get("band", "low") if isinstance(quality, dict) else "low"

    # Compute a tension-like metric from divergence
    # More objections + lower confidence = higher tension
    n_obj = len(divergence.get("object", []))
    n_con = len(divergence.get("concern", []))
    n_agr = len(divergence.get("agree", []))
    total = max(n_obj + n_con + n_agr, 1)
    tension = round((n_obj * 1.0 + n_con * 0.5) / total, 3)

    return {
        "verdict": (
            verdict.verdict.value if hasattr(verdict.verdict, "value") else str(verdict.verdict)
        ),
        "summary": verdict.summary or "",
        "tension": tension,
        "quality_band": quality_band,
        "quality_score": round(float(quality_score), 3),
        "fallback_triggered": fallback_triggered,
        "divergence": {
            "agree": divergence.get("agree", []),
            "concern": divergence.get("concern", []),
            "object": divergence.get("object", []),
            "core_divergence": divergence.get("core_divergence", ""),
            "recommended_action": divergence.get("recommended_action", ""),
            "quality": {
                "score": round(float(quality_score), 3),
                "band": quality_band,
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ToneSoul Council CLI for Elisa bridge",
    )
    parser.add_argument(
        "--draft",
        required=True,
        help="The agent output text to evaluate",
    )
    parser.add_argument(
        "--intent",
        default="",
        help="The user's original intent / goal",
    )
    parser.add_argument(
        "--mode",
        default="local",
        choices=sorted(_VALID_MODES),
        help="Council configuration mode (default: local)",
    )
    parser.add_argument(
        "--visual-context",
        default="",
        help="Optional Mermaid diagram representing the workspace state",
    )
    args = parser.parse_args()

    try:
        result = _run_council(args.draft, args.intent, args.mode, args.visual_context)
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    except Exception as exc:
        # Even on error, output valid JSON so the TypeScript side can parse it
        error_result = {
            "verdict": "CONCERN",
            "summary": f"Council CLI error: {str(exc)[:200]}",
            "tension": 0.5,
            "quality_band": "low",
            "quality_score": 0.0,
            "fallback_triggered": False,
            "divergence": {
                "agree": [],
                "concern": [],
                "object": [],
                "core_divergence": f"Error: {str(exc)[:100]}",
                "recommended_action": "Manual review recommended",
                "quality": {"score": 0.0, "band": "low"},
            },
        }
        json.dump(error_result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
