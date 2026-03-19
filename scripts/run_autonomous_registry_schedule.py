from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tonesoul.autonomous_schedule import build_autonomous_registry_schedule  # noqa: E402
from tonesoul.schedule_profile import resolve_schedule_profile  # noqa: E402


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _resolve_list(explicit: list[str], profile_values: list[str]) -> list[str]:
    if explicit:
        return [str(item).strip() for item in explicit if str(item).strip()]
    return list(profile_values)


def _resolve_value(explicit: object, profile_value: object, fallback: object) -> object:
    if explicit is not None:
        return explicit
    if profile_value is not None:
        return profile_value
    return fallback


def _parse_int_mapping_overrides(values: list[str], *, option_name: str) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for raw_item in values:
        item = str(raw_item).strip()
        if not item:
            continue
        key, separator, raw_value = item.partition("=")
        name = key.strip().lower()
        if separator != "=" or not name:
            raise ValueError(f"{option_name} entries must use category=value format: {item!r}")
        try:
            value = int(raw_value.strip())
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{option_name} value must be an integer: {item!r}") from exc
        if value < 1:
            raise ValueError(f"{option_name} value must be >= 1: {item!r}")
        mapping[name] = value
    return mapping


def _resolve_mapping(
    explicit_values: list[str],
    profile_values: dict[str, int] | None,
    *,
    option_name: str,
) -> dict[str, int]:
    merged = {str(key).strip().lower(): int(value) for key, value in (profile_values or {}).items()}
    merged.update(_parse_int_mapping_overrides(explicit_values, option_name=option_name))
    return merged


def _resolve_optional_float(
    explicit: float | None,
    profile_value: float | None,
) -> float | None:
    if explicit is not None:
        return float(explicit)
    if profile_value is not None:
        return float(profile_value)
    return None


