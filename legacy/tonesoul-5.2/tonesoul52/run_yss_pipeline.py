import argparse
import json
import os
from typing import Dict, Optional

from .yss_pipeline import PipelineConfig, run_pipeline
from .ystm.energy import EnergyConfig
from .ystm.representation import EmbeddingConfig
from .ystm.terrain import TerrainConfig


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run full YSS pipeline (M0-M5 + gates).")
    parser.add_argument("--run-dir", help="Override run directory.")
    parser.add_argument("--seed", help="Seed JSON/YAML for context compiler.")
    parser.add_argument("--task", help="Override task string.")
    parser.add_argument("--objective", help="Override objective string.")
    parser.add_argument("--domain", help="Override domain.")
    parser.add_argument("--decision-mode", help="Override decision mode.")
    parser.add_argument("--skip-ystm", action="store_true", help="Skip YSTM demo generation.")
    parser.add_argument("--ystm-export-png", action="store_true", help="Export YSTM PNGs if cairosvg is available.")
    parser.add_argument("--ystm-png-scale", type=float, default=2.0, help="Scale factor for YSTM PNG export.")
    parser.add_argument("--ystm-input", help="Optional YSTM segments JSON.")
    parser.add_argument("--ystm-diff", help="Optional semantic_diff.json to attach to evidence/audit.")
    parser.add_argument("--tech-trace-capture", help="Optional tech_trace capture JSON to attach.")
    parser.add_argument("--tech-trace-normalize", help="Optional tech_trace normalized JSON to attach.")
    parser.add_argument("--intent-evidence", help="Optional intent evidence JSON for verification.")
    parser.add_argument(
        "--tech-trace-auto",
        action="store_true",
        help="Auto-generate tech-trace capture/normalize from the execution report.",
    )
    parser.add_argument(
        "--tech-trace-claim-limit",
        type=int,
        default=12,
        help="Max claim count for tech-trace auto extraction.",
    )
    parser.add_argument(
        "--tech-trace-claim-min-chars",
        type=int,
        default=24,
        help="Minimum characters for tech-trace auto claims.",
    )
    parser.add_argument("--error-event", help="Optional ErrorEvent JSON.")
    parser.add_argument("--error-ledger", help="Optional error_ledger.jsonl path.")
    parser.add_argument("--skip-gates", action="store_true", help="Skip gate validators.")
    parser.add_argument(
        "--trace-level",
        default="standard",
        choices=["standard", "full"],
        help="Trace level: standard skips memory/skill promotion; full records everything.",
    )
    parser.add_argument(
        "--require-seed",
        action="store_true",
        help="Fail gates if memory seed schema is missing or invalid.",
    )
    parser.add_argument(
        "--require-tech-trace",
        action="store_true",
        help="Fail gates if tech-trace normalize is missing or invalid.",
    )
    parser.add_argument(
        "--require-intent",
        action="store_true",
        help="Fail gates if intent verification is missing or inconclusive.",
    )
    parser.add_argument(
        "--tech-trace-strict",
        action="store_true",
        help="Require attributions to reference claim ids in tech-trace gate.",
    )
    parser.add_argument(
        "--poav-threshold",
        type=float,
        default=0.7,
        help="POAV threshold for gate decision.",
    )
    parser.add_argument(
        "--enforce-poav",
        action="store_true",
        help="Fail gates if POAV falls below threshold.",
    )
    parser.add_argument(
        "--drift-threshold",
        type=float,
        default=4.0,
        help="Drift threshold for escalation decisions.",
    )
    parser.add_argument(
        "--mercy-threshold",
        type=float,
        default=0.1,
        help="Mercy objective threshold for gate decision.",
    )
    parser.add_argument(
        "--enforce-mercy",
        action="store_true",
        help="Fail gates if Mercy objective falls below threshold.",
    )
    parser.add_argument(
        "--enforce-guardian",
        action="store_true",
        help="Fail gates if guardian roles are missing.",
    )
    parser.add_argument(
        "--mercy-weights",
        help="JSON string or path for mercy objective weight overrides.",
    )
    parser.add_argument(
        "--mercy-signals",
        help="JSON string or path for mercy objective signal overrides.",
    )
    parser.add_argument("--skip-memory", action="store_true", help="Skip memory recording.")
    parser.add_argument("--memory-root", help="Override memory root (default: 5.2/memory).")
    parser.add_argument("--archive-root", help="Override archive root for runs.")
    parser.add_argument("--skip-skill-promote", action="store_true", help="Skip skill promotion.")
    parser.add_argument("--skill-policy", help="Override memory promotion policy YAML.")
    parser.add_argument("--skip-skill-review", action="store_true", help="Skip auto skill review.")
    parser.add_argument("--skip-auto-compact", action="store_true", help="Skip auto run compaction.")
    parser.add_argument("--compact-max-runs", type=int, help="Override compaction max active runs.")
    parser.add_argument("--compact-keep-latest", type=int, help="Override compaction keep latest.")
    parser.add_argument("--embedding-dims", type=int, default=12)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--beta", type=float, default=0.0)
    parser.add_argument("--gamma", type=float, default=0.0)
    parser.add_argument("--no-normalize-energy", action="store_true")
    parser.add_argument("--grid-width", type=int, default=80)
    parser.add_argument("--grid-height", type=int, default=60)
    parser.add_argument("--sigma", type=float, default=0.75)
    parser.add_argument("--levels", type=int, default=5)
    return parser


