"""Corrective-recall characterization harness.

This lights up and measures the *parked* error-vector-cued corrective recall
(`tonesoul/memory/hippocampus.py`, RFC-012: recall / recall_corrective are
tested-but-NO-live-caller, the class is never instantiated at runtime). It measures
STRUCTURE only — it does not judge production recall quality, relevance, or whether
recalled memory improves a decision. There is no relevance oracle here; the planted
item is a test coordinate.

What it measures, structurally:
  - inert_by_default      : a fresh Hippocampus with no store recalls nothing
  - noop_on_zero_vector   : intended == generated -> ~zero error vector (the no-rewrite case)
  - recall_fires_when_lit : with a controlled store + a real discrepancy, recall returns items
  - returns_planted_item  : the planted "corrective" memory (ground truth) is surfaced

Hermetic: it exercises the REAL recall logic with a deterministic fake vector index
(no FAISS, no embedder, no reading the gitignored `memory_base`). The public report omits
raw fixture text and carries non-canonical provenance. No runtime behavior is changed —
the harness calls the parked methods directly; nothing is wired into the pipeline.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.memory.hippocampus import Hippocampus  # noqa: E402

DEFAULT_REPORT_PATH = Path("docs/status/corrective_recall_characterization_latest.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("docs/status/corrective_recall_characterization_latest.md")
DEFAULT_SOURCE_COMMAND = "python tools/eval/corrective_recall_characterization.py --write-report"

EMBED_DIM = 16
ZERO_VECTOR_EPS = 1e-6  # matches the unified_pipeline corrective-recall skip threshold

# Claims this harness must never be read as making.
FORBIDDEN_PUBLIC_CLAIM_IDS = (
    "corrective_recall_is_live_in_runtime",
    "measures_production_recall_quality",
    "is_a_relevance_oracle",
    "proves_memory_improves_decisions",
)

STRUCTURAL_SIGNALS = (
    "inert_by_default",
    "noop_on_zero_vector",
    "recall_fires_when_lit",
    "returns_planted_item",
)


def _fake_embed(text: str) -> np.ndarray:
    """Deterministic text->vector (sha256-seeded). Not a real embedder — a stable
    test coordinate so the harness needs no model and runs identically everywhere."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    raw = np.frombuffer(
        (digest * ((EMBED_DIM // len(digest)) + 1))[: EMBED_DIM * 4], dtype=np.uint8
    )
    vec = raw[:EMBED_DIM].astype(np.float32)
    norm = float(np.linalg.norm(vec))
    return vec / norm if norm > 0 else vec


class _FakeIndex:
    """Deterministic in-memory nearest-neighbour stand-in for a FAISS index.

    Implements only the ``.search(query, k)`` shape `Hippocampus.search_vectors` uses.
    It fakes the FAISS/embedding backend so the REAL recall fusion logic can be exercised
    without the optional dependency or the gitignored store."""

    def __init__(self, vectors: np.ndarray) -> None:
        self._vectors = np.asarray(vectors, dtype=np.float32)

    def search(self, query: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
        q = np.asarray(query, dtype=np.float32)[0]
        if self._vectors.size == 0:
            return np.zeros((1, 0), dtype=np.float32), np.full((1, 0), -1, dtype=np.int64)
        dists = np.linalg.norm(self._vectors - q, axis=1)
        order = np.argsort(dists)[:k]
        # Hippocampus sorts results DESC by score, so return higher-is-closer scores.
        scores = (1.0 / (1.0 + dists[order])).astype(np.float32)
        return scores.reshape(1, -1), order.reshape(1, -1).astype(np.int64)


@dataclass(frozen=True)
class ExpectedSignals:
    inert_by_default: bool = False
    noop_on_zero_vector: bool = False
    recall_fires_when_lit: bool = False
    returns_planted_item: bool = False

    def to_public_dict(self) -> dict[str, bool]:
        return {
            "inert_by_default": self.inert_by_default,
            "noop_on_zero_vector": self.noop_on_zero_vector,
            "recall_fires_when_lit": self.recall_fires_when_lit,
            "returns_planted_item": self.returns_planted_item,
        }


@dataclass(frozen=True)
class Fixture:
    """A sanitized corrective-recall scenario.

    ``intended_text``/``generated_text`` are abstract category templates; their raw text is
    used only in-memory and omitted from the public report."""

    fixture_id: str
    category: str
    split: str
    mode: str  # "inert_default" | "noop_zero_vector" | "lit_discrepancy"
    intended_text: str
    generated_text: str
    expected: ExpectedSignals
    planted_item_id: str = "planted_corrective_memory"


@dataclass(frozen=True)
class DegradationEvent:
    gate: str
    tier: str
    error_type: str
    message: str

    def to_public_dict(self) -> dict[str, str]:
        return {
            "gate": self.gate,
            "tier": self.tier,
            "error_type": self.error_type,
            "message": self.message[:200],
        }


DEFAULT_FIXTURES: tuple[Fixture, ...] = (
    Fixture(
        fixture_id="inert_default_seen_001",
        category="inert_default",
        split="seen",
        mode="inert_default",
        intended_text="A measured, bounded answer to the request.",
        generated_text="An over-confident answer that drifted from the request.",
        expected=ExpectedSignals(inert_by_default=True),
    ),
    Fixture(
        fixture_id="noop_zero_vector_seen_001",
        category="noop_zero_vector",
        split="seen",
        mode="noop_zero_vector",
        intended_text="Identical intended and generated text (no rewrite happened).",
        generated_text="Identical intended and generated text (no rewrite happened).",
        expected=ExpectedSignals(noop_on_zero_vector=True),
    ),
    Fixture(
        fixture_id="lit_discrepancy_seen_001",
        category="lit_discrepancy",
        split="seen",
        mode="lit_discrepancy",
        intended_text="A bounded answer that stays inside the claim boundary.",
        generated_text="An answer that overclaimed certainty the request did not warrant.",
        expected=ExpectedSignals(recall_fires_when_lit=True, returns_planted_item=True),
    ),
    Fixture(
        fixture_id="lit_discrepancy_novel_001",
        category="lit_discrepancy",
        split="novel",
        mode="lit_discrepancy",
        intended_text="Surface the disagreement and keep both options visible.",
        generated_text="Smoothed the disagreement into one confident recommendation.",
        expected=ExpectedSignals(recall_fires_when_lit=True, returns_planted_item=True),
    ),
)


def _new_hippocampus_no_store() -> Hippocampus:
    """A fresh Hippocampus with no store (the default runtime state). The _load_db banner
    is suppressed so it does not pollute stdout for callers/tests."""
    with contextlib.redirect_stdout(io.StringIO()):
        return Hippocampus(db_path=str(REPO_ROOT / "_nonexistent_memory_base_for_characterization"))


def _lit_hippocampus(b_vec: np.ndarray, planted_id: str) -> Hippocampus:
    """A controlled, in-memory Hippocampus: a fake vector index whose closest item is the
    planted 'corrective' memory (vector == the correction direction), plus distractors."""
    hippo = _new_hippocampus_no_store()
    distractor_a = _fake_embed("unrelated note about scheduling")
    distractor_b = _fake_embed("unrelated note about formatting")
    vectors = np.stack([np.asarray(b_vec, dtype=np.float32), distractor_a, distractor_b])
    now = datetime.now(timezone.utc).isoformat()
    hippo.index = _FakeIndex(vectors)
    hippo.metadata = [
        {
            "id": planted_id,
            "content": "corrective exemplar",
            "source_file": "fixture",
            "ingested_at": now,
        },
        {
            "id": "distractor_a",
            "content": "scheduling",
            "source_file": "fixture",
            "ingested_at": now,
        },
        {
            "id": "distractor_b",
            "content": "formatting",
            "source_file": "fixture",
            "ingested_at": now,
        },
    ]
    hippo.bm25 = None  # vector-only; the corrective path is vector-driven
    return hippo


def evaluate_fixture(fixture: Fixture) -> dict[str, Any]:
    intended = _fake_embed(fixture.intended_text)
    generated = _fake_embed(fixture.generated_text)
    b_vec = Hippocampus.compute_error_vector(intended, generated)
    b_norm = float(np.linalg.norm(b_vec))

    observed = {
        "inert_by_default": False,
        "noop_on_zero_vector": False,
        "recall_fires_when_lit": False,
        "returns_planted_item": False,
        "error_vector_norm": round(b_norm, 6),
        "recall_hit_count": 0,
    }
    degradation_events: list[DegradationEvent] = []

    try:
        if fixture.mode == "inert_default":
            hippo = _new_hippocampus_no_store()
            results = hippo.recall(query_text="self-correction", query_vector=b_vec, top_k=5)
            observed["recall_hit_count"] = len(results)
            observed["inert_by_default"] = len(results) == 0
        elif fixture.mode == "noop_zero_vector":
            # intended == generated -> error vector is ~zero -> the no-rewrite no-op the
            # pipeline skips (norm <= ZERO_VECTOR_EPS).
            observed["noop_on_zero_vector"] = b_norm <= ZERO_VECTOR_EPS
        elif fixture.mode == "lit_discrepancy":
            hippo = _lit_hippocampus(b_vec, fixture.planted_item_id)
            results = hippo.recall(query_text="self-correction", query_vector=b_vec, top_k=3)
            observed["recall_hit_count"] = len(results)
            observed["recall_fires_when_lit"] = len(results) > 0
            observed["returns_planted_item"] = bool(
                results and results[0].doc_id == fixture.planted_item_id
            )
    except Exception as exc:  # fail-soft: a parked-method failure is a required-gate event
        degradation_events.append(
            DegradationEvent(
                gate="hippocampus_corrective_recall",
                tier="required",
                error_type=type(exc).__name__,
                message=str(exc),
            )
        )

    return {
        "fixture_id": fixture.fixture_id,
        "category": fixture.category,
        "split": fixture.split,
        "mode": fixture.mode,
        "expected": fixture.expected.to_public_dict(),
        "observed": observed,
        "degradation_events": [e.to_public_dict() for e in degradation_events],
    }


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def build_report(
    *, updated_at: str, source_command: str = DEFAULT_SOURCE_COMMAND
) -> dict[str, Any]:
    cases = [evaluate_fixture(f) for f in DEFAULT_FIXTURES]

    expected_signal_total = 0
    observed_signal_total = 0
    for case in cases:
        for signal in STRUCTURAL_SIGNALS:
            if case["expected"].get(signal):
                expected_signal_total += 1
                if case["observed"].get(signal):
                    observed_signal_total += 1

    lit_cases = [c for c in cases if c["mode"] == "lit_discrepancy"]
    inert_cases = [c for c in cases if c["mode"] == "inert_default"]
    noop_cases = [c for c in cases if c["mode"] == "noop_zero_vector"]

    metrics = {
        "fixture_count": len(cases),
        "structural_signal_expected_count": expected_signal_total,
        "structural_signal_observed_count": observed_signal_total,
        "structural_signal_rate": _ratio(observed_signal_total, expected_signal_total),
        "inert_by_default_rate": _ratio(
            sum(1 for c in inert_cases if c["observed"]["inert_by_default"]), len(inert_cases)
        ),
        "noop_on_zero_vector_rate": _ratio(
            sum(1 for c in noop_cases if c["observed"]["noop_on_zero_vector"]), len(noop_cases)
        ),
        "recall_fires_when_lit_rate": _ratio(
            sum(1 for c in lit_cases if c["observed"]["recall_fires_when_lit"]), len(lit_cases)
        ),
        "returns_planted_item_rate": _ratio(
            sum(1 for c in lit_cases if c["observed"]["returns_planted_item"]), len(lit_cases)
        ),
        "degradation_event_count": sum(len(c["degradation_events"]) for c in cases),
    }

    headline = (
        f"Under this fixture set, corrective recall is inert by default "
        f"({metrics['inert_by_default_rate']}), is a no-op on a zero error vector "
        f"({metrics['noop_on_zero_vector_rate']}), and its recall logic fires + returns the "
        f"planted item only when lit with a controlled store + a real discrepancy "
        f"({metrics['returns_planted_item_rate']})."
    )

    return {
        "schema_version": "corrective-recall-characterization.v1",
        "doc_provenance": {
            "generated": True,
            "canonical": False,
            "source_command": source_command,
            "updated_at": updated_at,
        },
        "generated_at": updated_at,
        "experiment": {
            "name": "corrective_recall_characterization",
            "not_a_runtime_claim": True,
            "not_a_relevance_oracle": True,
            "measures": "structural recall behaviour of the parked error-vector path, with a "
            "controlled fake index; not production recall quality",
            "forbidden_public_claim_ids": list(FORBIDDEN_PUBLIC_CLAIM_IDS),
            "raw_fixture_text_in_public_report": False,
            "notes": [
                "The parked recall/recall_corrective methods are exercised directly; nothing is "
                "wired into the runtime pipeline.",
                "A deterministic fake vector index stands in for FAISS + the gitignored "
                "memory_base; production recall needs a real index and a populated store.",
                "The planted item is a test coordinate (ground truth), not a real relevance "
                "judgement.",
                "Inert-by-default and no-op-on-zero-vector are the honest default-runtime "
                "findings; the lit case shows only that the recall logic works given a store "
                "and a discrepancy.",
            ],
        },
        "allowed_conclusion": headline,
        "metrics": metrics,
        "cases": cases,
    }


def render_markdown(report: dict[str, Any]) -> str:
    m = report["metrics"]
    lines: list[str] = []
    lines.append("# Corrective-Recall Characterization")
    lines.append("")
    lines.append(f"generated: {report['doc_provenance']['generated']}")
    lines.append(f"canonical: {report['doc_provenance']['canonical']}")
    lines.append(f"updated_at: {report['doc_provenance']['updated_at']}")
    lines.append("")
    lines.append(
        "This status artifact is non-canonical and makes no runtime or relevance claim. "
        "It measures the parked error-vector corrective-recall logic with a controlled fake "
        "index (no FAISS, no model, no gitignored store)."
    )
    lines.append("")
    lines.append("## Allowed conclusion")
    lines.append("")
    lines.append(report["allowed_conclusion"])
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---|")
    for key in (
        "fixture_count",
        "inert_by_default_rate",
        "noop_on_zero_vector_rate",
        "recall_fires_when_lit_rate",
        "returns_planted_item_rate",
        "structural_signal_rate",
        "degradation_event_count",
    ):
        lines.append(f"| {key} | {m[key]} |")
    lines.append("")
    lines.append("## Cases")
    lines.append("")
    lines.append("| fixture_id | mode | split | signals observed |")
    lines.append("|---|---|---|---|")
    for case in report["cases"]:
        observed = [s for s in STRUCTURAL_SIGNALS if case["observed"].get(s)]
        lines.append(
            f"| {case['fixture_id']} | {case['mode']} | {case['split']} | "
            f"{', '.join(observed) or '(none)'} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-markdown", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_REPORT_PATH)
    parser.add_argument("--updated-at", default=None)
    parser.add_argument("--source-command", default=DEFAULT_SOURCE_COMMAND)
    args = parser.parse_args(argv)

    updated_at = args.updated_at or datetime.now(timezone.utc).isoformat()
    report = build_report(updated_at=updated_at, source_command=args.source_command)

    if args.write_report:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    if args.write_markdown:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(render_markdown(report), encoding="utf-8")

    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
