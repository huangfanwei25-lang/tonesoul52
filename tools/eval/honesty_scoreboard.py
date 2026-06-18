"""Honesty-auditor scoreboard (program piece 5).

Aggregates the existing honesty characterizations into ONE generated
(`canonical: false`) board: "what ToneSoul measurably catches / misses under
pressure." This is the accountability artifact — the deliberate opposite of a
flashy demo. It is an INDEX of per-piece structural findings, not a new
capability and NOT a composite score.

Design (load-bearing honesty):
  - It REGENERATES each piece's report in-process (imports each piece's
    build_report and calls it with a fixed timestamp) rather than reading the
    committed JSON findings — so the board is always consistent with the current
    code and cannot drift to a stale snapshot.
  - It composes NOTHING into a higher confidence: N green characterizations stay
    N individual findings. Each piece is individual-level structural measurement
    on sanitized fixtures, with no oracle for intent / truth / correctness. The
    board bakes that anti-aggregation rule in code (BOARD_FORBIDDEN_CLAIM_IDS)
    and refuses to emit any aggregate "honesty score".
  - It inherits and re-surfaces every piece's own forbidden-claim set and
    "does-not-claim" negations, so the index cannot quietly drop a piece's limits.
  - It is honest about its own gaps (`what_this_board_does_not_have`): no real
    consumers, no external reviewer, no E1-E5 ladder (the repo has none), no
    composite score.

No runtime behaviour is changed; nothing here is wired into the pipeline.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_REPORT_PATH = Path("docs/status/honesty_scoreboard_latest.json")
DEFAULT_MARKDOWN_REPORT_PATH = Path("docs/status/honesty_scoreboard_latest.md")
DEFAULT_SOURCE_COMMAND = "python tools/eval/honesty_scoreboard.py --write-report"

# Claims this board must never be read as making — the aggregation trap, baked in.
BOARD_FORBIDDEN_CLAIM_IDS = (
    "the_system_is_honest",
    "green_means_safe",
    "these_pieces_compose_to_a_guarantee",
    "higher_confidence_than_any_single_piece",
    "measures_intent_or_truth",
)

ANTI_AGGREGATION_CAVEAT = (
    "Each piece is an individual-level structural characterization on sanitized fixtures. "
    "They do NOT compose into a higher system-level confidence or an 'is honest' guarantee — "
    "N green characterizations remain N individual findings. Read each at its own (modest) "
    "evidence level; do not let the index inflate it."
)

EVIDENCE_LADDER_NOTE = (
    "Evidence levels follow the repo's canonical ladder "
    "(docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md: E1 test-backed "
    "... E6 unverifiable). Every piece here is E1 for its STRUCTURAL claim — an automated test "
    "asserts the signal and CI fails if it breaks — but that E1 is scoped to sanitized fixtures, "
    "not production traffic. The scope (fixture-bound, no-oracle, no production consumers) is the "
    "limit, not the evidence strength. The board does not map findings onto the broader production "
    "claims in TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md; those are rated separately. "
    "(Self-review correction: an earlier draft of this note claimed the repo had no E1-E5 ladder "
    "— a false 'verified' claim from grepping only runtime code, not docs/architecture/. Fixed.)"
)

WHAT_THIS_BOARD_DOES_NOT_HAVE = (
    "real consumers — the characterized paths have little or no production traffic yet",
    "an external independent reviewer — same-model self-review has correlated blind spots",
    "a composite / aggregate honesty score — deliberately absent",
    "a cross-link into docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md — these E1 "
    "findings are not yet registered in the repo's claim-evidence matrix",
    "any measurement of intent, truth, or moral correctness — there is no oracle",
)


@dataclass(frozen=True)
class Piece:
    program_piece: int
    piece_id: str
    leg: str  # output-gate | council-under-pressure | memory-recall
    module: str
    finding_stem: str


# Ordered by program piece. egress_gate is piece 0 (the output-gate leg + the harness
# pattern the later pieces reuse); 1-4 are the program's measured pieces.
PIECES: tuple[Piece, ...] = (
    Piece(
        0,
        "egress_gate",
        "output-gate",
        "tools.eval.egress_gate_characterization",
        "egress_gate_characterization_latest",
    ),
    Piece(
        1,
        "dilemma_pressure",
        "council-under-pressure",
        "tools.eval.dilemma_pressure_characterization",
        "dilemma_pressure_characterization_latest",
    ),
    Piece(
        2,
        "unsourced_confidence",
        "council-under-pressure",
        "tools.eval.unsourced_confidence_characterization",
        "unsourced_confidence_characterization_latest",
    ),
    Piece(
        3,
        "sycophancy_pressure",
        "council-under-pressure",
        "tools.eval.sycophancy_pressure_characterization",
        "sycophancy_pressure_characterization_latest",
    ),
    Piece(
        4,
        "corrective_recall",
        "memory-recall",
        "tools.eval.corrective_recall_characterization",
        "corrective_recall_characterization_latest",
    ),
)

EVIDENCE_BASIS = {
    "evidence_level": "E1",
    "evidence_level_scope": (
        "test-backed for the structural signal under sanitized fixtures; "
        "NOT a claim about production behaviour"
    ),
    "ladder_ref": "docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md",
    "method": "structural characterization on sanitized fixtures",
    "oracle": "none (measures structure, not intent / truth / correctness)",
    "provenance": "canonical:false, re-runnable",
}


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


def _load_piece_report(module_path: str, updated_at: str) -> dict[str, Any]:
    """Regenerate a piece's report in-process with a fixed timestamp. The piece's
    own banner/output is suppressed so it does not pollute the board's stdout."""
    module = importlib.import_module(module_path)
    with contextlib.redirect_stdout(io.StringIO()):
        return module.build_report(updated_at=updated_at)


