from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

import tonesoul.true_verification_summary as _tv_summary  # noqa: E402
from tonesoul.status_alignment import build_dream_weekly_alignment_line  # noqa: E402

summarize_long_run_payload = _tv_summary.summarize_long_run_payload
summarize_schedule_payload = _tv_summary.summarize_schedule_payload

DEFAULT_TASK_NAME = "ToneSoul True Verification Weekly"
DEFAULT_STATUS_PATH = (
    "docs/status/true_verification_weekly/true_verification_task_status_latest.json"
)
DEFAULT_INSTALL_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_task_scheduler_install_latest.json"
)
DEFAULT_TEMPLATE_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_task_scheduler_latest.json"
)
DEFAULT_HOST_TICK_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_host_tick_latest.json"
)
DEFAULT_EXPERIMENT_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_experiment_latest.json"
)
DEFAULT_SCHEDULE_SNAPSHOT_PATH = (
    "docs/status/true_verification_weekly/autonomous_registry_schedule_latest.json"
)
DEFAULT_DREAM_OBSERVABILITY_PATH = "docs/status/dream_observability_latest.json"
DEFAULT_SUBJECTIVITY_REVIEW_PATH = "docs/status/subjectivity_review_batch_latest.json"
TASK_NS = {"task": "http://schemas.microsoft.com/windows/2004/02/mit/task"}


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report live Windows Task Scheduler status for the weekly True Verification task."
    )
    parser.add_argument(
        "--task-name",
        type=str,
        default=DEFAULT_TASK_NAME,
        help="Task Scheduler display name to query",
    )
    parser.add_argument(
        "--status-path",
        type=str,
        default=DEFAULT_STATUS_PATH,
        help="Where to write the task status snapshot JSON",
    )
    parser.add_argument(
        "--install-summary-path",
        type=str,
        default=DEFAULT_INSTALL_SUMMARY_PATH,
        help="Installer summary artifact to include when present",
    )
    parser.add_argument(
        "--template-summary-path",
        type=str,
        default=DEFAULT_TEMPLATE_SUMMARY_PATH,
        help="Task template summary artifact to include when present",
    )
    parser.add_argument(
        "--host-tick-summary-path",
        type=str,
        default=DEFAULT_HOST_TICK_SUMMARY_PATH,
        help="Latest host tick summary artifact to include when present",
    )
    parser.add_argument(
        "--experiment-summary-path",
        type=str,
        default=DEFAULT_EXPERIMENT_SUMMARY_PATH,
        help="Latest weekly experiment summary artifact to include when present",
    )
    parser.add_argument(
        "--schedule-snapshot-path",
        type=str,
        default=DEFAULT_SCHEDULE_SNAPSHOT_PATH,
        help="Latest weekly schedule snapshot artifact to include when present",
    )
    parser.add_argument(
        "--dream-observability-path",
        type=str,
        default=DEFAULT_DREAM_OBSERVABILITY_PATH,
        help="Latest dream observability status artifact to compare when present",
    )
    parser.add_argument(
        "--subjectivity-review-path",
        type=str,
        default=DEFAULT_SUBJECTIVITY_REVIEW_PATH,
        help="Latest subjectivity review status artifact to mirror when present",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when the task cannot be queried successfully",
    )
    return parser


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_optional_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_summary(path: Path, *, kind: str) -> dict[str, object] | None:
    payload = _read_optional_json(path)
    if not isinstance(payload, dict):
        return payload
    if kind == "long_run":
        return summarize_long_run_payload(payload)
    if kind == "schedule":
        return summarize_schedule_payload(payload)
    return payload


def _admissibility_primary_status_line(
    subjectivity_review_payload: dict[str, object] | None,
) -> str:
    if not isinstance(subjectivity_review_payload, dict):
        return ""
    line = str(subjectivity_review_payload.get("admissibility_primary_status_line") or "").strip()
    if line:
        return line
    handoff = subjectivity_review_payload.get("handoff")
    if isinstance(handoff, dict):
        return str(handoff.get("admissibility_primary_status_line") or "").strip()
    return ""


