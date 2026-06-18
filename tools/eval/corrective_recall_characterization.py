"""Corrective-recall characterization harness.

This lights up and measures the *parked* error-vector-cued corrective recall
(`tonesoul/memory/hippocampus.py`, RFC-012: recall / recall_corrective are
tested-but-NO-live-caller, the class is never instantiated at runtime). It measures
STRUCTURE only — it does not judge production recall quality, relevance, or whether
recalled memory improves a decision. There is no relevance oracle here; the planted
item is a test coordinate.

What it measures, structurally (signal level in parentheses):
  - inert_by_default      (recall): a fresh Hippocampus with no store recalls nothing
  - noop_on_zero_vector   (guard) : intended == generated -> ~zero error vector, so the
                                    pre-recall guard skips (the no-rewrite case). recall is
                                    NOT called here. This is the discrepancy gate, located in
                                    the guard, not inside recall.
  - recall_fires_when_lit (recall): given a POPULATED store, recall returns items. The only
                                    firing precondition this demonstrates for recall itself is
                                    a store, not a discrepancy (recall fires on a zero vector too).
  - returns_planted_item  (recall): the planted "corrective" memory is present in the SELECTED
                                    result subset (membership, not a top-1 / relevance claim).
                                    Non-degenerate: top_k < store size (recall must select) and
                                    the planted vector is offset from the query (not a distance-0
                                    identity artifact).

Hermetic: it exercises the REAL corrective-recall path — the named `recall_corrective` method
(which composes compute_error_vector + recall) is called directly — with a deterministic fake
vector index that matches the FAISS contract (fixed-width (1,k) results, -1 padding). No FAISS,
no embedder, no reading the gitignored `memory_base`. The public report omits raw fixture text
and carries non-canonical provenance. No runtime behavior is changed — the harness calls the
parked method directly; nothing is wired into the pipeline.
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
        """Match the FAISS contract: always return fixed (1, k) arrays, padding with -1
        indices (and a -inf-like sentinel score) when k > ntotal — so the real
        `if idx == -1` guard in search_vectors is exercised on real-shaped input
        (recall searches with top_k=20, which exceeds a small fixture store)."""
        q = np.asarray(query, dtype=np.float32)[0]
        ntotal = self._vectors.shape[0]
        idx = np.full(k, -1, dtype=np.int64)
        scores = np.full(k, -3.4e38, dtype=np.float32)
        if ntotal:
            dists = np.linalg.norm(self._vectors - q, axis=1)
            order = np.argsort(dists)[:k]
            n = len(order)
            idx[:n] = order.astype(np.int64)
            # Hippocampus sorts results DESC by score, so return higher-is-closer scores.
            scores[:n] = (1.0 / (1.0 + dists[order])).astype(np.float32)
        return scores.reshape(1, -1), idx.reshape(1, -1)


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
    """A controlled, in-memory Hippocampus whose store holds a planted 'corrective' memory
    that is the NEAREST neighbour of the correction direction (b_vec) among several distractors,
    but is NOT identical to it. The planted vector is offset from the query so the planted item
    must be SELECTED by the real recall fusion (top_k < store size) rather than winning trivially
    as a distance-0 copy of the query."""
    hippo = _new_hippocampus_no_store()
    # Planted vector: near b_vec but deliberately offset (so it is not the query itself),
    # while staying far closer than any distractor -> the real ranking must surface it.
    offset = (0.05 * _fake_embed("corrective neighbour perturbation")).astype(np.float32)
    planted_vec = np.asarray(b_vec, dtype=np.float32) + offset
    distractors = {
        "distractor_a": _fake_embed("unrelated note about scheduling"),
        "distractor_b": _fake_embed("unrelated note about formatting"),
        "distractor_c": _fake_embed("unrelated note about weather"),
        "distractor_d": _fake_embed("unrelated note about travel"),
    }
    vectors = np.stack([planted_vec, *distractors.values()])
    now = datetime.now(timezone.utc).isoformat()
    hippo.index = _FakeIndex(vectors)
    hippo.metadata = [
        {
            "id": planted_id,
            "content": "corrective exemplar",
            "source_file": "fixture",
            "ingested_at": now,
        },
        *(
            {"id": d_id, "content": d_id, "source_file": "fixture", "ingested_at": now}
            for d_id in distractors
        ),
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
        "store_size": 0,
        "recall_top_k": 0,
    }
    degradation_events: list[DegradationEvent] = []

    try:
        if fixture.mode == "inert_default":
            hippo = _new_hippocampus_no_store()
            # Call the NAMED parked entry point (recall_corrective composes
            # compute_error_vector + recall); empty store -> nothing recalled.
            results = hippo.recall_corrective(intended, generated, top_k=5)
            observed["recall_hit_count"] = len(results)
            observed["inert_by_default"] = len(results) == 0
        elif fixture.mode == "noop_zero_vector":
            # GUARD-level: intended == generated -> error vector is ~zero -> the no-rewrite
            # no-op the pipeline skips (norm <= ZERO_VECTOR_EPS). recall is not called here.
            observed["noop_on_zero_vector"] = b_norm <= ZERO_VECTOR_EPS
        elif fixture.mode == "lit_discrepancy":
            top_k = 3
            hippo = _lit_hippocampus(b_vec, fixture.planted_item_id)
            store_size = len(hippo.metadata)
            # Call the NAMED parked entry point, not an inline reimplementation of its glue.
            results = hippo.recall_corrective(intended, generated, top_k=top_k)
            observed["store_size"] = store_size
            observed["recall_top_k"] = top_k
            observed["recall_hit_count"] = len(results)
            observed["recall_fires_when_lit"] = len(results) > 0
            # Membership (not top-1 ranking): did the planted corrective id plumb through the
            # real index -> metadata -> RRF -> MemoryResult mapping into the SELECTED subset?
            # Non-degenerate: top_k < store_size forces selection; planted vector != query.
            observed["returns_planted_item"] = any(
                r.doc_id == fixture.planted_item_id for r in results
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
        f"Under this fixture set, corrective recall is inert by default with no store "
        f"({metrics['inert_by_default_rate']}); the pre-recall guard skips on a zero error "
        f"vector / no-rewrite case ({metrics['noop_on_zero_vector_rate']}); and given a "
        f"populated store the recall path fires ({metrics['recall_fires_when_lit_rate']}) and "
        f"the planted corrective item is present in the selected subset "
        f"({metrics['returns_planted_item_rate']}). These are structural signals — not a claim "
        f"about runtime liveness, discrepancy-gated firing, or recall quality."
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
            "signal_levels": {
                "inert_by_default": "recall",
                "noop_on_zero_vector": "guard",
                "recall_fires_when_lit": "recall",
                "returns_planted_item": "recall",
            },
            "notes": [
                "The named parked entry point recall_corrective (which composes "
                "compute_error_vector + recall) is called directly; nothing is wired into the "
                "runtime pipeline.",
                "A deterministic fake vector index matches the FAISS contract (fixed-width "
                "(1,k) results, -1 padding) and stands in for FAISS + the gitignored "
                "memory_base; production recall needs a real index and a populated store.",
                "returns_planted_item is a MEMBERSHIP check (is the planted id in the selected "
                "subset), not a top-1 ranking or relevance judgement; it is non-degenerate "
                "because top_k < store size and the planted vector is offset from the query.",
                "Signal levels: noop_on_zero_vector is GUARD-level (the pre-recall discrepancy "
                "gate; recall is not called), the others are RECALL-level. The only firing "
                "precondition the lit case demonstrates for recall itself is a populated store "
                "— not a discrepancy (recall fires on a zero error vector too).",
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