def _load_json_arg(
    parser: argparse.ArgumentParser,
    value: Optional[str],
    label: str,
) -> Optional[Dict[str, float]]:
    if value is None:
        return None
    try:
        if os.path.exists(value):
            with open(value, "r", encoding="utf-8-sig") as handle:
                payload = json.load(handle)
        else:
            payload = json.loads(value)
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"{label} must be JSON or a JSON file path: {exc}")
    if not isinstance(payload, dict):
        parser.error(f"{label} must be a JSON object.")
    return payload


def main() -> Dict[str, object]:
    parser = build_arg_parser()
    args = parser.parse_args()
    mercy_weights = _load_json_arg(parser, args.mercy_weights, "--mercy-weights")
    mercy_signals = _load_json_arg(parser, args.mercy_signals, "--mercy-signals")
    config = PipelineConfig(
        run_dir=args.run_dir,
        seed_path=args.seed,
        task=args.task,
        objective=args.objective,
        domain=args.domain,
        decision_mode=args.decision_mode,
        run_ystm_demo=not args.skip_ystm,
        ystm_export_png=args.ystm_export_png,
        ystm_png_scale=args.ystm_png_scale,
        ystm_input=args.ystm_input,
        ystm_diff_path=args.ystm_diff,
        tech_trace_capture_path=args.tech_trace_capture,
        tech_trace_normalize_path=args.tech_trace_normalize,
        intent_evidence_path=args.intent_evidence,
        tech_trace_auto=args.tech_trace_auto,
        tech_trace_auto_claim_limit=args.tech_trace_claim_limit,
        tech_trace_auto_claim_min_chars=args.tech_trace_claim_min_chars,
        tech_trace_require=args.require_tech_trace,
        tech_trace_strict=args.tech_trace_strict,
        intent_require=args.require_intent,
        error_event=args.error_event,
        error_ledger=args.error_ledger,
        skip_gates=args.skip_gates,
        seed_gate_require=args.require_seed,
        trace_level=args.trace_level,
        poav_threshold=args.poav_threshold,
        poav_enforce=args.enforce_poav,
        drift_threshold=args.drift_threshold,
        mercy_threshold=args.mercy_threshold,
        mercy_enforce=args.enforce_mercy,
        guardian_enforce=args.enforce_guardian,
        mercy_weights=mercy_weights,
        mercy_signals=mercy_signals,
        record_memory=not args.skip_memory,
        memory_root=args.memory_root,
        archive_root=args.archive_root,
        promote_skills=not args.skip_skill_promote,
        skill_policy_path=args.skill_policy,
        auto_review_skills=not args.skip_skill_review,
        auto_compact=not args.skip_auto_compact,
        compact_max_runs=args.compact_max_runs,
        compact_keep_latest=args.compact_keep_latest,
        energy=EnergyConfig(
            alpha=args.alpha,
            beta=args.beta,
            gamma=args.gamma,
            normalize=not args.no_normalize_energy,
        ),
        embedding=EmbeddingConfig(dims=args.embedding_dims),
        terrain=TerrainConfig(
            grid_width=args.grid_width,
            grid_height=args.grid_height,
            sigma=args.sigma,
            contour_levels=args.levels,
        ),
    )
    return run_pipeline(config)


if __name__ == "__main__":
    paths = main()
    for key, value in paths.items():
        print(f"{key}: {value}")