def _host_trigger_mode(host_tick_summary: dict[str, object] | None) -> str | None:
    if not isinstance(host_tick_summary, dict):
        return None
    experiment = host_tick_summary.get("experiment")
    if not isinstance(experiment, dict):
        return None
    mode = experiment.get("host_trigger_mode")
    if isinstance(mode, str) and mode.strip():
        return mode
    return None


def _extract_runtime_lineage(
    schedule_summary: dict[str, object] | None,
) -> dict[str, object] | None:
    if not isinstance(schedule_summary, dict):
        return None
    latest_result = schedule_summary.get("latest_result")
    if not isinstance(latest_result, dict):
        return None

    autonomous_payload = (
        latest_result.get("autonomous_payload")
        if isinstance(latest_result.get("autonomous_payload"), dict)
        else {}
    )
    runtime_state = (
        autonomous_payload.get("runtime_state")
        if isinstance(autonomous_payload.get("runtime_state"), dict)
        else {}
    )
    tension_budget = (
        latest_result.get("tension_budget")
        if isinstance(latest_result.get("tension_budget"), dict)
        else {}
    )
    observation = (
        tension_budget.get("observation")
        if isinstance(tension_budget.get("observation"), dict)
        else {}
    )

    lineage: dict[str, object] = {}
    if latest_result.get("cycle") is not None:
        lineage["cycle"] = latest_result.get("cycle")
    if latest_result.get("overall_ok") is not None:
        lineage["result_overall_ok"] = bool(latest_result.get("overall_ok"))
    if schedule_summary.get("overall_ok") is not None:
        lineage["schedule_overall_ok"] = bool(schedule_summary.get("overall_ok"))
    if runtime_state.get("session_id") is not None:
        lineage["session_id"] = runtime_state.get("session_id")
    if "resumed" in runtime_state:
        lineage["session_resumed"] = bool(runtime_state.get("resumed"))
    for key in ("next_cycle", "consecutive_failures", "state_path"):
        value = runtime_state.get(key)
        if value is not None:
            lineage[key] = value
    if tension_budget.get("status") is not None:
        lineage["tension_status"] = tension_budget.get("status")
    if observation.get("max_consecutive_failure_count") is not None:
        lineage["max_consecutive_failure_count"] = observation.get("max_consecutive_failure_count")
    return lineage or None


def _extract_scribe_handoff(
    schedule_summary: dict[str, object] | None,
) -> dict[str, object] | None:
    if not isinstance(schedule_summary, dict):
        return None
    latest_result = schedule_summary.get("latest_result")
    if not isinstance(latest_result, dict):
        return None

    autonomous_payload = (
        latest_result.get("autonomous_payload")
        if isinstance(latest_result.get("autonomous_payload"), dict)
        else {}
    )
    wakeup_summary = (
        autonomous_payload.get("wakeup_summary")
        if isinstance(autonomous_payload.get("wakeup_summary"), dict)
        else {}
    )

    handoff: dict[str, object] = {}
    for key in (
        "overall_status",
        "result_count",
        "latest_cycle",
        "latest_status",
        "scribe_evaluated",
        "scribe_triggered",
        "scribe_status",
        "scribe_generation_mode",
        "scribe_state_document_posture",
        "scribe_anchor_status_line",
        "scribe_problem_route_status_line",
        "scribe_problem_route_secondary_labels",
        "scribe_latest_available_source",
        "scribe_skip_reason",
    ):
        value = wakeup_summary.get(key)
        if value is not None:
            handoff[key] = value
    return handoff or None


def _scheduler_state(runtime_payload: dict[str, object] | None) -> str:
    if not isinstance(runtime_payload, dict):
        return "unknown"
    state = str(runtime_payload.get("State") or "").strip()
    return state or "unknown"


def _bool_word(value: object) -> str:
    return "yes" if bool(value) else "no"


