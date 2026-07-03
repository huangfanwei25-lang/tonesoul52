"""Tests for scripts/aegis_reanchor.py — the provenance-preserving head repair.

The tool must (1) do nothing when intact, (2) repair ONLY the benign shape
(chain valid + no signature failures + head!=tail) and leave a chained
aegis_reanchor event recording the old head, (3) refuse anything else.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import tonesoul.aegis_shield as aegis_shield  # noqa: E402
from scripts.aegis_reanchor import diagnose_gap, reanchor  # noqa: E402
from tonesoul.aegis_shield import AegisShield  # noqa: E402
from tonesoul.backends.file_store import FileStore  # noqa: E402


def _make_store(tmp_path, monkeypatch) -> FileStore:
    # Keep ALL aegis side effects (chain_head.txt, keys/) inside tmp_path.
    monkeypatch.setattr(aegis_shield, "_AEGIS_DIR", tmp_path / ".aegis")
    return FileStore(
        gov_path=tmp_path / "gov.json",
        traces_path=tmp_path / "traces.jsonl",
        zones_path=tmp_path / "zones.json",
        claims_path=tmp_path / "claims.json",
    )


def _seed_chain(store: FileStore, n: int = 2) -> AegisShield:
    shield = AegisShield.load(store)
    for i in range(n):
        protected, check = shield.protect_trace(
            {"type": "test_trace", "seq": i, "agent": "tester"}, "tester"
        )
        assert check.severity != "blocked"
        store.append_trace(protected)
    shield.save(store)
    return shield


def test_intact_chain_is_left_alone(tmp_path, monkeypatch):
    store = _make_store(tmp_path, monkeypatch)
    shield = _seed_chain(store)
    result = reanchor(store, shield, "tester", "unit test", apply=True)
    assert result["status"] == "intact"
    assert result["applied"] is False
    assert store.get_traces(n=100)[-1]["type"] == "test_trace"


def test_benign_gap_dry_run_writes_nothing(tmp_path, monkeypatch):
    store = _make_store(tmp_path, monkeypatch)
    _seed_chain(store)
    stale = AegisShield(chain_head="0" * 64)
    stale.save(store)
    before_lines = len(store.get_traces(n=100))

    result = reanchor(store, AegisShield.load(store), "tester", "unit test", apply=False)
    assert result["status"] == "reanchor_gap"
    assert result["applied"] is False
    assert len(store.get_traces(n=100)) == before_lines
    # stored head untouched
    assert AegisShield.load(store).chain_head == "0" * 64


def test_benign_gap_apply_reanchors_with_provenance(tmp_path, monkeypatch):
    store = _make_store(tmp_path, monkeypatch)
    shield = _seed_chain(store)
    real_tail = shield.chain_head
    stale = AegisShield(chain_head="0" * 64)
    stale.save(store)

    result = reanchor(store, AegisShield.load(store), "tester", "unit test", apply=True)
    assert result["status"] == "reanchored"
    assert result["applied"] is True
    assert result["after"]["integrity"] == "intact"

    traces = store.get_traces(n=100)
    event = traces[-1]
    assert event["type"] == "aegis_reanchor"
    assert event["old_stored_head"] == "0" * 64  # the gap stays on record
    assert event["reanchored_to_tail"] == real_tail
    assert event["_chain"]["prev_hash"] == real_tail  # chained onto the truth
    # follow-up audit by a fresh load agrees
    assert AegisShield.load(store).audit(store)["integrity"] == "intact"


def test_broken_chain_is_refused(tmp_path, monkeypatch):
    store = _make_store(tmp_path, monkeypatch)
    _seed_chain(store)
    # Corrupt the first entry's payload so the chain hash no longer verifies.
    lines = store.traces_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["seq"] = 999
    lines[0] = json.dumps(first, ensure_ascii=False)
    store.traces_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    before_lines = len(store.get_traces(n=100))
    result = reanchor(store, AegisShield.load(store), "tester", "unit test", apply=True)
    assert result["status"] == "unsafe"
    assert result["applied"] is False
    assert len(store.get_traces(n=100)) == before_lines  # refused = untouched


def test_diagnose_gap_shapes():
    assert diagnose_gap({"integrity": "intact"}) == "intact"
    assert (
        diagnose_gap(
            {
                "integrity": "compromised",
                "chain_valid": True,
                "signature_failures": [],
                "head_matches_tail": False,
            }
        )
        == "reanchor_gap"
    )
    assert (
        diagnose_gap(
            {
                "integrity": "compromised",
                "chain_valid": False,
                "signature_failures": [],
                "head_matches_tail": False,
            }
        )
        == "unsafe"
    )
    assert (
        diagnose_gap(
            {
                "integrity": "compromised",
                "chain_valid": True,
                "signature_failures": [{"entry": 0}],
                "head_matches_tail": False,
            }
        )
        == "unsafe"
    )
