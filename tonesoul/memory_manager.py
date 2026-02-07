import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import yaml

from .ystm.schema import stable_hash, utc_now


@dataclass
class RunPointers:
    run_id: str
    run_path: str
    context: Optional[str]
    frame_plan: Optional[str]
    constraints: Optional[str]
    action_set: Optional[str]
    mercy_objective: Optional[str]
    council_summary: Optional[str]
    execution_report: Optional[str]
    audit_request: Optional[str]
    gate_report: Optional[str]
    error_ledger: Optional[str]
    evidence_summary: Optional[str]
    tsr_metrics: Optional[str]
    dcs_result: Optional[str]
    ystm_nodes: Optional[str]
    ystm_audit: Optional[str]
    ystm_diff: Optional[str]
    ystm_terrain: Optional[str]
    ystm_terrain_svg: Optional[str]
    ystm_terrain_png: Optional[str]
    ystm_terrain_json: Optional[str]
    ystm_terrain_p2: Optional[str]
    ystm_terrain_p2_svg: Optional[str]
    ystm_terrain_p2_png: Optional[str]
    ystm_terrain_p2_json: Optional[str]
    tech_trace_capture: Optional[str]
    tech_trace_normalize: Optional[str]


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _memory_root() -> str:
    return os.path.join(_workspace_root(), "memory")


def _ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)


def _file_hash(path: str) -> Optional[str]:
    if not path or not os.path.exists(path):
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()[:12]


def _file_info(path: Optional[str]) -> Dict[str, object]:
    if not path or not os.path.exists(path):
        return {"path": path, "exists": False}
    return {
        "path": path,
        "exists": True,
        "hash": _file_hash(path),
        "size": os.path.getsize(path),
    }