def _runtime_status_line(source: str | None, lineage: dict[str, object] | None) -> str:
    normalized_source = str(source or "none").strip() or "none"
    if not isinstance(lineage, dict):
        return f"{normalized_source} | runtime_lineage=unavailable"

    session_id = str(lineage.get("session_id") or "n/a")
    next_cycle = lineage.get("next_cycle")
    failures = lineage.get("consecutive_failures")
    max_failures = lineage.get("max_consecutive_failure_count")
    tension_status = str(lineage.get("tension_status") or "n/a")
    return (
        f"{normalized_source} | session={session_id} resumed={_bool_word(lineage.get('session_resumed'))} "
        f"next_cycle={next_cycle if next_cycle is not None else 'n/a'} "
        f"failures={failures if failures is not None else 'n/a'} "
        f"max_failure={max_failures if max_failures is not None else 'n/a'} "
        f"tension={tension_status}"
    )


def _scribe_handoff_has_signal(handoff: dict[str, object] | None) -> bool:
    if not isinstance(handoff, dict):
        return False
    for key in (
        "scribe_status",
        "scribe_generation_mode",
        "scribe_state_document_posture",
        "scribe_anchor_status_line",
        "scribe_problem_route_status_line",
        "scribe_problem_route_secondary_labels",
        "scribe_latest_available_source",
    ):
        if str(handoff.get(key) or "").strip():
            return True
    return bool(handoff.get("scribe_evaluated")) or bool(handoff.get("scribe_triggered"))


def _scribe_status_line(source: str | None, handoff: dict[str, object] | None) -> str:
    normalized_source = str(source or "none").strip() or "none"
    if not isinstance(handoff, dict):
        return f"{normalized_source} | scribe=unavailable"

    status = str(handoff.get("scribe_status") or "n/a")
    generation_mode = str(handoff.get("scribe_generation_mode") or "n/a")
    posture = str(handoff.get("scribe_state_document_posture") or "n/a")
    latest_source = str(handoff.get("scribe_latest_available_source") or "n/a")
    skip_reason = str(handoff.get("scribe_skip_reason") or "none")
    return (
        f"{normalized_source} | status={status} mode={generation_mode} "
        f"posture={posture} source={latest_source} "
        f"triggered={_bool_word(handoff.get('scribe_triggered'))} skip={skip_reason}"
    )


def _scribe_anchor_status_line(source: str | None, handoff: dict[str, object] | None) -> str:
    normalized_source = str(source or "none").strip() or "none"
    if not isinstance(handoff, dict):
        return ""

    anchor_line = str(handoff.get("scribe_anchor_status_line") or "").strip()
    if not anchor_line:
        return ""
    return f"{normalized_source} | {anchor_line}"


def _scribe_problem_route_status_line(source: str | None, handoff: dict[str, object] | None) -> str:
    normalized_source = str(source or "none").strip() or "none"
    if not isinstance(handoff, dict):
        return ""

    route_line = str(handoff.get("scribe_problem_route_status_line") or "").strip()
    if not route_line:
        return ""
    if route_line.startswith("route | "):
        route_line = route_line[len("route | ") :]
    return f"{normalized_source} | {route_line}"


def _scribe_problem_route_secondary_labels(
    handoff: dict[str, object] | None,
) -> str:
    if not isinstance(handoff, dict):
        return ""
    return str(handoff.get("scribe_problem_route_secondary_labels") or "").strip()


def _artifact_policy_status_line(
    *,
    host_trigger_mode: str | None,
    experiment_summary_included: bool,
    ignored_reason: str | None,
) -> str:
    mode = str(host_trigger_mode or "unknown").strip() or "unknown"
    status = "included" if experiment_summary_included else "ignored"
    reason = str(ignored_reason or "none").strip() or "none"
    return f"host_trigger_mode={mode} | experiment_summary={status} reason={reason}"


def _runtime_lineage_has_signal(lineage: dict[str, object] | None) -> bool:
    if not isinstance(lineage, dict):
        return False
    if str(lineage.get("session_id") or "").strip():
        return True
    for key in (
        "next_cycle",
        "consecutive_failures",
        "max_consecutive_failure_count",
        "tension_status",
    ):
        value = lineage.get(key)
        if value not in (None, "", "n/a"):
            return True
    return False


