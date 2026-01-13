from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .summary_generator import resolve_language
from .types import CouncilVerdict


VERDICT_LABELS = {
    "approve": ("approved", "\u901a\u904e"),
    "refine": ("needs refinement", "\u9700\u8981\u6539\u9032"),
    "declare_stance": ("needs a declared stance", "\u9700\u8981\u7acb\u5834\u8868\u660e"),
    "block": ("blocked", "\u5df2\u5c01\u9396"),
}


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_journal_path() -> Path:
    return _workspace_root() / "memory" / "self_journal.jsonl"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _label_for_verdict(verdict_value: str, language: str) -> str:
    label = VERDICT_LABELS.get(verdict_value)
    if not label:
        return verdict_value
    return label[0] if language == "en" else label[1]


def _build_self_statement(
    verdict: CouncilVerdict,
    identity: str,
    language: str,
) -> str:
    verdict_value = verdict.verdict.value
    verdict_label = _label_for_verdict(verdict_value, language)
    reason = verdict.human_summary or verdict.summary or ""

    if language == "zh":
        statement = f"\u6211\u662f{identity}\u3002\u6211\u525b\u525b\u5b8c\u6210\u4e00\u6b21\u5224\u65b7\uff0c\u7d50\u8ad6\u662f{verdict_label}\u3002"
        if reason:
            statement += f"\u539f\u56e0\uff1a{reason}"
        return statement

    statement = f"I am {identity}. I just completed a review and decided {verdict_label}."
    if reason:
        statement += f" Reason: {reason}"
    return statement


def record_self_memory(
    verdict: CouncilVerdict,
    context: Optional[dict] = None,
    path: Optional[os.PathLike] = None,
    include_transcript: bool = True,
) -> dict:
    context = context or {}
    language = resolve_language(context)
    identity = str(context.get("self_identity", "ToneSoul"))
    divergence = verdict.divergence_analysis or {}

    entry = {
        "timestamp": _iso_now(),
        "identity": identity,
        "verdict": verdict.verdict.value,
        "human_summary": verdict.human_summary,
        "core_divergence": divergence.get("core_divergence"),
        "recommended_action": divergence.get("recommended_action"),
        "self_statement": _build_self_statement(verdict, identity, language),
    }
    if include_transcript:
        entry["transcript"] = verdict.transcript or {}

    journal_path = Path(path) if path else _default_journal_path()
    os.makedirs(journal_path.parent, exist_ok=True)
    with open(journal_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def load_recent_memory(
    limit: int = 3,
    path: Optional[os.PathLike] = None,
) -> List[dict]:
    journal_path = Path(path) if path else _default_journal_path()
    if not journal_path.exists():
        return []
    if limit <= 0:
        return []

    with open(journal_path, "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]

    entries: List[dict] = []
    for line in lines[-limit:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries
