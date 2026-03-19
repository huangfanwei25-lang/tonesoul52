from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tonesoul import memory_manager as module


def _write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _write_yaml(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return path


def _context_payload(
    *,
    task: str = "Task",
    objective: str = "Objective",
    domain: str = "testing",
    audience: str = "ops",
    mode: str = "shadow",
    decision_mode: str = "careful",
    time_stamp: str = "2026-03-19T12:00:00Z",
    dependency_basis: str = "weekly",
) -> dict[str, object]:
    return {
        "context": {
            "task": task,
            "objective": objective,
            "domain": domain,
            "audience": audience,
            "mode": mode,
        },
        "time_island": {
            "chronos": {
                "time_stamp": time_stamp,
                "dependency_basis": dependency_basis,
            },
            "kairos": {"decision_mode": decision_mode},
        },
    }


def _make_run(
    base: Path,
    run_id: str,
    *,
    context_payload: dict[str, object] | None = None,
) -> Path:
    run_dir = base / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(run_dir / "context.yaml", context_payload or _context_payload())
    return run_dir


def test_list_run_dirs_returns_sorted_context_directories(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    _make_run(run_root, "run-b")
    _make_run(run_root, "run-a")
    (run_root / "not-a-run").mkdir(parents=True, exist_ok=True)

    assert module.list_run_dirs(str(run_root)) == [
        str(run_root / "run-a"),
        str(run_root / "run-b"),
    ]


def test_list_run_dirs_returns_empty_for_missing_root(tmp_path: Path) -> None:
    assert module.list_run_dirs(str(tmp_path / "missing")) == []


def test_collect_run_dirs_deduplicates_by_run_id(tmp_path: Path) -> None:
    root_a = tmp_path / "runs_a"
    root_b = tmp_path / "runs_b"
    first = _make_run(root_a, "shared-run")
    _make_run(root_b, "shared-run")
    _make_run(root_b, "unique-run")

    collected = module.collect_run_dirs([str(root_a), str(root_b)])

    assert collected == [str(first), str(root_b / "unique-run")]


def test_load_audit_inputs_invalid_json_returns_empty(tmp_path: Path) -> None:
    path = tmp_path / "audit_request.json"
    path.write_text("{not json}", encoding="utf-8")

    assert module._load_audit_inputs(str(path)) == {}


def test_context_fields_extract_nested_values() -> None:
    fields = module._context_fields(
        _context_payload(
            task="Audit task",
            objective="Preserve evidence",
            domain="governance",
            audience="operators",
            mode="assist",
            decision_mode="fast",
            time_stamp="2026-03-19T13:00:00Z",
            dependency_basis="hourly",
        )
    )

    assert fields == {
        "task": "Audit task",
        "objective": "Preserve evidence",
        "domain": "governance",
        "audience": "operators",
        "mode": "assist",
        "decision_mode": "fast",
        "time_stamp": "2026-03-19T13:00:00Z",
        "dependency_basis": "hourly",
    }


def test_ystm_stats_summarizes_nodes_and_audit_updates(tmp_path: Path) -> None:
    nodes_path = _write_json(
        tmp_path / "nodes.json",
        {
            "nodes": [
                {"id": "n1", "scalar": {"E_total": 0.2}},
                {"id": "n2", "scalar": {"E_total": 0.8}},
            ]
        },
    )
    audit_path = _write_json(tmp_path / "audit.json", {"updates": [{"id": 1}, {"id": 2}]})

    stats = module._ystm_stats(str(nodes_path), str(audit_path))

    assert stats["node_count"] == 2
    assert stats["E_total_mean"] == pytest.approx(0.5)
    assert stats["E_total_max"] == 0.8
    assert stats["E_total_max_node"] == "n2"
    assert stats["audit_update_count"] == 2


def test_build_pointers_prefers_explicit_ystm_outputs(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    run_dir = _make_run(workspace / "runs", "run-001")
    _write_json(run_dir / "audit_request.json", {"inputs": {"ystm_diff": "from-audit.json"}})
    _write_json(run_dir / "frame_plan.json", {"steps": 2})
    _write_json(run_dir / "action_set.json", {"actions": ["review"]})
    monkeypatch.setattr(module, "_workspace_root", lambda: str(workspace))

    pointers = module.build_pointers(
        str(run_dir),
        ystm_outputs={
            "nodes": str(workspace / "custom_nodes.json"),
            "audit": str(workspace / "custom_audit.json"),
            "diff": str(workspace / "custom_diff.json"),
            "tech_trace_capture": str(workspace / "capture.json"),
            "tech_trace_normalize": str(workspace / "normalize.json"),
        },
    )

    assert pointers.run_id == "run-001"
    assert pointers.frame_plan == str(run_dir / "frame_plan.json")
    assert pointers.action_set == str(run_dir / "action_set.json")
    assert pointers.ystm_diff == str(workspace / "custom_diff.json")
    assert pointers.tech_trace_capture == str(workspace / "capture.json")
    assert pointers.tech_trace_normalize == str(workspace / "normalize.json")
    assert pointers.evidence_summary == str(workspace / "evidence" / "summary.md")


def test_build_seed_populates_expected_sections(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    run_dir = _make_run(
        workspace / "runs",
        "run-002",
        context_payload=_context_payload(
            task="Memory",
            objective="Index artifacts",
            domain="ops",
            time_stamp="2026-03-19T14:00:00Z",
        ),
    )
    _write_json(run_dir / "gate_report.json", {"overall": "PASS"})
    nodes_path = _write_json(
        workspace / "nodes.json",
        {"nodes": [{"id": "peak", "scalar": {"E_total": 0.9}}]},
    )
    audit_path = _write_json(workspace / "audit.json", {"updates": [{"id": 1}]})
    _write_json(workspace / "diff.json", {"delta": 1})
    monkeypatch.setattr(module, "_workspace_root", lambda: str(workspace))

    pointers = module.build_pointers(
        str(run_dir),
        ystm_outputs={
            "nodes": str(nodes_path),
            "audit": str(audit_path),
            "diff": str(workspace / "diff.json"),
        },
    )
    seed = module.build_seed(pointers, archived=False)

    assert seed["run_id"] == "run-002"
    assert seed["created_at"] == "2026-03-19T14:00:00Z"
    assert seed["gate_overall"] == "PASS"
    assert seed["governance"]["canonical"] is True
    assert seed["content"]["summary"] == "Memory | Index artifacts | ops"
    assert seed["provenance"]["artifact_hashes"]["context"]
    assert seed["ystm_stats"]["node_count"] == 1
    assert seed["ystm_stats"]["E_total_max_node"] == "peak"
    assert seed["ystm_snapshot"]["nodes"]["exists"] is True


def test_write_seed_creates_roundtrip_file(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    seed = {"run_id": "run-003", "value": 1}

    path = module.write_seed(str(memory_root), "run-003", seed)

    assert Path(path).exists()
    assert json.loads(Path(path).read_text(encoding="utf-8"))["run_id"] == "run-003"


def test_record_run_creates_seed_graph_and_run_index(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    run_dir = _make_run(workspace / "runs", "run-004")
    _write_json(run_dir / "gate_report.json", {"overall": "WARN"})
    _write_json(run_dir / "frame_plan.json", {"steps": 1})
    monkeypatch.setattr(module, "_workspace_root", lambda: str(workspace))

    outputs = module.record_run(str(run_dir), memory_root=str(tmp_path / "memory"))

    graph = json.loads(Path(outputs["graph"]).read_text(encoding="utf-8"))
    run_index = json.loads(Path(outputs["run_index"]).read_text(encoding="utf-8"))

    assert Path(outputs["seed"]).exists()
    assert "run:run-004" in graph["nodes"]
    assert "seed:run-004" in graph["nodes"]
    assert any(edge["rel"] == "summarized_by" for edge in graph["edges"])
    assert run_index["runs"][0]["run_id"] == "run-004"
    assert run_index["runs"][0]["gate_overall"] == "WARN"


def test_record_run_replaces_existing_run_entry(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    run_dir = _make_run(workspace / "runs", "run-005")
    monkeypatch.setattr(module, "_workspace_root", lambda: str(workspace))
    memory_root = tmp_path / "memory"

    module.record_run(str(run_dir), memory_root=str(memory_root))
    _write_json(run_dir / "gate_report.json", {"overall": "PASS"})
    outputs = module.record_run(str(run_dir), memory_root=str(memory_root))
    run_index = json.loads(Path(outputs["run_index"]).read_text(encoding="utf-8"))

    assert len(run_index["runs"]) == 1
    assert run_index["runs"][0]["run_id"] == "run-005"
    assert run_index["runs"][0]["gate_overall"] == "PASS"


def test_record_run_marks_archived_when_under_archive_root(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    archive_root = tmp_path / "archive" / "runs"
    run_dir = _make_run(archive_root, "run-006")
    monkeypatch.setattr(module, "_workspace_root", lambda: str(workspace))

    outputs = module.record_run(
        str(run_dir),
        memory_root=str(tmp_path / "memory"),
        archive_root=str(archive_root),
    )
    run_index = json.loads(Path(outputs["run_index"]).read_text(encoding="utf-8"))

    assert run_index["runs"][0]["archived"] is True


def test_build_indexes_sorts_runs_by_created_at(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    run_root = workspace / "runs"
    older = _make_run(
        run_root,
        "run-older",
        context_payload=_context_payload(time_stamp="2026-03-19T10:00:00Z"),
    )
    newer = _make_run(
        run_root,
        "run-newer",
        context_payload=_context_payload(time_stamp="2026-03-19T11:00:00Z"),
    )
    monkeypatch.setattr(module, "_workspace_root", lambda: str(workspace))

    outputs = module.build_indexes(
        [str(newer), str(older)],
        memory_root=str(tmp_path / "memory"),
    )
    run_index = json.loads(Path(outputs["run_index"]).read_text(encoding="utf-8"))

    assert [item["run_id"] for item in run_index["runs"]] == ["run-older", "run-newer"]


def test_archive_runs_keeps_latest_lexicographic_run(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    archive_root = tmp_path / "archive"
    _make_run(run_root, "run-001")
    older = _make_run(run_root, "run-002")
    newest = _make_run(run_root, "run-003")

    archived = module.archive_runs(str(run_root), str(archive_root), keep_latest=1)

    assert str(archive_root / older.name) in archived
    assert str(archive_root / "run-001") in archived
    assert newest.exists()
    assert not older.exists()


def test_archive_runs_suffixes_when_destination_exists(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    archive_root = tmp_path / "archive"
    _make_run(run_root, "run-007")
    existing_dest = archive_root / "run-007"
    existing_dest.parent.mkdir(parents=True, exist_ok=True)
    existing_dest.mkdir()

    archived = module.archive_runs(str(run_root), str(archive_root), keep_latest=0)

    assert len(archived) == 1
    assert archived[0] != str(existing_dest)
    assert Path(archived[0]).exists()
