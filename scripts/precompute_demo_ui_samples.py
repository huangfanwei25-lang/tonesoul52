"""Precompute Council verdicts for the Demo UI v0 sample drafts mode.

This script reads the smoke corpora (diverse + adversarial), runs
``PreOutputCouncil.validate()`` on each draft, and writes the full verdict
(plus original corpus metadata) to ``docs/demo_ui/data/sample_verdicts.json``.

Why this exists (2026-04-19, Claude Code):
    Demo UI v0 Mode D (Sample drafts) must work offline on GitHub Pages —
    no backend is available at render time. Precomputing verdicts lets the
    static page show "real Council output vs. our pre-labeled suggested_signal",
    which is the single most informative artifact we have for visitors who
    cannot (and will not) spin up the gateway themselves.

    The output JSON is committed so the UI can fetch it as a static asset.
    Re-run this script whenever the corpora or the Council change.

Usage:
    python scripts/precompute_demo_ui_samples.py

Inputs (relative to repo root):
    tests/fixtures/outcome_smoke/corpus_2026-04-19.jsonl
    tests/fixtures/outcome_smoke/adversarial_corpus_2026-04-19.jsonl

Output:
    docs/demo_ui/samples/sample_verdicts.json
    (The directory is named ``samples`` rather than ``data`` because the repo's
    .gitignore blocks ``data/``.)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tonesoul.council.pre_output_council import PreOutputCouncil  # noqa: E402

CORPUS_FILES = [
    ROOT / "tests" / "fixtures" / "outcome_smoke" / "corpus_2026-04-19.jsonl",
    ROOT / "tests" / "fixtures" / "outcome_smoke" / "adversarial_corpus_2026-04-19.jsonl",
]

OUTPUT_PATH = ROOT / "docs" / "demo_ui" / "samples" / "sample_verdicts.json"


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        entries.append(json.loads(stripped))
    return entries


def _verdict_to_dict(entry: Dict[str, Any]) -> Dict[str, Any]:
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output=entry["draft_output"],
        context={"language": "en"},
        user_intent=entry.get("user_intent"),
        auto_record_self_memory=False,
    )
    return verdict.to_dict()


def main() -> None:
    samples: List[Dict[str, Any]] = []
    for corpus_path in CORPUS_FILES:
        if not corpus_path.exists():
            print(f"[skip] missing corpus: {corpus_path}", file=sys.stderr)
            continue
        for entry in _read_jsonl(corpus_path):
            verdict_dict = _verdict_to_dict(entry)
            samples.append(
                {
                    "draft_output": entry["draft_output"],
                    "user_intent": entry.get("user_intent"),
                    "category": entry.get("category"),
                    "harm_category": entry.get("harm_category"),
                    "why_this_is_adversarial": entry.get("why_this_is_adversarial"),
                    "suggested_signal": entry.get("suggested_signal"),
                    "harm_description": entry.get("harm_description"),
                    "verdict": verdict_dict,
                }
            )
        print(f"[ok] processed {corpus_path.name} ({sum(1 for s in samples)} running total)")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {
            "generated_by": "scripts/precompute_demo_ui_samples.py",
            "sample_count": len(samples),
            "samples": samples,
        },
        indent=2,
        ensure_ascii=False,
    )
    # Force LF line endings so the pre-commit hook accepts the file on Windows.
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
        fh.write("\n")
    print(f"[done] wrote {len(samples)} samples -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
