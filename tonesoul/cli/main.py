"""ToneSoul CLI — unified operator command surface.

Subcommands
-----------
  ts diagnose      Runtime health, drift, vow state (wraps tonesoul.diagnose)
  ts council       Run council deliberation on a draft (wraps council.council_cli)
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
__ts_purpose__ = (
    "Unified CLI entry point: dispatch operator subcommands to the right subsystem."
)


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
    parser.add_argument("--status-only", action="store_true", help="Only print status, no new pulse")
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
    parser.add_argument("--output-dir", default="/tmp/tonesoul_ystm_demo", help="Output directory")
    parser.add_argument("--export-png", action="store_true", help="Also export PNG (requires cairosvg or Pillow)")
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
    for vow in vows:
        tag = "[ACTIVE]  " if vow.active else "[INACTIVE]"
        label = f"{vow.id}: {vow.title}"
        print(f"  {tag} {label:<40} {vow.description[:60]}")
    return 0


_SUBCOMMANDS = {
    "diagnose": (_cmd_diagnose, "Runtime health, drift, and vow state"),
    "council": (_cmd_council, "Run council deliberation on a draft output"),
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
