"""Tests for Soul Persistence — cross-session Ψ integral storage."""

from __future__ import annotations

import json
from pathlib import Path

from tonesoul.soul_persistence import SoulPsiSnapshot, load_psi, save_psi


def test_snapshot_initializes_updated_at() -> None:
    snap = SoulPsiSnapshot()

    assert snap.psi == 0.0
    assert snap.step_count == 0
    assert snap.updated_at != ""


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "psi.json"
    save_psi(psi=0.42, step_count=10, path=path)
    loaded = load_psi(path)
    assert abs(loaded.psi - 0.42) < 1e-9
    assert loaded.step_count == 10
    assert loaded.updated_at != ""


def test_load_missing_file_returns_zero(tmp_path: Path) -> None:
    path = tmp_path / "nonexistent.json"
    loaded = load_psi(path)
    assert loaded.psi == 0.0
    assert loaded.step_count == 0


def test_load_corrupt_file_returns_zero(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("NOT VALID JSON", encoding="utf-8")
    loaded = load_psi(path)
    assert loaded.psi == 0.0


def test_save_creates_parent_dirs(tmp_path: Path) -> None:
    path = tmp_path / "deep" / "nested" / "psi.json"
    save_psi(psi=1.5, step_count=3, path=path)
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["psi"] == 1.5
    assert data["step_count"] == 3


def test_save_overwrites_existing_snapshot(tmp_path: Path) -> None:
    path = tmp_path / "psi.json"
    save_psi(psi=0.2, step_count=2, path=path)

    save_psi(psi=0.9, step_count=9, path=path)
    loaded = load_psi(path)

    assert loaded.psi == 0.9
    assert loaded.step_count == 9


def test_snapshot_to_dict() -> None:
    snap = SoulPsiSnapshot(psi=0.99, step_count=50, updated_at="2026-03-18T00:00:00Z")
    d = snap.to_dict()
    assert d["psi"] == 0.99
    assert d["step_count"] == 50
    assert d["updated_at"] == "2026-03-18T00:00:00Z"


def test_tension_engine_save_load(tmp_path: Path) -> None:
    """TensionEngine.save_persistence / load_persistence roundtrip."""
    from tonesoul.tension_engine import TensionEngine

    engine = TensionEngine()
    # Run a few compute cycles to accumulate Ψ
    for _ in range(5):
        engine.compute(
            text_tension=0.3,
            confidence=0.6,
        )
    psi_after = engine.persistence
    assert psi_after > 0.0

    path = tmp_path / "psi.json"
    engine.save_persistence(path)

    # Create a fresh engine and load the snapshot
    engine2 = TensionEngine()
    assert engine2.persistence == 0.0
    engine2.load_persistence(path)
    assert abs(engine2.persistence - psi_after) < 1e-9


def test_decay_accumulation_correctness() -> None:
    """Verify Ψ formula: Ψ_new = 0.995 × Ψ_prev + 0.10 × T_unified."""
    from tonesoul.tension_engine import TensionEngine

    engine = TensionEngine()
    psi = 0.0
    for _ in range(10):
        result = engine.compute(
            text_tension=0.3,
            confidence=0.7,
        )
        # Manually replicate the formula
        psi = 0.995 * psi + 0.10 * result.total
    assert abs(engine.persistence - psi) < 1e-9
    # After 10 rounds with non-zero tension, Ψ should be positive
    assert engine.persistence > 0.0