def _primary_status_line(
    *,
    overall_ok: bool,
    task_registered: bool,
    runtime_payload: dict[str, object] | None,
    host_trigger_mode: str | None,
    latest_runtime_source: str | None,
    lineage: dict[str, object] | None,
) -> str:
    headline = "task_ready" if overall_ok and task_registered else "task_attention"
    session_id = "n/a"
    resumed = "no"
    if isinstance(lineage, dict):
        session_id = str(lineage.get("session_id") or "n/a")
        resumed = _bool_word(lineage.get("session_resumed"))
    mode = str(host_trigger_mode or "unknown").strip() or "unknown"
    source = str(latest_runtime_source or "none").strip() or "none"
    return (
        f"{headline} | scheduler={_scheduler_state(runtime_payload)} "
        f"registered={_bool_word(task_registered)} host_trigger_mode={mode} "
        f"runtime_source={source} session={session_id} resumed={resumed}"
    )


def _decode_output(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "cp950", sys.getdefaultencoding()):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _query_task_xml(task_name: str) -> tuple[bool, str]:
    completed = subprocess.run(
        ["schtasks", "/Query", "/TN", task_name, "/XML"],
        capture_output=True,
        check=False,
    )
    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    if completed.returncode != 0:
        return False, stderr or stdout
    return True, stdout


def _powershell_task_runtime_command(task_name: str) -> str:
    escaped_name = task_name.replace("'", "''")
    return (
        "$ErrorActionPreference='Stop'; "
        f"$task=Get-ScheduledTask -TaskName '{escaped_name}'; "
        f"$info=Get-ScheduledTaskInfo -TaskName '{escaped_name}'; "
        "[pscustomobject]@{"
        "TaskName=$task.TaskName; "
        "TaskPath=$task.TaskPath; "
        "State=[string]$task.State; "
        "Enabled=[bool]$task.Settings.Enabled; "
        "LastRunTime=$info.LastRunTime.ToString('o'); "
        "NextRunTime=$info.NextRunTime.ToString('o'); "
        "LastTaskResult=$info.LastTaskResult; "
        "NumberOfMissedRuns=$info.NumberOfMissedRuns"
        "} | ConvertTo-Json -Compress"
    )


def _query_task_runtime_info(task_name: str) -> tuple[bool, dict[str, object] | str]:
    completed = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            _powershell_task_runtime_command(task_name),
        ],
        capture_output=True,
        check=False,
    )
    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    if completed.returncode != 0:
        return False, stderr or stdout
    return True, json.loads(stdout)


def _xml_text(root: ET.Element, path: str) -> str | None:
    node = root.find(path, TASK_NS)
    if node is None or node.text is None:
        return None
    return node.text


def _parse_task_xml(xml_payload: str) -> dict[str, object]:
    root = ET.fromstring(xml_payload)
    return {
        "author": _xml_text(root, "task:RegistrationInfo/task:Author"),
        "description": _xml_text(root, "task:RegistrationInfo/task:Description"),
        "uri": _xml_text(root, "task:RegistrationInfo/task:URI"),
        "start_boundary": _xml_text(root, "task:Triggers/task:CalendarTrigger/task:StartBoundary"),
        "interval": _xml_text(
            root, "task:Triggers/task:CalendarTrigger/task:Repetition/task:Interval"
        ),
        "duration": _xml_text(
            root, "task:Triggers/task:CalendarTrigger/task:Repetition/task:Duration"
        ),
        "stop_at_duration_end": _xml_text(
            root,
            "task:Triggers/task:CalendarTrigger/task:Repetition/task:StopAtDurationEnd",
        ),
        "execution_time_limit": _xml_text(root, "task:Settings/task:ExecutionTimeLimit"),
        "multiple_instances_policy": _xml_text(root, "task:Settings/task:MultipleInstancesPolicy"),
        "command": _xml_text(root, "task:Actions/task:Exec/task:Command"),
        "arguments": _xml_text(root, "task:Actions/task:Exec/task:Arguments"),
        "working_directory": _xml_text(root, "task:Actions/task:Exec/task:WorkingDirectory"),
    }


