from __future__ import annotations

from pathlib import Path

from tonesoul.backends.file_store import FileStore
from tonesoul.council.persistence import build_council_verdict_record
from tonesoul.council.runtime import CouncilRequest, CouncilRuntime


def _store(tmp_path: Path) -> FileStore:
    return FileStore(council_verdicts_path=tmp_path / ".aegis" / "council_verdicts.json")


def _request() -> CouncilRequest:
    return CouncilRequest(
        draft_output="Provide a careful answer with explicit evidence posture.",
        context={
            "agent_id": "codex",
            "session_id": "sess-calibration-1",
            "source": "unit_test",
            "tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0},
        },
        user_intent="review this answer path",
    )


def test_file_store_council_verdict_lane_rotates(tmp_path: Path) -> None:
    store = _store(tmp_path)

    store.append_council_verdict({"record_id": "cv-1"}, limit=2, ttl_seconds=60)
    store.append_council_verdict({"record_id": "cv-2"}, limit=2, ttl_seconds=60)
    store.append_council_verdict({"record_id": "cv-3"}, limit=2, ttl_seconds=60)

    saved = store.get_council_verdicts(n=5)

    assert [item["record_id"] for item in saved] == ["cv-3", "cv-2"]


def test_build_council_verdict_record_stays_bounded(monkeypatch, tmp_path: Path) -> None:
    import tonesoul.council.persistence as persistence_module

    store = _store(tmp_path)
    monkeypatch.setattr(persistence_module, "get_store", lambda: store)

    runtime = CouncilRuntime()
    request = _request()
    verdict = runtime.deliberate(request)

    record = build_council_verdict_record(request, verdict)

    assert record["agent"] == "codex"
    assert record["session_id"] == "sess-calibration-1"
    assert record["source"] == "unit_test"
    assert "draft_output" not in record
    assert "user_intent" not in record
    assert record["input_fingerprint"]
    assert record["draft_fingerprint"]
    assert all("reasoning" not in vote for vote in record["vote_profile"])


def test_council_runtime_persists_bounded_verdict_record(monkeypatch, tmp_path: Path) -> None:
    import tonesoul.council.persistence as persistence_module

    store = _store(tmp_path)
    monkeypatch.setattr(persistence_module, "get_store", lambda: store)

    runtime = CouncilRuntime()
    verdict = runtime.deliberate(_request())

    saved = store.get_council_verdicts(n=5)

    assert len(saved) == 1
    assert saved[0]["agent"] == "codex"
    assert saved[0]["session_id"] == "sess-calibration-1"
    assert saved[0]["vote_profile"]
    observability = (verdict.transcript or {}).get("council_persistence")
    assert observability["status"] == "stored"
    assert observability["surface"] == ".aegis/council_verdicts.json"
    assert observability["retention"]["policy"] == "capped_rotation"
    assert observability["retention"]["max_items"] == 1000


def test_council_runtime_reports_persistence_error(monkeypatch) -> None:
    import tonesoul.council.persistence as persistence_module

    def _raise(*args, **kwargs):
        raise RuntimeError("store unavailable")

    monkeypatch.setattr(persistence_module, "persist_council_verdict", _raise)

    runtime = CouncilRuntime()
    verdict = runtime.deliberate(_request())

    observability = (verdict.transcript or {}).get("council_persistence")
    assert observability["status"] == "error"
    assert "store unavailable" in observability["error"]