def _resolve_optional_int(
    explicit: int | None,
    profile_value: int | None,
) -> int | None:
    if explicit is not None:
        return int(explicit)
    if profile_value is not None:
        return int(profile_value)
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run ToneSoul autonomous schedule against curated registry sources."
    )
    parser.add_argument("--db-path", type=str, default=None, help="Path to soul.db")
    parser.add_argument(
        "--crystal-path", type=str, default=None, help="Path to crystals.jsonl override"
    )
    parser.add_argument(
        "--journal-path",
        type=str,
        default="memory/self_journal.jsonl",
        help="Path to self_journal JSONL",
    )
    parser.add_argument(
        "--history-path",
        type=str,
        default="memory/autonomous/dream_wakeup_history.jsonl",
        help="Path to append wake-up history JSONL rows",
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        default="docs/status/dream_wakeup_snapshot_latest.json",
        help="Path to write the latest wake-up snapshot JSON",
    )
    parser.add_argument(
        "--dashboard-out-dir",
        type=str,
        default="docs/status",
        help="Directory for dream observability artifacts",
    )
    parser.add_argument(
        "--registry-path",
        type=str,
        default="spec/external_source_registry.yaml",
        help="Curated external source registry YAML path",
    )
    parser.add_argument(
        "--profile-path",
        type=str,
        default="spec/registry_schedule_profiles.yaml",
        help="Schedule profile YAML path",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=None,
        help="Named schedule profile to resolve from the profile spec",
    )
    parser.add_argument(
        "--registry-id",
        action="append",
        default=[],
        help="Registry entry id to include (repeatable)",
    )
    parser.add_argument(
        "--registry-category",
        action="append",
        default=[],
        help="Registry category to include (repeatable)",
    )
    parser.add_argument(
        "--entries-per-cycle",
        type=int,
        default=None,
        help="Number of approved registry entries to rotate through per schedule tick",
    )
    parser.add_argument(
        "--urls-per-cycle",
        type=int,
        default=None,
        help="Maximum number of curated URLs to ingest per schedule tick",
    )
    parser.add_argument(
        "--revisit-interval-cycles",
        type=int,
        default=None,
        help="Minimum number of schedule cycles before the same entry may be selected again",
    )
    parser.add_argument(
        "--failure-backoff-cycles",
        type=int,
        default=None,
        help="Base number of schedule cycles to back off after a source-specific failure",
    )
    parser.add_argument(
        "--category-weight",
        action="append",
        default=[],
        help="Override or add category cadence weight using category=value (repeatable)",
    )
    parser.add_argument(
        "--category-backoff-multiplier",
        action="append",
        default=[],
        help="Override or add category backoff multiplier using category=value (repeatable)",
    )
    parser.add_argument(
        "--tension-max-friction-score",
        type=float,
        default=None,
        help="Maximum allowed wake-up cycle friction before category cooldown is applied",
    )
    parser.add_argument(
        "--tension-max-lyapunov-proxy",
        type=float,
        default=None,
        help="Maximum allowed wake-up cycle Lyapunov proxy before category cooldown is applied",
    )
    parser.add_argument(
        "--tension-max-council-count",
        type=int,
        default=None,
        help="Maximum allowed council count per wake-up cycle before category cooldown is applied",
    )
    parser.add_argument(
        "--tension-max-llm-preflight-latency-ms",
        type=int,
        default=None,
        help="Maximum allowed total LLM preflight latency per wake-up cycle before category cooldown is applied",
    )
    parser.add_argument(
        "--tension-max-llm-selection-latency-ms",
        type=int,
        default=None,
        help="Maximum allowed backend selection latency per wake-up cycle before category cooldown is applied",
    )
    parser.add_argument(
        "--tension-max-llm-probe-latency-ms",
        type=int,
        default=None,
        help="Maximum allowed inference probe latency per wake-up cycle before category cooldown is applied",
    )
    parser.add_argument(
        "--tension-max-llm-timeout-count",
        type=int,
        default=None,
        help="Maximum allowed LLM preflight timeout count per wake-up cycle before category cooldown is applied",
    )
    parser.add_argument(
        "--tension-max-consecutive-failure-count",
        type=int,
        default=None,
        help="Maximum allowed nested wake-up consecutive failure count before category cooldown is applied",
    )
    parser.add_argument(
        "--tension-cooldown-cycles",
        type=int,
        default=None,
        help="Number of schedule cycles to cool selected categories after a tension budget breach",
    )
    stale_group = parser.add_mutually_exclusive_group()
    stale_group.add_argument(
        "--allow-stale-registry",
        dest="allow_stale_registry",
        action="store_true",
        help="Allow stale reviewed registry entries to be scheduled",
    )
    stale_group.add_argument(
        "--disallow-stale-registry",
        dest="allow_stale_registry",
        action="store_false",
        help="Force stale reviewed registry entries to remain excluded",
    )
    parser.set_defaults(allow_stale_registry=None)
    parser.add_argument(
        "--schedule-state-path",
        type=str,
        default="memory/autonomous/registry_schedule_state.json",
        help="Path to persisted schedule cursor state JSON",
    )
    parser.add_argument(
        "--schedule-snapshot-path",
        type=str,
        default="docs/status/autonomous_registry_schedule_latest.json",
        help="Path to write the latest schedule snapshot JSON",
    )
    parser.add_argument(
        "--schedule-history-path",
        type=str,
        default="memory/autonomous/registry_schedule_history.jsonl",
        help="Path to append schedule cycle history JSONL rows",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=None,
        help="Seconds between schedule ticks",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=1,
        help="Number of schedule ticks to execute",
    )
    parser.add_argument("--limit", type=int, default=None, help="Dream stimulus selection limit")
    parser.add_argument(
        "--min-priority",
        type=float,
        default=None,
        help="Minimum priority score for DreamEngine selection",
    )
    parser.add_argument(
        "--related-limit",
        type=int,
        default=None,
        help="Maximum related memories per collision",
    )
    parser.add_argument(
        "--crystal-count",
        type=int,
        default=None,
        help="Maximum crystal rules used by DreamEngine",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM reflection generation",
    )
    parser.add_argument(
        "--skip-llm-preflight",
        action="store_true",
        help="Skip bounded inference-readiness probe before reflection generation",
    )
    parser.add_argument(
        "--llm-probe-timeout-seconds",
        type=float,
        default=10.0,
        help="Timeout for the bounded LLM inference-readiness probe",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if registry selection or downstream execution is not fully OK",
    )
    return parser