def _honest_negations(experiment: dict[str, Any]) -> list[str]:
    """The piece's own 'does-not-claim' structural flags (not_* booleans set True)."""
    return sorted(k for k, v in experiment.items() if k.startswith("not_") and v is True)


def _forbidden_claims(experiment: dict[str, Any]) -> list[str]:
    # egress_gate uses 'forbidden_public_claims'; the others use 'forbidden_public_claim_ids'.
    raw = (
        experiment.get("forbidden_public_claim_ids")
        or experiment.get("forbidden_public_claims")
        or []
    )
    return list(raw)


def _evidence_level_counts(built: list[dict[str, Any]]) -> dict[str, int]:
    """Count pieces by evidence level (an honest tally, NOT a composite quality score)."""
    counts: dict[str, int] = {}
    for s in built:
        level = s.get("evidence_basis", {}).get("evidence_level", "unknown")
        counts[level] = counts.get(level, 0) + 1
    return dict(sorted(counts.items()))


def _summarize_piece(piece: Piece, report: dict[str, Any]) -> dict[str, Any]:
    provenance = report.get("doc_provenance", {})
    experiment = report.get("experiment", {})
    return {
        "program_piece": piece.program_piece,
        "piece_id": piece.piece_id,
        "leg": piece.leg,
        "module": piece.module.replace(".", "/") + ".py",
        "finding_json": f"docs/status/{piece.finding_stem}.json",
        "finding_md": f"docs/status/{piece.finding_stem}.md",
        "canonical": bool(provenance.get("canonical", True)),
        "honest_conclusion": report.get("allowed_conclusion", ""),
        "measures": experiment.get("measures"),
        "does_not_claim": _honest_negations(experiment),
        "forbidden_public_claim_ids": _forbidden_claims(experiment),
        "raw_fixture_text_in_public_report": bool(
            experiment.get("raw_fixture_text_in_public_report", False)
        ),
        "evidence_basis": dict(EVIDENCE_BASIS),
        "build_ok": True,
    }


