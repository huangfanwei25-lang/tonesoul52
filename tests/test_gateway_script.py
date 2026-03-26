from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_gateway_module():
    module_name = "test_gateway_script_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "gateway.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_gateway_registers_packet_route() -> None:
    module = _load_gateway_module()
    assert "/packet" in module.ROUTES_GET
    assert "/claims" in module.ROUTES_GET
    assert "/claim" in module.ROUTES_POST
    assert "/release" in module.ROUTES_POST
    assert "/compact" in module.ROUTES_POST


def test_handle_packet_returns_r_memory_packet(monkeypatch) -> None:
    module = _load_gateway_module()
    captured = {}

    def fake_send_json(handler, data, status=200):
        captured["data"] = data
        captured["status"] = status

    monkeypatch.setattr(module, "_send_json", fake_send_json)
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.r_memory_packet",
        lambda: {"contract_version": "v1", "backend": "redis"},
    )

    module.handle_packet(object())

    assert captured["status"] == 200
    assert captured["data"] == {"contract_version": "v1", "backend": "redis"}


def test_handle_claim_and_release_proxy_runtime_claims(monkeypatch) -> None:
    module = _load_gateway_module()
    captured = []
    payload_iter = iter(
        [
            {"task_id": "task-1", "agent": "codex", "summary": "sync", "paths": ["a.py"]},
            {"task_id": "task-1", "agent": "codex"},
        ]
    )

    monkeypatch.setattr(module, "_parse_json", lambda handler: next(payload_iter))
    monkeypatch.setattr(
        module,
        "_send_json",
        lambda handler, data, status=200: captured.append({"status": status, "data": data}),
    )
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.claim_task",
        lambda task_id, agent_id, summary="", paths=None, source="direct", ttl_seconds=1800: {
            "ok": True,
            "task_id": task_id,
            "claim": {"agent": agent_id, "summary": summary, "paths": paths or []},
            "backend": "redis",
        },
    )
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.release_task_claim",
        lambda task_id, agent_id=None: {"ok": True, "task_id": task_id, "backend": "redis"},
    )

    module.handle_claim(object())
    module.handle_release(object())

    assert captured[0]["status"] == 200
    assert captured[0]["data"]["backend"] == "redis"
    assert captured[1]["status"] == 200
    assert captured[1]["data"]["task_id"] == "task-1"


def test_handle_compact_proxies_runtime_compaction(monkeypatch) -> None:
    module = _load_gateway_module()
    captured = {}
    payload = {
        "agent": "codex",
        "session_id": "sess-44",
        "summary": "Bounded resumability summary.",
        "carry_forward": ["keep compaction non-canonical"],
        "pending_paths": ["scripts/gateway.py"],
        "evidence_refs": [
            "docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md"
        ],
        "next_action": "teach gateway consumers to prefer packet",
    }

    monkeypatch.setattr(module, "_parse_json", lambda handler: payload)
    monkeypatch.setattr(
        module,
        "_send_json",
        lambda handler, data, status=200: captured.update({"status": status, "data": data}),
    )
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.write_compaction",
        lambda **kwargs: {
            "agent": kwargs["agent_id"],
            "summary": kwargs["summary"],
            "source": kwargs["source"],
        },
    )

    module.handle_compact(object())

    assert captured["status"] == 200
    assert captured["data"]["agent"] == "codex"
    assert captured["data"]["source"] == "gateway"
