"""Guard the layer-boundary honesty introduced in Reality Sync PR 5.

Context: the 2026-06-12 audit showed ALLOWED_DEPS had been widened until
~52% of ordered layer pairs were legal, including bidirectional pairs that
make "0 layer_violations" a bookkeeping result, not a strong-hierarchy
guarantee. PR 5 (option b) chose honest naming over silent widening: the
bidirectional pairs are now enumerated in ACCEPTED_INVERSIONS with a
justification each.

These tests make any FUTURE silent widening fail CI:
- a new bidirectional layer pair that is not in ACCEPTED_INVERSIONS, or
- an ACCEPTED_INVERSIONS entry without a justification.

This does not enforce a hierarchy (that is option c, deferred). It enforces
that inversions stay *declared and justified* — accountability via structure,
which is the project's own thesis applied to its own dependency rules.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ACG_PATH = Path(__file__).resolve().parent.parent / "scripts" / "analyze_codebase_graph.py"


def _load_acg():
    spec = importlib.util.spec_from_file_location("acg_under_test", _ACG_PATH)
    mod = importlib.util.module_from_spec(spec)
    # Register before exec: the analyzer uses @dataclass + `from __future__
    # import annotations`; dataclass field resolution needs the module visible
    # in sys.modules under its own name during exec, or it raises on _KW_ONLY.
    sys.modules["acg_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _bidirectional_pairs(allowed_deps: dict[str, set[str]]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for a, targets in allowed_deps.items():
        for b in targets:
            if a != b and a in allowed_deps.get(b, set()):
                pairs.add(tuple(sorted((a, b))))
    return pairs


def test_bidirectional_edges_match_accepted_inversions():
    acg = _load_acg()
    actual = _bidirectional_pairs(acg.ALLOWED_DEPS)
    declared = {tuple(sorted(k)) for k in acg.ACCEPTED_INVERSIONS}
    undeclared = actual - declared
    stale = declared - actual
    assert not undeclared, (
        "ALLOWED_DEPS gained bidirectional layer pair(s) not declared in "
        f"ACCEPTED_INVERSIONS: {sorted(undeclared)}. Either justify the "
        "inversion by adding it (with a real reason) or re-tighten the rule to "
        "one-way. Silent widening is the failure mode this guard exists to stop."
    )
    assert not stale, (
        "ACCEPTED_INVERSIONS lists pair(s) that are no longer bidirectional in "
        f"ALLOWED_DEPS: {sorted(stale)}. Remove the stale entries — an inversion "
        "ledger that over-states is as dishonest as one that hides."
    )


def test_every_accepted_inversion_has_a_justification():
    acg = _load_acg()
    empty = [k for k, v in acg.ACCEPTED_INVERSIONS.items() if not (v and v.strip())]
    assert not empty, f"ACCEPTED_INVERSIONS entries without justification: {empty}"