def report_task_status(args: argparse.Namespace) -> dict[str, object]:
    xml_ok, xml_payload = _query_task_xml(str(args.task_name))
    runtime_ok, runtime_payload = _query_task_runtime_info(str(args.task_name))
    host_tick_summary = _read_optional_json(Path(args.host_tick_summary_path))
    host_trigger_mode = _host_trigger_mode(host_tick_summary)
    ignore_experiment_summary = host_trigger_mode == "single_tick"
    overall_ok = bool(xml_ok and runtime_ok)
    task_registered = bool(xml_ok and runtime_ok)
    artifacts = {
        "install_summary": _read_optional_summary(Path(args.install_summary_path), kind="raw"),
        "template_summary": _read_optional_summary(
            Path(args.template_summary_path),
            kind="raw",
        ),
        "host_tick_summary": summarize_long_run_payload(host_tick_summary),
        "experiment_summary": (
            None
            if ignore_experiment_summary
            else _read_optional_summary(Path(args.experiment_summary_path), kind="long_run")
        ),
        "schedule_snapshot": _read_optional_summary(
            Path(args.schedule_snapshot_path),
            kind="schedule",
        ),
    }
    host_tick_runtime_lineage = _extract_runtime_lineage(
        (
            artifacts["host_tick_summary"].get("schedule")
            if isinstance(artifacts.get("host_tick_summary"), dict)
            else None
        )
    )
    host_tick_scribe_handoff = _extract_scribe_handoff(
        (
            artifacts["host_tick_summary"].get("schedule")
            if isinstance(artifacts.get("host_tick_summary"), dict)
            else None
        )
    )
    schedule_snapshot_runtime_lineage = _extract_runtime_lineage(
        (
            artifacts["schedule_snapshot"]
            if isinstance(artifacts.get("schedule_snapshot"), dict)
            else None
        )
    )
    schedule_snapshot_scribe_handoff = _extract_scribe_handoff(
        (
            artifacts["schedule_snapshot"]
            if isinstance(artifacts.get("schedule_snapshot"), dict)
            else None
        )
    )
    latest_runtime_source = None
    latest_runtime_lineage = None
    if _runtime_lineage_has_signal(schedule_snapshot_runtime_lineage):
        latest_runtime_source = "schedule_snapshot"
        latest_runtime_lineage = schedule_snapshot_runtime_lineage
    elif _runtime_lineage_has_signal(host_tick_runtime_lineage):
        latest_runtime_source = "host_tick"
        latest_runtime_lineage = host_tick_runtime_lineage
    latest_scribe_source = None
    latest_scribe_handoff = None
    if latest_runtime_source == "schedule_snapshot" and _scribe_handoff_has_signal(
        schedule_snapshot_scribe_handoff
    ):
        latest_scribe_source = "schedule_snapshot"
        latest_scribe_handoff = schedule_snapshot_scribe_handoff
    elif latest_runtime_source == "host_tick" and _scribe_handoff_has_signal(
        host_tick_scribe_handoff
    ):
        latest_scribe_source = "host_tick"
        latest_scribe_handoff = host_tick_scribe_handoff
    elif _scribe_handoff_has_signal(schedule_snapshot_scribe_handoff):
        latest_scribe_source = "schedule_snapshot"
        latest_scribe_handoff = schedule_snapshot_scribe_handoff
    elif _scribe_handoff_has_signal(host_tick_scribe_handoff):
        latest_scribe_source = "host_tick"
        latest_scribe_handoff = host_tick_scribe_handoff
    experiment_summary_included = not ignore_experiment_summary
    experiment_summary_ignored_reason = (
        "host_tick_single_tick_mode" if ignore_experiment_summary else None
    )
    artifact_policy_status_line = _artifact_policy_status_line(
        host_trigger_mode=host_trigger_mode,
        experiment_summary_included=experiment_summary_included,
        ignored_reason=experiment_summary_ignored_reason,
    )
    runtime_status_line = _runtime_status_line(latest_runtime_source, latest_runtime_lineage)
    scribe_status_line = _scribe_status_line(latest_scribe_source, latest_scribe_handoff)
    anchor_status_line = _scribe_anchor_status_line(latest_scribe_source, latest_scribe_handoff)
    problem_route_status_line = _scribe_problem_route_status_line(
        latest_scribe_source, latest_scribe_handoff
    )
    problem_route_secondary_labels = _scribe_problem_route_secondary_labels(latest_scribe_handoff)
    dream_observability_preview = _read_optional_json(Path(args.dream_observability_path))
    subjectivity_review_preview = _read_optional_json(Path(args.subjectivity_review_path))
    dream_weekly_alignment_line = build_dream_weekly_alignment_line(
        {
            "problem_route_status_line": problem_route_status_line,
            "problem_route_secondary_labels": problem_route_secondary_labels,
        },
        dream_observability_preview if isinstance(dream_observability_preview, dict) else None,
    )
    admissibility_primary_status_line = _admissibility_primary_status_line(
        subjectivity_review_preview if isinstance(subjectivity_review_preview, dict) else None
    )
    primary_status_line = _primary_status_line(
        overall_ok=overall_ok,
        task_registered=task_registered,
        runtime_payload=(
            runtime_payload if runtime_ok and isinstance(runtime_payload, dict) else None
        ),
        host_trigger_mode=host_trigger_mode,
        latest_runtime_source=latest_runtime_source,
        lineage=latest_runtime_lineage if isinstance(latest_runtime_lineage, dict) else None,
    )
    result: dict[str, object] = {
        "overall_ok": overall_ok,
        "task_name": str(args.task_name),
        "task_registered": task_registered,
        "scheduler_runtime": runtime_payload if runtime_ok else None,
        "task_contract": _parse_task_xml(xml_payload) if xml_ok else None,
        "errors": {
            "xml": None if xml_ok else xml_payload,
            "runtime": None if runtime_ok else runtime_payload,
        },
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "scribe_status_line": scribe_status_line,
        "anchor_status_line": anchor_status_line,
        "problem_route_status_line": problem_route_status_line,
        "problem_route_secondary_labels": problem_route_secondary_labels,
        "dream_weekly_alignment_line": dream_weekly_alignment_line,
        "artifact_policy_status_line": artifact_policy_status_line,
        "admissibility_primary_status_line": admissibility_primary_status_line,
        "handoff": {
            "queue_shape": "weekly_host_status",
            "primary_status_line": primary_status_line,
            "scribe_status_line": scribe_status_line,
            "anchor_status_line": anchor_status_line,
            "problem_route_status_line": problem_route_status_line,
            "artifact_policy_status_line": artifact_policy_status_line,
            "requires_operator_action": not overall_ok,
        },
        "artifact_policy": {
            "host_trigger_mode": host_trigger_mode,
            "experiment_summary": {
                "included": experiment_summary_included,
                "ignored_reason": experiment_summary_ignored_reason,
            },
        },
        "artifacts": artifacts,
        "runtime_lineage": {
            "latest_available_source": latest_runtime_source,
            "host_tick": host_tick_runtime_lineage,
            "schedule_snapshot": schedule_snapshot_runtime_lineage,
        },
        "scribe_handoff": {
            "latest_available_source": latest_scribe_source,
            "host_tick": host_tick_scribe_handoff,
            "schedule_snapshot": schedule_snapshot_scribe_handoff,
        },
    }
    if problem_route_secondary_labels:
        result["handoff"]["problem_route_secondary_labels"] = problem_route_secondary_labels
    if dream_weekly_alignment_line:
        result["handoff"]["dream_weekly_alignment_line"] = dream_weekly_alignment_line
    if admissibility_primary_status_line:
        result["handoff"]["admissibility_primary_status_line"] = admissibility_primary_status_line
    _write_json(Path(args.status_path), result)
    return result


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    payload = report_task_status(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
