from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_launch_world_module():
    module_name = "test_launch_world_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "launch_world.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_rebuild_data_prefers_redis_store(monkeypatch, tmp_path: Path) -> None:
    module = _load_launch_world_module()
    module.WORLD_HTML = tmp_path / "world.html"
    module.WORLD_HTML.write_text("<html><head></head><body></body></html>", encoding="utf-8")
    module.GOV_STATE = tmp_path / "governance_state.json"
    module.TRACES = tmp_path / "session_traces.jsonl"
    module.REGISTRY = tmp_path / "zone_registry.json"

    class _FakeStore:
        is_redis = True
        backend_name = "redis"

        def get_state(self):
            return {"session_count": 7, "soul_integral": 1.2}

    class _FakeWorld:
        def to_dict(self):
            return {"zones": [], "total_sessions": 7}

    class _FakeShield:
        @classmethod
        def load(cls, store=None):
            return cls()

        def audit(self, store):
            return {"integrity": "intact"}

    fake_store = _FakeStore()
    module._active_store = fake_store
    calls = {}

    def fake_rebuild_and_save(
        traces_path=None,
        governance_path=None,
        registry_path=None,
        store=None,
    ):
        calls["traces_path"] = traces_path
        calls["governance_path"] = governance_path
        calls["registry_path"] = registry_path
        calls["store"] = store
        return _FakeWorld()

    monkeypatch.setattr("tonesoul.zone_registry.rebuild_and_save", fake_rebuild_and_save)
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.get_recent_visitors", lambda store, n=10: [{"agent": "codex"}]
    )
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    module.rebuild_data()

    assert calls["store"] is fake_store
    assert calls["traces_path"] is None
    assert calls["governance_path"] is None
    assert calls["registry_path"] is None
    assert json.loads(module._gov_json)["session_count"] == 7
    assert "__VISITORS__" in module._html_cache
    assert "__AEGIS__" in module._html_cache


def test_build_server_uses_threading_http_server() -> None:
    module = _load_launch_world_module()

    server = module._build_server(0)
    try:
        assert server.__class__.__name__ == "ThreadingHTTPServer"
    finally:
        server.server_close()


def test_rebuild_data_populates_aegis_for_file_store(monkeypatch, tmp_path: Path) -> None:
    module = _load_launch_world_module()
    module.WORLD_HTML = tmp_path / "world.html"
    module.WORLD_HTML.write_text("<html><head></head><body></body></html>", encoding="utf-8")
    module.GOV_STATE = tmp_path / "governance_state.json"
    module.GOV_STATE.write_text("{}", encoding="utf-8")
    module.TRACES = tmp_path / "session_traces.jsonl"
    module.REGISTRY = tmp_path / "zone_registry.json"

    class _FakeStore:
        is_redis = False
        backend_name = "file"

    class _FakeWorld:
        def to_dict(self):
            return {"zones": [], "total_sessions": 0}

    class _FakeShield:
        @classmethod
        def load(cls, store=None):
            return cls()

        def audit(self, store):
            return {"integrity": "intact", "chain_valid": True, "total_traces": 0}

    module._active_store = _FakeStore()
    monkeypatch.setattr("tonesoul.zone_registry.rebuild_and_save", lambda **kwargs: _FakeWorld())
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    module.rebuild_data()

    assert json.loads(module._aegis_json)["integrity"] == "intact"


def test_handle_redis_event_dedupes_immediate_zone_update(monkeypatch) -> None:
    module = _load_launch_world_module()
    calls = {"rebuild": 0, "push": 0}

    monkeypatch.setattr(
        module, "rebuild_data", lambda: calls.__setitem__("rebuild", calls["rebuild"] + 1)
    )
    monkeypatch.setattr(module, "push_update", lambda: calls.__setitem__("push", calls["push"] + 1))

    assert module._handle_redis_event("governance:updated", now=10.0) == "rebuild"
    assert module._handle_redis_event("zones:updated", now=10.1) == "deduped"
    assert calls == {"rebuild": 1, "push": 1}


def test_handle_redis_event_allows_standalone_zone_refresh(monkeypatch) -> None:
    module = _load_launch_world_module()
    calls = {"rebuild": 0, "push": 0}

    monkeypatch.setattr(
        module, "rebuild_data", lambda: calls.__setitem__("rebuild", calls["rebuild"] + 1)
    )
    monkeypatch.setattr(module, "push_update", lambda: calls.__setitem__("push", calls["push"] + 1))

    module._last_governance_refresh_at = 0.0
    assert module._handle_redis_event("zones:updated", now=5.0) == "rebuild"
    assert calls == {"rebuild": 1, "push": 1}