def run_schedule(args: argparse.Namespace) -> dict[str, object]:
    profile = (
        resolve_schedule_profile(Path(args.profile_path), args.profile) if args.profile else None
    )
    schedule = build_autonomous_registry_schedule(
        db_path=Path(args.db_path) if args.db_path else None,
        crystal_path=Path(args.crystal_path) if args.crystal_path else None,
        journal_path=Path(args.journal_path),
        history_path=Path(args.history_path),
        snapshot_path=Path(args.snapshot_path),
        dashboard_out_dir=Path(args.dashboard_out_dir),
        registry_path=Path(args.registry_path),
        schedule_state_path=Path(args.schedule_state_path),
        schedule_snapshot_path=Path(args.schedule_snapshot_path),
        schedule_history_path=Path(args.schedule_history_path),
        interval_seconds=float(
            _resolve_value(
                args.interval_seconds,
                profile.interval_seconds if profile else None,
                10800.0,
            )
        ),
    )
    payload = schedule.run(
        max_cycles=args.max_cycles,
        entry_ids=_resolve_list(args.registry_id, profile.registry_entry_ids if profile else []),
        categories=_resolve_list(
            args.registry_category,
            profile.registry_categories if profile else [],
        ),
        entries_per_cycle=int(
            _resolve_value(
                args.entries_per_cycle,
                profile.entries_per_cycle if profile else None,
                1,
            )
        ),
        urls_per_cycle=int(
            _resolve_value(
                args.urls_per_cycle,
                profile.urls_per_cycle if profile else None,
                3,
            )
        ),
        revisit_interval_cycles=int(
            _resolve_value(
                args.revisit_interval_cycles,
                profile.revisit_interval_cycles if profile else None,
                0,
            )
        ),
        failure_backoff_cycles=int(
            _resolve_value(
                args.failure_backoff_cycles,
                profile.failure_backoff_cycles if profile else None,
                0,
            )
        ),
        category_weights=_resolve_mapping(
            args.category_weight,
            profile.category_weights if profile else None,
            option_name="--category-weight",
        ),
        category_backoff_multipliers=_resolve_mapping(
            args.category_backoff_multiplier,
            profile.category_backoff_multipliers if profile else None,
            option_name="--category-backoff-multiplier",
        ),
        tension_max_friction_score=_resolve_optional_float(
            args.tension_max_friction_score,
            profile.tension_max_friction_score if profile else None,
        ),
        tension_max_lyapunov_proxy=_resolve_optional_float(
            args.tension_max_lyapunov_proxy,
            profile.tension_max_lyapunov_proxy if profile else None,
        ),
        tension_max_council_count=_resolve_optional_int(
            args.tension_max_council_count,
            profile.tension_max_council_count if profile else None,
        ),
        tension_max_llm_preflight_latency_ms=_resolve_optional_int(
            args.tension_max_llm_preflight_latency_ms,
            profile.tension_max_llm_preflight_latency_ms if profile else None,
        ),
        tension_max_llm_selection_latency_ms=_resolve_optional_int(
            args.tension_max_llm_selection_latency_ms,
            profile.tension_max_llm_selection_latency_ms if profile else None,
        ),
        tension_max_llm_probe_latency_ms=_resolve_optional_int(
            args.tension_max_llm_probe_latency_ms,
            profile.tension_max_llm_probe_latency_ms if profile else None,
        ),
        tension_max_llm_timeout_count=_resolve_optional_int(
            args.tension_max_llm_timeout_count,
            profile.tension_max_llm_timeout_count if profile else None,
        ),
        tension_max_consecutive_failure_count=_resolve_optional_int(
            args.tension_max_consecutive_failure_count,
            profile.tension_max_consecutive_failure_count if profile else None,
        ),
        tension_cooldown_cycles=int(
            _resolve_value(
                args.tension_cooldown_cycles,
                profile.tension_cooldown_cycles if profile else None,
                0,
            )
        ),
        include_stale=bool(
            _resolve_value(
                args.allow_stale_registry,
                profile.include_stale if profile else None,
                False,
            )
        ),
        cycle_kwargs={
            "limit": int(
                _resolve_value(
                    args.limit,
                    profile.limit if profile else None,
                    3,
                )
            ),
            "min_priority": float(
                _resolve_value(
                    args.min_priority,
                    profile.min_priority if profile else None,
                    0.35,
                )
            ),
            "related_limit": int(
                _resolve_value(
                    args.related_limit,
                    profile.related_limit if profile else None,
                    5,
                )
            ),
            "crystal_count": int(
                _resolve_value(
                    args.crystal_count,
                    profile.crystal_count if profile else None,
                    5,
                )
            ),
            "generate_reflection": not bool(args.no_llm),
            "require_inference_ready": not bool(args.no_llm or args.skip_llm_preflight),
            "inference_timeout_seconds": float(args.llm_probe_timeout_seconds),
        },
    )
    payload["profile"] = profile.to_dict() if profile is not None else None
    return payload


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = run_schedule(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