def build_report(
    *, updated_at: str, source_command: str = DEFAULT_SOURCE_COMMAND
) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    degradation_events: list[DegradationEvent] = []

    for piece in PIECES:
        try:
            report = _load_piece_report(piece.module, updated_at)
            summaries.append(_summarize_piece(piece, report))
        except Exception as exc:  # a piece that fails to build is a required-gate fault
            degradation_events.append(
                DegradationEvent(
                    gate=f"honesty_scoreboard:{piece.piece_id}",
                    tier="required",
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
            )
            summaries.append(
                {
                    "program_piece": piece.program_piece,
                    "piece_id": piece.piece_id,
                    "leg": piece.leg,
                    "module": piece.module.replace(".", "/") + ".py",
                    "finding_json": f"docs/status/{piece.finding_stem}.json",
                    "finding_md": f"docs/status/{piece.finding_stem}.md",
                    "build_ok": False,
                }
            )

    built = [s for s in summaries if s.get("build_ok")]
    metrics = {
        "piece_count": len(PIECES),
        "pieces_built": len(built),
        "build_failures": len(PIECES) - len(built),
        "legs_covered": sorted({s["leg"] for s in built}),
        "all_canonical_false": all(s.get("canonical") is False for s in built) if built else False,
        "pieces_with_raw_text_leak": sum(
            1 for s in built if s.get("raw_fixture_text_in_public_report")
        ),
        "total_forbidden_claims_declared": sum(
            len(s.get("forbidden_public_claim_ids", [])) for s in built
        ),
        "evidence_levels": _evidence_level_counts(built),
        "degradation_event_count": len(degradation_events),
    }

    allowed_conclusion = (
        f"This board indexes {metrics['pieces_built']}/{metrics['piece_count']} structural "
        f"honesty characterizations across {len(metrics['legs_covered'])} ToneSoul legs "
        f"({', '.join(metrics['legs_covered'])}). Each is individual-level, canonical:false, and "
        f"measures structure — not intent, truth, or moral correctness. The board does NOT compose "
        f"them into a system-level honesty score or guarantee: N green characterizations remain N "
        f"individual findings."
    )

    return {
        "schema_version": "honesty-scoreboard.v1",
        "doc_provenance": {
            "generated": True,
            "canonical": False,
            "source_command": source_command,
            "updated_at": updated_at,
        },
        "experiment": {
            "name": "honesty_scoreboard",
            "is_an_index_not_a_capability": True,
            "not_a_composite_score": True,
            "not_a_guarantee": True,
            "measures": "an index of per-piece structural characterizations; no new measurement",
            "board_forbidden_claim_ids": list(BOARD_FORBIDDEN_CLAIM_IDS),
            "anti_aggregation_caveat": ANTI_AGGREGATION_CAVEAT,
            "evidence_ladder_note": EVIDENCE_LADDER_NOTE,
            "raw_fixture_text_in_public_report": False,
        },
        "allowed_conclusion": allowed_conclusion,
        "what_this_board_does_not_have": list(WHAT_THIS_BOARD_DOES_NOT_HAVE),
        "metrics": metrics,
        "pieces": summaries,
        "degradation_events": [e.to_public_dict() for e in degradation_events],
    }


def render_markdown(report: dict[str, Any]) -> str:
    m = report["metrics"]
    exp = report["experiment"]
    lines: list[str] = []
    lines.append("# Honesty-Auditor Scoreboard")
    lines.append("")
    lines.append(f"generated: {report['doc_provenance']['generated']}")
    lines.append(f"canonical: {report['doc_provenance']['canonical']}")
    lines.append(f"updated_at: {report['doc_provenance']['updated_at']}")
    lines.append("")
    lines.append(
        "This is an INDEX of per-piece structural honesty characterizations — not a new "
        "measurement, not a composite score, not a guarantee. Every piece is regenerated "
        "in-process so the board stays consistent with the current code."
    )
    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    lines.append(report["allowed_conclusion"])
    lines.append("")
    lines.append("## Pieces")
    lines.append("")
    lines.append("| # | piece | leg | built | honest conclusion |")
    lines.append("|---|---|---|---|---|")
    for s in sorted(report["pieces"], key=lambda x: x["program_piece"]):
        if s.get("build_ok"):
            concl = s.get("honest_conclusion", "").replace("\n", " ")
            lines.append(f"| {s['program_piece']} | {s['piece_id']} | {s['leg']} | yes | {concl} |")
        else:
            lines.append(
                f"| {s['program_piece']} | {s['piece_id']} | {s['leg']} | **NO (build failed)** | — |"
            )
    lines.append("")
    lines.append("## What each piece refuses to claim")
    lines.append("")
    for s in sorted(report["pieces"], key=lambda x: x["program_piece"]):
        if not s.get("build_ok"):
            continue
        forbidden = ", ".join(s.get("forbidden_public_claim_ids", [])) or "(none declared)"
        lines.append(f"- **{s['piece_id']}** does not claim: {forbidden}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---|")
    for key in (
        "piece_count",
        "pieces_built",
        "build_failures",
        "all_canonical_false",
        "pieces_with_raw_text_leak",
        "total_forbidden_claims_declared",
        "degradation_event_count",
    ):
        lines.append(f"| {key} | {m[key]} |")
    lines.append("")
    lines.append("## Anti-aggregation rule (load-bearing)")
    lines.append("")
    lines.append(exp["anti_aggregation_caveat"])
    lines.append("")
    lines.append("## Evidence basis (E1, fixture-scoped)")
    lines.append("")
    lines.append(f"evidence levels: {m['evidence_levels']}")
    lines.append("")
    lines.append(exp["evidence_ladder_note"])
    lines.append("")
    lines.append("## What this board does NOT have")
    lines.append("")
    for gap in report["what_this_board_does_not_have"]:
        lines.append(f"- {gap}")
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
