"""ToneSoul CLI — unified operator command surface.

Subcommands
-----------
  ts diagnose      Runtime health, drift, vow state (wraps tonesoul.diagnose)
  ts council       Run council deliberation on a draft (wraps council.council_cli)
  ts review        Review a file for claim-to-evidence mismatch risks
  ts context       Compile a context.yaml for pipeline runs
  ts heartbeat     Emit a heartbeat pulse and show status
  ts ystm          Run the YSTM terrain demo pipeline
  ts start         Start an agent session (wraps scripts/start_agent_session.py)
  ts end           End an agent session  (wraps scripts/end_agent_session.py)
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

__ts_layer__ = "surface"
__ts_purpose__ = "Unified CLI entry point: dispatch operator subcommands to the right subsystem."


def _cmd_diagnose(argv: List[str]) -> int:
    from tonesoul.diagnose import main as diag_main

    sys.argv = ["ts diagnose"] + argv
    diag_main()
    return 0


def _cmd_council(argv: List[str]) -> int:
    from tonesoul.council.council_cli import main as council_main

    council_main(argv)
    return 0


def _cmd_context(argv: List[str]) -> int:
    from tonesoul.context_compiler import main as ctx_main

    result = ctx_main(argv)
    if result:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


def _cmd_heartbeat(argv: List[str]) -> int:
    import json

    from tonesoul.heartbeat import Heartbeat

    parser = argparse.ArgumentParser(prog="ts heartbeat")
    parser.add_argument("--agent", default="unknown", help="Agent identifier")
    parser.add_argument("--note", default="", help="Optional note")
    parser.add_argument("--path", default=".aegis/heartbeat.jsonl", help="Heartbeat file path")
    parser.add_argument(
        "--status-only", action="store_true", help="Only print status, no new pulse"
    )
    args = parser.parse_args(argv)

    hb = Heartbeat(args.path)
    if not args.status_only:
        pulse = hb.pulse(agent=args.agent, note=args.note)
        print(f"[heartbeat] pulse recorded: {pulse['ts']}")
    status = hb.status()
    print(json.dumps(status, indent=2))
    return 0


def _cmd_ystm(argv: List[str]) -> int:
    import json

    from tonesoul.ystm.demo import DEFAULT_SEGMENTS, write_demo_outputs

    parser = argparse.ArgumentParser(prog="ts ystm")
    parser.add_argument(
        "--output-dir",
        default="/tmp/tonesoul_ystm_demo",  # nosec B108  # demo-only artifacts; caller can override.
        help="Output directory",
    )
    parser.add_argument(
        "--export-png", action="store_true", help="Also export PNG (requires cairosvg or Pillow)"
    )
    parser.add_argument("--segments", help="Optional path to a JSON segments file")
    args = parser.parse_args(argv)

    segments = DEFAULT_SEGMENTS
    if args.segments:
        with open(args.segments, encoding="utf-8") as fh:
            segments = json.load(fh)

    print(f"[ystm] running demo → {args.output_dir}")
    results = write_demo_outputs(args.output_dir, segments, export_png=args.export_png)
    for k, v in results.items():
        state = v if v else "(skipped)"
        print(f"  {k}: {state}")
    return 0


def _cmd_vows(argv: List[str]) -> int:
    from tonesoul.vow_system import VowRegistry

    parser = argparse.ArgumentParser(prog="ts vows")
    parser.add_argument("--path", default=None, help="Path to vow_store.json (optional)")
    args = parser.parse_args(argv)

    if args.path:
        from tonesoul.vow_system import VowRegistry

        registry = VowRegistry.from_file(args.path)
    else:
        from tonesoul.vow_system import create_enforcer

        registry = create_enforcer().registry

    vows = registry.all_vows()
    if not vows:
        print("No vows registered.")
        return 0
    active = registry.active_vows()
    print(f"Vows: {len(vows)} total, {len(active)} active\n")
    withdrawn_by = {
        record["vow_id"]: record for record in getattr(registry, "withdrawal_records", list)()
    }
    for vow in vows:
        record = withdrawn_by.get(vow.id)
        if record is not None:
            # the human-visible decency: an exit shows who retired it and why
            tag = f"[WITHDRAWN by {record['actor']}: {record['reason']}]"
        else:
            tag = "[ACTIVE]  " if vow.active else "[INACTIVE]"
        label = f"{vow.id}: {vow.title}"
        print(f"  {tag} {label:<40} {vow.description[:60]}")
    return 0


def _cmd_validate(argv: List[str]) -> int:
    """Validate a file's content against the council and exit with verdict-based code.

    Operator-friendly entry: `ts validate my_draft.md` reads the file, runs
    PreOutputCouncil.validate(), prints the human_summary (which since PR #45
    and #49 includes per-perspective dissent + branch tags), and exits with
    a code that maps to the verdict so it can be chained into git hooks / CI:
        0  APPROVE
        1  REFINE or DECLARE_STANCE (needs human attention)
        2  BLOCK
        3  file or argument error

    Differs from `ts council`: that one is the Node.js bridge contract
    (--draft text + --intent text + JSON stdout). `ts validate` is for
    humans validating a draft file in their editor / CI pipeline.
    """
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="ts validate",
        description="Validate a draft file against the council.",
    )
    parser.add_argument("file", type=Path, help="Path to the draft file to validate")
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable verdict JSON to stdout"
    )
    parser.add_argument("--quiet", action="store_true", help="No output; rely on exit code only")
    parser.add_argument(
        "--intent", default="", help="Optional user intent string for council context"
    )
    parser.add_argument(
        "--language",
        default="en",
        choices=["en", "zh"],
        help="Language for the human_summary output (en/zh)",
    )
    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"ts validate: file not found: {args.file}", file=sys.stderr)
        return 3
    if not args.file.is_file():
        print(f"ts validate: not a regular file: {args.file}", file=sys.stderr)
        return 3

    try:
        draft = args.file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"ts validate: cannot decode {args.file} as UTF-8: {exc}", file=sys.stderr)
        return 3

    from tonesoul.council.pre_output_council import PreOutputCouncil
    from tonesoul.council.types import VerdictType

    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output=draft,
        context={"language": args.language},
        user_intent=args.intent or None,
        auto_record_self_memory=False,
    )

    def _emit(text: str) -> None:
        """UTF-8-safe stdout write — handles Windows cp950 console gracefully."""
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        else:
            print(text)

    if args.json:
        _emit(json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2, default=str))
    elif not args.quiet:
        _emit(f"verdict:   {verdict.verdict.value}")
        _emit(f"coherence: {verdict.coherence.overall:.2f}")
        if verdict.human_summary:
            _emit("")
            _emit(verdict.human_summary)

    # Exit code maps to verdict severity (for git hooks / CI integration)
    if verdict.verdict == VerdictType.BLOCK:
        return 2
    if verdict.verdict in (VerdictType.REFINE, VerdictType.DECLARE_STANCE):
        return 1
    return 0


def _cmd_review(argv: List[str]) -> int:
    """Review a file for claim-to-evidence overclaim risks.

    Phase 1 is deterministic and local: it emits candidate findings for explicit claim-risk
    wording. Findings are reviewer aids, not a runtime gate, so successful review exits 0 even
    when findings are present.
    """
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="ts review",
        description="Review a file for claim-to-evidence mismatch risks.",
    )
    parser.add_argument("file", type=Path, help="Path to the text or markdown file to review")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable report JSON")
    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"ts review: file not found: {args.file}", file=sys.stderr)
        return 3
    if not args.file.is_file():
        print(f"ts review: not a regular file: {args.file}", file=sys.stderr)
        return 3

    try:
        from tonesoul.reviewer.report import review_file

        report = review_file(args.file)
    except UnicodeDecodeError as exc:
        print(f"ts review: cannot decode {args.file} as UTF-8: {exc}", file=sys.stderr)
        return 3

    def _emit(text: str) -> None:
        """UTF-8-safe stdout write -- handles Windows cp950 console gracefully."""
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        else:
            print(text)

    if args.json:
        _emit(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        count = len(report["findings"])
        _emit(f"claim-to-evidence findings: {count}")
        if count:
            _emit("Run with --json for structured details.")
    return 0


_SUBCOMMANDS = {
    "diagnose": (_cmd_diagnose, "Runtime health, drift, and vow state"),
    "council": (_cmd_council, "Run council deliberation on a draft output"),
    "validate": (_cmd_validate, "Validate a draft file against the council (operator-friendly)"),
    "review": (_cmd_review, "Review a file for claim-to-evidence mismatch risks"),
    "context": (_cmd_context, "Compile a context.yaml for pipeline runs"),
    "heartbeat": (_cmd_heartbeat, "Emit a heartbeat pulse and show file-backed status"),
    "ystm": (_cmd_ystm, "Run the YSTM terrain visualization demo"),
    "vows": (_cmd_vows, "Inspect active governance vows"),
}


def _print_help() -> None:
    print("ToneSoul CLI — AI governance operator surface\n")
    print("Usage: ts <command> [args...]\n")
    print("Commands:")
    for name, (_, desc) in _SUBCOMMANDS.items():
        print(f"  {name:<12} {desc}")
    print("\nRun 'ts <command> --help' for command-specific options.")


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        _print_help()
        return 0

    cmd = argv[0]
    rest = argv[1:]

    if cmd not in _SUBCOMMANDS:
        print(f"ts: unknown command '{cmd}'", file=sys.stderr)
        print("Run 'ts --help' for available commands.", file=sys.stderr)
        return 1

    handler, _ = _SUBCOMMANDS[cmd]
    try:
        return handler(rest)
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
