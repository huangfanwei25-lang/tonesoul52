import shutil
import uuid
from pathlib import Path

from memory.provenance_chain import ProvenanceManager
from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource


def _make_tmp_dir() -> Path:
    base = Path(__file__).resolve().parents[1] / "memory" / ".tmp_tests"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"provenance_{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _build_db(tmp_dir: Path) -> JsonlSoulDB:
    ledger_path = tmp_dir / "provenance_ledger.jsonl"
    return JsonlSoulDB(source_map={MemorySource.PROVENANCE_LEDGER: ledger_path})


def test_provenance_hash_chain():
    tmp_dir = _make_tmp_dir()
    try:
        db = _build_db(tmp_dir)
        manager = ProvenanceManager(soul_db=db)
        manager.add_record("council_verdict", {"verdict": "approve"})
        manager.add_record("council_verdict", {"verdict": "block"})

        records = list(db.stream(MemorySource.PROVENANCE_LEDGER))
        assert len(records) == 2
        first = records[0].payload
        second = records[1].payload

        assert first.get("hash")
        assert second.get("hash")
        assert second.get("prev_hash") == first.get("hash")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_provenance_load_restores_last_hash():
    tmp_dir = _make_tmp_dir()
    try:
        db = _build_db(tmp_dir)
        manager = ProvenanceManager(soul_db=db)
        manager.add_record("council_verdict", {"verdict": "approve"})

        # New manager should load the last hash and continue the chain.
        manager_reload = ProvenanceManager(soul_db=db)
        manager_reload.add_record("council_verdict", {"verdict": "refine"})

        records = list(db.stream(MemorySource.PROVENANCE_LEDGER))
        assert len(records) == 2
        assert records[1].payload.get("prev_hash") == records[0].payload.get("hash")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
