"""Lock-in for the AXIOMS.json enforcement reconciliation (Reality Sync PR 3).

History: before 2026-06-13 the repo carried axioms whose enforcement
reality ranged from fully wired to declared-only, while external docs
described them uniformly as runtime invariants. This test locks the
honest per-axiom enforcement metadata in place: every axiom must carry
an explicit status, and the status vocabulary cannot drift silently.
"""

from __future__ import annotations

import json
from pathlib import Path

AXIOMS_PATH = Path(__file__).resolve().parent.parent / "AXIOMS.json"
ALLOWED_STATUSES = {"enforced", "partial", "referenced", "aspirational"}


def _load() -> dict:
    return json.loads(AXIOMS_PATH.read_text(encoding="utf-8"))


def test_every_axiom_declares_enforcement_status():
    data = _load()
    missing = []
    for axiom in data["axioms"]:
        enf = axiom.get("enforcement")
        if not isinstance(enf, dict) or enf.get("status") not in ALLOWED_STATUSES:
            missing.append(axiom.get("id"))
    assert not missing, (
        f"Axioms without a valid enforcement.status {sorted(ALLOWED_STATUSES)}: {missing}. "
        "If you added or rewired an axiom, update its enforcement block in the same "
        "commit — undeclared enforcement is how docs drift back into overclaim."
    )


def test_existential_principle_declares_enforcement_status():
    data = _load()
    enf = data["existential_principle"].get("enforcement")
    assert isinstance(enf, dict) and enf.get("status") in ALLOWED_STATUSES


def test_enforcement_notes_and_dates_present():
    data = _load()
    for axiom in data["axioms"]:
        enf = axiom["enforcement"]
        assert enf.get("note"), f"Axiom {axiom['id']} enforcement.note is empty"
        assert enf.get("as_of"), f"Axiom {axiom['id']} enforcement.as_of is empty"


def test_reconciliation_meta_block_present():
    data = _load()
    recon = data["meta"].get("enforcement_reconciliation")
    assert isinstance(recon, dict)
    scale = recon.get("status_scale")
    assert isinstance(scale, dict) and set(scale) == ALLOWED_STATUSES, (
        "status_scale must define exactly the allowed statuses — "
        "changing the vocabulary requires updating this test deliberately."
    )
