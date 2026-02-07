import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

import yaml

from .ystm.schema import stable_hash, utc_now

DEFAULT_CONTEXT_SEED = {
    "task": "Build a minimal, auditable YSTM demo.",
    "objective": "Produce traceable outputs with clear audit hooks.",
    "domain": "governance",
    "audience": "internal",
    "mode": "analysis",
    "decision_mode": "normal",
    "assumptions": ["Inputs are trusted for demo purposes."],
    "constraints": ["Do not modify legacy project assets."],
    "residual_risk": "Low (demo only).",
    "rollback_condition": "Revert generated artifacts.",
}


def _load_seed(path: str) -> Dict[str, object]:
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8") as handle:
        if ext in {".yaml", ".yml"}:
            payload = yaml.safe_load(handle)
        elif ext == ".json":
            payload = json.load(handle)
        else:
            raise ValueError("Seed file must be .json or .yaml/.yml")
    if not isinstance(payload, dict):
        raise ValueError("Seed payload must be an object.")
    return payload


def compile_context(seed: Dict[str, object]) -> Dict[str, object]:
    now = utc_now()
    seed_json = json.dumps(seed, sort_keys=True)
    payload = {
        "context": {
            "task": seed.get("task"),
            "objective": seed.get("objective"),
            "domain": seed.get("domain", "general"),
            "audience": seed.get("audience", "internal"),
            "mode": seed.get("mode", "analysis"),
        },
        "assumptions": seed.get("assumptions", []),
        "constraints": seed.get("constraints", []),
        "inputs": {
            "source": seed.get("source", "manual"),
            "payload": seed.get("payload"),
        },
        "time_island": {
            "chronos": {
                "time_stamp": now,
                "dependency_basis": seed.get("dependency_basis", []),
                "change_log": seed.get("change_log", []),
            },
            "kairos": {
                "trigger": seed.get("trigger", "manual"),
                "decision_mode": seed.get("decision_mode", "normal"),
            },
            "trace": {
                "residual_risk": seed.get("residual_risk", "unknown"),
                "rollback_condition": seed.get("rollback_condition", "manual revert"),
                "audit_pointer": seed.get("audit_pointer"),
            },
        },
        "seed_hash": stable_hash(seed_json),
        "generated_at": now,
    }
    return payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile a context.yaml for YSS M0.")
    parser.add_argument("--input", help="Path to a JSON/YAML seed.")
    parser.add_argument("--output", help="Output path for context.yaml.")
    parser.add_argument("--task", help="Override task string.")
    parser.add_argument("--objective", help="Override objective string.")
    parser.add_argument("--domain", help="Override domain.")
    parser.add_argument("--decision-mode", default=None)
    parser.add_argument(
        "--run-dir",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "run", "execution")),
        help="Base run directory for outputs.",
    )
    return parser


def _resolve_output(path: Optional[str], run_dir: str) -> str:
    if path:
        return os.path.abspath(path)
    run_id = _generate_run_id()
    return os.path.join(run_dir, run_id, "context.yaml")


def _generate_run_id() -> str:
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%S")
    ms = f"{int(now.microsecond / 1000):03d}"
    suffix = uuid.uuid4().hex[:6]
    return f"{stamp}{ms}Z_{suffix}"


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    seed = dict(DEFAULT_CONTEXT_SEED)
    if args.input:
        seed.update(_load_seed(args.input))
    if args.task:
        seed["task"] = args.task
    if args.objective:
        seed["objective"] = args.objective
    if args.domain:
        seed["domain"] = args.domain
    if args.decision_mode:
        seed["decision_mode"] = args.decision_mode

    output_path = _resolve_output(args.output, args.run_dir)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    payload = compile_context(seed)
    with open(output_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)
    return {"context": output_path}


if __name__ == "__main__":
    paths = main()
    print(f"context.yaml: {paths['context']}")
