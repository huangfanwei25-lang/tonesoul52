from __future__ import annotations

import json
from pathlib import Path

from tonesoul.inter_soul.sovereignty import SovereigntyGuard


def _write_axioms(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_build_boundary_maps_p0_axioms_to_non_negotiable_fields(tmp_path: Path) -> None:
    axioms_path = tmp_path / "AXIOMS.json"
    _write_axioms(
        axioms_path,
        {
            "axioms": [
                {"id": 3, "priority": "P0"},
                {"id": 4, "priority": "P2"},
                {"id": 6, "priority": "P0"},
            ]
        },
    )

    boundary = SovereigntyGuard(str(axioms_path)).build_boundary()

    assert boundary.non_negotiable_fields == frozenset({"zone", "lambda_state"})
    assert boundary.axiom_ids == frozenset({"3", "6"})


def test_build_boundary_supports_list_style_axiom_payloads(tmp_path: Path) -> None:
    axioms_path = tmp_path / "AXIOMS.json"
    _write_axioms(axioms_path, [{"id": "3"}, {"id": "6"}])

    boundary = SovereigntyGuard(str(axioms_path)).build_boundary()

    assert boundary.non_negotiable_fields == frozenset({"zone", "lambda_state"})
    assert boundary.axiom_ids == frozenset({"3", "6"})


def test_check_violation_returns_protected_field_name(tmp_path: Path) -> None:
    axioms_path = tmp_path / "AXIOMS.json"
    _write_axioms(axioms_path, [{"id": "3"}])
    guard = SovereigntyGuard(str(axioms_path))

    assert guard.check_violation({"zone": "risk"}) == "zone"


def test_check_violation_ignores_non_protected_fields(tmp_path: Path) -> None:
    axioms_path = tmp_path / "AXIOMS.json"
    _write_axioms(axioms_path, [{"id": "3"}])
    guard = SovereigntyGuard(str(axioms_path))

    assert guard.check_violation({"signals": {"semantic_delta": 0.9}}) is None