def _load_yaml(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("YAML payload must be a mapping.")
    return payload


def list_run_dirs(run_root: str) -> List[str]:
    if not run_root or not os.path.isdir(run_root):
        return []
    runs = []
    for name in os.listdir(run_root):
        path = os.path.join(run_root, name)
        if not os.path.isdir(path):
            continue
        if os.path.exists(os.path.join(path, "context.yaml")):
            runs.append(path)
    return sorted(runs)


def collect_run_dirs(run_roots: Iterable[str]) -> List[str]:
    collected: List[str] = []
    seen = set()
    for root in run_roots:
        for path in list_run_dirs(root):
            run_id = os.path.basename(path)
            if run_id in seen:
                continue
            collected.append(path)
            seen.add(run_id)
    return collected


def build_pointers(run_dir: str, ystm_outputs: Optional[Dict[str, str]] = None) -> RunPointers:
    workspace = _workspace_root()
    run_id = os.path.basename(run_dir)

    def path_in_run(filename: str) -> Optional[str]:
        path = os.path.join(run_dir, filename)
        return path if os.path.exists(path) else None

    ystm_outputs = ystm_outputs or {}
    audit_request_path = path_in_run("audit_request.json")
    audit_inputs = _load_audit_inputs(audit_request_path)
    ystm_diff = ystm_outputs.get("diff") or audit_inputs.get("ystm_diff")
    tech_trace_capture = ystm_outputs.get("tech_trace_capture") or audit_inputs.get(
        "tech_trace_capture"
    )
    tech_trace_normalize = ystm_outputs.get("tech_trace_normalize") or audit_inputs.get(
        "tech_trace_normalize"
    )
    return RunPointers(
        run_id=run_id,
        run_path=run_dir,
        context=path_in_run("context.yaml"),
        frame_plan=path_in_run("frame_plan.json"),
        constraints=path_in_run("constraints.md"),
        action_set=path_in_run("action_set.json"),
        mercy_objective=path_in_run("mercy_objective.json"),
        council_summary=path_in_run("council_summary.json"),
        execution_report=path_in_run("execution_report.md"),
        audit_request=audit_request_path,
        gate_report=path_in_run("gate_report.json"),
        error_ledger=path_in_run("error_ledger.jsonl"),
        evidence_summary=os.path.join(workspace, "evidence", "summary.md"),
        tsr_metrics=path_in_run("tsr_metrics.json"),
        dcs_result=path_in_run("dcs_result.json"),
        ystm_nodes=ystm_outputs.get("nodes")
        or os.path.join(workspace, "reports", "ystm_demo", "nodes.json"),
        ystm_audit=ystm_outputs.get("audit")
        or os.path.join(workspace, "reports", "ystm_demo", "audit_log.json"),
        ystm_diff=ystm_diff if isinstance(ystm_diff, str) else None,
        ystm_terrain=ystm_outputs.get("terrain")
        or os.path.join(workspace, "reports", "ystm_demo", "terrain.html"),
        ystm_terrain_svg=ystm_outputs.get("terrain_svg")
        or os.path.join(workspace, "reports", "ystm_demo", "terrain.svg"),
        ystm_terrain_png=ystm_outputs.get("terrain_png")
        or os.path.join(workspace, "reports", "ystm_demo", "terrain.png"),
        ystm_terrain_json=ystm_outputs.get("terrain_json")
        or os.path.join(workspace, "reports", "ystm_demo", "terrain.json"),
        ystm_terrain_p2=ystm_outputs.get("terrain_p2")
        or os.path.join(workspace, "reports", "ystm_demo", "terrain_p2.html"),
        ystm_terrain_p2_svg=ystm_outputs.get("terrain_p2_svg")
        or os.path.join(workspace, "reports", "ystm_demo", "terrain_p2.svg"),
        ystm_terrain_p2_png=ystm_outputs.get("terrain_p2_png")
        or os.path.join(workspace, "reports", "ystm_demo", "terrain_p2.png"),
        ystm_terrain_p2_json=ystm_outputs.get("terrain_p2_json")
        or os.path.join(workspace, "reports", "ystm_demo", "terrain_p2.json"),
        tech_trace_capture=tech_trace_capture if isinstance(tech_trace_capture, str) else None,
        tech_trace_normalize=(
            tech_trace_normalize if isinstance(tech_trace_normalize, str) else None
        ),
    )


def _load_gate_overall(path: Optional[str]) -> Optional[str]:
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        return payload.get("overall")
    return None


def _load_audit_inputs(path: Optional[str]) -> Dict[str, object]:
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    inputs = payload.get("inputs")
    return inputs if isinstance(inputs, dict) else {}


def _load_context_payload(path: Optional[str]) -> Dict[str, object]:
    if not path or not os.path.exists(path):
        return {}
    payload = _load_yaml(path)
    return payload if isinstance(payload, dict) else {}


def _context_fields(payload: Dict[str, object]) -> Dict[str, Optional[str]]:
    context = payload.get("context", {}) if isinstance(payload.get("context"), dict) else {}
    time_island = (
        payload.get("time_island", {}) if isinstance(payload.get("time_island"), dict) else {}
    )
    chronos = time_island.get("chronos", {}) if isinstance(time_island.get("chronos"), dict) else {}
    kairos = time_island.get("kairos", {}) if isinstance(time_island.get("kairos"), dict) else {}
    return {
        "task": context.get("task"),
        "objective": context.get("objective"),
        "domain": context.get("domain"),
        "audience": context.get("audience"),
        "mode": context.get("mode"),
        "decision_mode": kairos.get("decision_mode"),
        "time_stamp": chronos.get("time_stamp"),
        "dependency_basis": chronos.get("dependency_basis"),
    }


def _load_context_timestamp(path: Optional[str]) -> Optional[str]:
    payload = _load_context_payload(path)
    fields = _context_fields(payload)
    return fields.get("time_stamp")


def _ystm_stats(nodes_path: Optional[str], audit_path: Optional[str]) -> Dict[str, object]:
    stats = {"node_count": 0}
    if nodes_path and os.path.exists(nodes_path):
        with open(nodes_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        nodes = payload.get("nodes", []) if isinstance(payload, dict) else []
        stats["node_count"] = len(nodes)
        if nodes:
            totals = [node.get("scalar", {}).get("E_total", 0.0) for node in nodes]
            stats["E_total_mean"] = sum(totals) / len(totals)
            max_idx = max(range(len(totals)), key=lambda idx: totals[idx])
            stats["E_total_max"] = totals[max_idx]
            stats["E_total_max_node"] = nodes[max_idx].get("id")
    if audit_path and os.path.exists(audit_path):
        with open(audit_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        updates = payload.get("updates", []) if isinstance(payload, dict) else []
        stats["audit_update_count"] = len(updates)
    return stats


def _artifact_index(pointers: RunPointers) -> Dict[str, Dict[str, object]]:
    file_paths = {
        "context": pointers.context,
        "frame_plan": pointers.frame_plan,
        "constraints": pointers.constraints,
        "action_set": pointers.action_set,
        "mercy_objective": pointers.mercy_objective,
        "council_summary": pointers.council_summary,
        "execution_report": pointers.execution_report,
        "audit_request": pointers.audit_request,
        "gate_report": pointers.gate_report,
        "error_ledger": pointers.error_ledger,
        "evidence_summary": pointers.evidence_summary,
        "tsr_metrics": pointers.tsr_metrics,
        "dcs_result": pointers.dcs_result,
        "ystm_nodes": pointers.ystm_nodes,
        "ystm_audit": pointers.ystm_audit,
        "ystm_diff": pointers.ystm_diff,
        "ystm_terrain": pointers.ystm_terrain,
        "ystm_terrain_svg": pointers.ystm_terrain_svg,
        "ystm_terrain_png": pointers.ystm_terrain_png,
        "ystm_terrain_json": pointers.ystm_terrain_json,
        "ystm_terrain_p2": pointers.ystm_terrain_p2,
        "ystm_terrain_p2_svg": pointers.ystm_terrain_p2_svg,
        "ystm_terrain_p2_png": pointers.ystm_terrain_p2_png,
        "ystm_terrain_p2_json": pointers.ystm_terrain_p2_json,
        "tech_trace_capture": pointers.tech_trace_capture,
        "tech_trace_normalize": pointers.tech_trace_normalize,
    }
    return {label: _file_info(path) for label, path in file_paths.items() if path}


def build_seed(pointers: RunPointers, archived: bool) -> Dict[str, object]:
    context_payload = _load_context_payload(pointers.context)
    context_fields = _context_fields(context_payload)
    created_at = context_fields.get("time_stamp") or utc_now()
    gate_overall = _load_gate_overall(pointers.gate_report)
    ystm_snapshot = {
        "nodes": _file_info(pointers.ystm_nodes),
        "audit": _file_info(pointers.ystm_audit),
        "semantic_diff": _file_info(pointers.ystm_diff),
        "terrain": _file_info(pointers.ystm_terrain),
        "terrain_svg": _file_info(pointers.ystm_terrain_svg),
        "terrain_png": _file_info(pointers.ystm_terrain_png),
        "terrain_json": _file_info(pointers.ystm_terrain_json),
        "terrain_p2": _file_info(pointers.ystm_terrain_p2),
        "terrain_p2_svg": _file_info(pointers.ystm_terrain_p2_svg),
        "terrain_p2_png": _file_info(pointers.ystm_terrain_p2_png),
        "terrain_p2_json": _file_info(pointers.ystm_terrain_p2_json),
        "shared_output": True,
    }
    tech_trace_snapshot = {
        "capture": _file_info(pointers.tech_trace_capture),
        "normalize": _file_info(pointers.tech_trace_normalize),
    }
    artifact_index = _artifact_index(pointers)
    artifact_hashes = {
        label: info.get("hash")
        for label, info in artifact_index.items()
        if isinstance(info, dict) and info.get("hash")
    }
    task = context_fields.get("task")
    objective = context_fields.get("objective")
    summary_parts = [item for item in (task, objective, context_fields.get("domain")) if item]
    summary_text = " | ".join(summary_parts) if summary_parts else None
    content_hash = _file_hash(pointers.context)
    seed = {
        "seed_version": "0.1",
        "run_id": pointers.run_id,
        "run_path": pointers.run_path,
        "created_at": created_at,
        "gate_overall": gate_overall,
        "archived": archived,
        "metadata": {
            "id": pointers.run_id,
            "chronos": context_fields.get("time_stamp") or created_at,
            "author": "tonesoul52",
            "license": "MIT",
        },
        "provenance": {
            "source": {
                "run_id": pointers.run_id,
                "run_path": pointers.run_path,
                "context": pointers.context,
            },
            "confidence": gate_overall or "unknown",
            "parent_seed": [],
            "artifact_index": artifact_index,
            "artifact_hashes": artifact_hashes,
            "artifact_count": len(artifact_index),
        },
        "content": {
            "title": task or f"Run {pointers.run_id}",
            "body": objective,
            "summary": summary_text,
            "context_vector": None,
        },
        "governance": {
            "canonical": bool(gate_overall == "PASS"),
            "rules": ["gate_overall"],
            "sunset_policy": None,
            "revocation": None,
        },
        "anchor": {
            "content_hash": content_hash,
            "cid": None,
            "event_id": pointers.run_id,
        },
        "sigma_stamp": "T0",
        "state_history": [
            {
                "from": None,
                "to": "T0",
                "event": "seed_created",
                "timestamp": created_at,
            }
        ],
        "context_hash": stable_hash(json.dumps({"run": pointers.run_id, "created_at": created_at})),
        "pointers": {
            "context": pointers.context,
            "frame_plan": pointers.frame_plan,
            "constraints": pointers.constraints,
            "action_set": pointers.action_set,
            "mercy_objective": pointers.mercy_objective,
            "council_summary": pointers.council_summary,
            "execution_report": pointers.execution_report,
            "audit_request": pointers.audit_request,
            "gate_report": pointers.gate_report,
            "error_ledger": pointers.error_ledger,
            "evidence_summary": pointers.evidence_summary,
            "tsr_metrics": pointers.tsr_metrics,
            "dcs_result": pointers.dcs_result,
        },
        "ystm_stats": _ystm_stats(pointers.ystm_nodes, pointers.ystm_audit),
        "ystm_snapshot": ystm_snapshot,
        "tech_trace_snapshot": tech_trace_snapshot,
        "note": "Seed stores hashes and pointers; full artifacts remain in run directories.",
    }
    return seed


def _seed_path(memory_root: str, run_id: str) -> str:
    return os.path.join(memory_root, "seeds", f"{run_id}.json")


def write_seed(memory_root: str, run_id: str, seed: Dict[str, object]) -> str:
    path = _seed_path(memory_root, run_id)
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(seed, handle, indent=2)
    return path


def _graph_template() -> Dict[str, object]:
    return {"generated_at": utc_now(), "nodes": {}, "edges": [], "runs": {}}


def _run_index_template() -> Dict[str, object]:
    return {"generated_at": utc_now(), "runs": []}


def _load_json(path: str, fallback: Dict[str, object]) -> Dict[str, object]:
    if not os.path.exists(path):
        return fallback
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        return payload
    return fallback


def _write_json(path: str, payload: Dict[str, object]) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _add_edge(edges: List[Dict[str, str]], edge: Dict[str, str]) -> None:
    key = f"{edge['from']}|{edge['rel']}|{edge['to']}"
    existing = {f"{e['from']}|{e['rel']}|{e['to']}" for e in edges}
    if key not in existing:
        edges.append(edge)


def record_run(
    run_dir: str,
    ystm_outputs: Optional[Dict[str, str]] = None,
    memory_root: Optional[str] = None,
    archive_root: Optional[str] = None,
) -> Dict[str, str]:
    memory_root = memory_root or _memory_root()
    archive_root = archive_root or os.path.join(_workspace_root(), "..", "archive", "runs")

    pointers = build_pointers(run_dir, ystm_outputs=ystm_outputs)
    archived = os.path.abspath(run_dir).startswith(os.path.abspath(archive_root))
    seed = build_seed(pointers, archived=archived)
    seed_path = write_seed(memory_root, pointers.run_id, seed)

    graph_path = os.path.join(memory_root, "graph_index.json")
    run_index_path = os.path.join(memory_root, "run_index.json")
    graph = _load_json(graph_path, _graph_template())
    run_index = _load_json(run_index_path, _run_index_template())

    run_node_id = f"run:{pointers.run_id}"
    seed_node_id = f"seed:{pointers.run_id}"
    graph["nodes"][run_node_id] = {
        "type": "run",
        "path": pointers.run_path,
        "label": pointers.run_id,
    }
    graph["nodes"][seed_node_id] = {
        "type": "seed",
        "path": seed_path,
        "label": pointers.run_id,
    }
    _add_edge(graph["edges"], {"from": run_node_id, "to": seed_node_id, "rel": "summarized_by"})

    file_paths = {
        "context": pointers.context,
        "frame_plan": pointers.frame_plan,
        "constraints": pointers.constraints,
        "action_set": pointers.action_set,
        "mercy_objective": pointers.mercy_objective,
        "council_summary": pointers.council_summary,
        "execution_report": pointers.execution_report,
        "audit_request": pointers.audit_request,
        "gate_report": pointers.gate_report,
        "error_ledger": pointers.error_ledger,
        "evidence_summary": pointers.evidence_summary,
        "tsr_metrics": pointers.tsr_metrics,
        "dcs_result": pointers.dcs_result,
        "ystm_nodes": pointers.ystm_nodes,
        "ystm_audit": pointers.ystm_audit,
        "ystm_diff": pointers.ystm_diff,
        "ystm_terrain": pointers.ystm_terrain,
        "ystm_terrain_svg": pointers.ystm_terrain_svg,
        "ystm_terrain_png": pointers.ystm_terrain_png,
        "ystm_terrain_json": pointers.ystm_terrain_json,
        "ystm_terrain_p2": pointers.ystm_terrain_p2,
        "ystm_terrain_p2_svg": pointers.ystm_terrain_p2_svg,
        "ystm_terrain_p2_png": pointers.ystm_terrain_p2_png,
        "ystm_terrain_p2_json": pointers.ystm_terrain_p2_json,
        "tech_trace_capture": pointers.tech_trace_capture,
        "tech_trace_normalize": pointers.tech_trace_normalize,
    }
    for label, path in file_paths.items():
        if not path or not os.path.exists(path):
            continue
        file_hash = _file_hash(path)
        node_id = f"file:{file_hash}"
        graph["nodes"][node_id] = {
            "type": "file",
            "path": path,
            "hash": file_hash,
            "label": label,
        }
        _add_edge(graph["edges"], {"from": run_node_id, "to": node_id, "rel": "produced"})
        _add_edge(graph["edges"], {"from": seed_node_id, "to": node_id, "rel": "references"})

    graph["runs"][pointers.run_id] = {
        "path": pointers.run_path,
        "seed": seed_path,
        "archived": archived,
    }
    graph["generated_at"] = utc_now()

    runs_list = [
        item for item in run_index.get("runs", []) if item.get("run_id") != pointers.run_id
    ]
    runs_list.append(
        {
            "run_id": pointers.run_id,
            "path": pointers.run_path,
            "seed": seed_path,
            "created_at": seed.get("created_at"),
            "gate_overall": seed.get("gate_overall"),
            "archived": archived,
        }
    )
    run_index["runs"] = sorted(runs_list, key=lambda item: item.get("created_at", ""))
    run_index["generated_at"] = utc_now()

    _write_json(graph_path, graph)
    _write_json(run_index_path, run_index)
    return {"seed": seed_path, "graph": graph_path, "run_index": run_index_path}


def build_indexes(
    run_dirs: Iterable[str],
    memory_root: Optional[str] = None,
    archive_root: Optional[str] = None,
) -> Dict[str, str]:
    memory_root = memory_root or _memory_root()
    archive_root = archive_root or os.path.join(_workspace_root(), "..", "archive", "runs")
    graph = _graph_template()
    run_index = _run_index_template()

    for run_dir in run_dirs:
        pointers = build_pointers(run_dir)
        archived = os.path.abspath(run_dir).startswith(os.path.abspath(archive_root))
        seed = build_seed(pointers, archived=archived)
        seed_path = write_seed(memory_root, pointers.run_id, seed)

        run_node_id = f"run:{pointers.run_id}"
        seed_node_id = f"seed:{pointers.run_id}"
        graph["nodes"][run_node_id] = {
            "type": "run",
            "path": pointers.run_path,
            "label": pointers.run_id,
        }
        graph["nodes"][seed_node_id] = {
            "type": "seed",
            "path": seed_path,
            "label": pointers.run_id,
        }
        _add_edge(graph["edges"], {"from": run_node_id, "to": seed_node_id, "rel": "summarized_by"})

        file_paths = {
            "context": pointers.context,
            "frame_plan": pointers.frame_plan,
            "constraints": pointers.constraints,
            "action_set": pointers.action_set,
            "mercy_objective": pointers.mercy_objective,
            "council_summary": pointers.council_summary,
            "execution_report": pointers.execution_report,
            "audit_request": pointers.audit_request,
            "gate_report": pointers.gate_report,
            "error_ledger": pointers.error_ledger,
            "evidence_summary": pointers.evidence_summary,
            "tsr_metrics": pointers.tsr_metrics,
            "dcs_result": pointers.dcs_result,
            "ystm_nodes": pointers.ystm_nodes,
            "ystm_audit": pointers.ystm_audit,
            "ystm_diff": pointers.ystm_diff,
            "ystm_terrain": pointers.ystm_terrain,
            "ystm_terrain_svg": pointers.ystm_terrain_svg,
            "ystm_terrain_png": pointers.ystm_terrain_png,
            "ystm_terrain_json": pointers.ystm_terrain_json,
            "ystm_terrain_p2": pointers.ystm_terrain_p2,
            "ystm_terrain_p2_svg": pointers.ystm_terrain_p2_svg,
            "ystm_terrain_p2_png": pointers.ystm_terrain_p2_png,
            "ystm_terrain_p2_json": pointers.ystm_terrain_p2_json,
            "tech_trace_capture": pointers.tech_trace_capture,
            "tech_trace_normalize": pointers.tech_trace_normalize,
        }
        for label, path in file_paths.items():
            if not path or not os.path.exists(path):
                continue
            file_hash = _file_hash(path)
            node_id = f"file:{file_hash}"
            graph["nodes"][node_id] = {
                "type": "file",
                "path": path,
                "hash": file_hash,
                "label": label,
            }
            _add_edge(graph["edges"], {"from": run_node_id, "to": node_id, "rel": "produced"})
            _add_edge(graph["edges"], {"from": seed_node_id, "to": node_id, "rel": "references"})

        graph["runs"][pointers.run_id] = {
            "path": pointers.run_path,
            "seed": seed_path,
            "archived": archived,
        }
        run_index["runs"].append(
            {
                "run_id": pointers.run_id,
                "path": pointers.run_path,
                "seed": seed_path,
                "created_at": seed.get("created_at"),
                "gate_overall": seed.get("gate_overall"),
                "archived": archived,
            }
        )

    graph["generated_at"] = utc_now()
    run_index["generated_at"] = utc_now()
    run_index["runs"] = sorted(run_index["runs"], key=lambda item: item.get("created_at", ""))

    graph_path = os.path.join(memory_root, "graph_index.json")
    run_index_path = os.path.join(memory_root, "run_index.json")
    _write_json(graph_path, graph)
    _write_json(run_index_path, run_index)
    return {"graph": graph_path, "run_index": run_index_path}


def archive_runs(run_root: str, archive_root: str, keep_latest: int) -> List[str]:
    if keep_latest < 0:
        keep_latest = 0
    runs = list_run_dirs(run_root)
    runs_sorted = sorted(runs, reverse=True)
    to_archive = runs_sorted[keep_latest:]
    archived = []
    for path in to_archive:
        run_id = os.path.basename(path)
        dest = os.path.join(archive_root, run_id)
        _ensure_dir(os.path.dirname(dest))
        if os.path.exists(dest):
            dest = os.path.join(archive_root, f"{run_id}_{stable_hash(path)}")
        os.replace(path, dest)
        archived.append(dest)
    return archived
