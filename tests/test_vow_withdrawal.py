"""Tests for the decent-exit (withdrawal) semantics revived from the G8 lineage
(docs/plans/vow_withdrawal_gap_study_2026-07-02.md). Shadow-first: these pin that
withdrawal RECORDS and never GATES."""

from __future__ import annotations

from tonesoul.vow_system import DEFAULT_VOWS, Vow, VowRegistry, WithdrawalTerms


def _vow(**kw) -> Vow:
    base = dict(id="ΣVow_T", title="t", description="d", expected={"truthfulness": 0.9})
    base.update(kw)
    return Vow(**base)


def test_withdraw_deactivates_and_records_never_deletes() -> None:
    reg = VowRegistry([_vow()])
    assert reg.withdraw("ΣVow_T", reason="superseded by test", actor="tester") is True
    vow = reg.get("ΣVow_T")
    assert vow is not None and vow.active is False  # deactivated, NOT deleted
    records = reg.withdrawal_records()
    assert len(records) == 1
    rec = records[0]
    assert rec["vow_id"] == "ΣVow_T" and rec["actor"] == "tester"
    assert rec["reason"] == "superseded by test"
    assert rec["withdrawn_at"]  # timestamped (the G8 withdraw() never did this)
    assert reg.get("ΣVow_T") in reg.all_vows()  # provenance stays queryable


def test_withdraw_unknown_vow_returns_false() -> None:
    reg = VowRegistry([_vow()])
    assert reg.withdraw("nope", reason="r", actor="a") is False
    assert reg.withdrawal_records() == []


def test_conditions_cited_recorded_not_validated() -> None:
    # shadow-first: citing conditions that were never declared must still record
    terms = WithdrawalTerms(conditions=["only-this"], repair_owner="module_owner")
    reg = VowRegistry([_vow(withdrawal_terms=terms)])
    assert reg.withdraw("ΣVow_T", reason="r", actor="a", conditions_cited=["something-else"])
    rec = reg.withdrawal_records()[0]
    assert rec["conditions_cited"] == ["something-else"]  # recorded verbatim
    assert rec["terms_snapshot"]["conditions"] == ["only-this"]  # declared terms snapshotted


def test_withdrawn_vow_leaves_enforcement_path() -> None:
    reg = VowRegistry([_vow()])
    assert any(v.id == "ΣVow_T" for v in reg.active_vows())
    reg.withdraw("ΣVow_T", reason="r", actor="a")
    assert not any(v.id == "ΣVow_T" for v in reg.active_vows())  # enforce() skips it


def test_terms_roundtrip_and_backward_compat() -> None:
    terms = WithdrawalTerms(
        conditions=["c1"], repair_owner="system_admin", repair_actions=["a1"], repair_deadline=None
    )
    v = _vow(withdrawal_terms=terms)
    restored = Vow.from_dict(v.to_dict())
    assert restored.withdrawal_terms is not None
    assert restored.withdrawal_terms.repair_owner == "system_admin"
    legacy = Vow.from_dict({"id": "x", "title": "t", "description": "", "expected": {}})
    assert legacy.withdrawal_terms is None  # old serialized vows stay valid


def test_default_vows_declare_exit_terms_per_instance() -> None:
    terms = [v.withdrawal_terms for v in DEFAULT_VOWS]
    assert all(t is not None for t in terms)
    # per-instance construction — the G8 shared-template aliasing hazard must not recur
    assert len({id(t) for t in terms}) == len(terms)
    no_harm = next(v for v in DEFAULT_VOWS if v.id == "ΣVow_003")
    assert no_harm.withdrawal_terms.repair_owner == "system_admin"
    assert any("公理層" in c or "axiom" in c for c in no_harm.withdrawal_terms.conditions)


def test_registry_to_dict_includes_exit_ledger() -> None:
    reg = VowRegistry([_vow()])
    reg.withdraw("ΣVow_T", reason="r", actor="a")
    d = reg.to_dict()
    assert d["withdrawals"][0]["vow_id"] == "ΣVow_T"
    assert d["active_count"] == 0 and d["count"] == 1


def test_registries_do_not_share_default_vow_instances() -> None:
    # codex finding (confirmed live): withdrawing in one registry must not
    # deactivate No-Harm in every other registry in the process
    r1, r2 = VowRegistry(), VowRegistry()
    r1.withdraw("ΣVow_003", reason="t", actor="t")
    assert r1.get("ΣVow_003").active is False
    assert r2.get("ΣVow_003").active is True


def test_exit_ledger_survives_save_load(tmp_path) -> None:
    reg = VowRegistry([_vow()])
    reg.withdraw("ΣVow_T", reason="r", actor="a")
    path = str(tmp_path / "vows.json")
    reg.save(path)
    restored = VowRegistry.from_file(path)
    recs = restored.withdrawal_records()
    assert len(recs) == 1 and recs[0]["actor"] == "a"


def test_withdrawal_records_are_deep_copies() -> None:
    terms = WithdrawalTerms(conditions=["c1"], repair_owner="o")
    reg = VowRegistry([_vow(withdrawal_terms=terms)])
    reg.withdraw("ΣVow_T", reason="r", actor="a", conditions_cited=["x"])
    rec = reg.withdrawal_records()[0]
    rec["conditions_cited"].append("EVIL")
    rec["terms_snapshot"]["conditions"].append("EVIL")
    clean = reg.withdrawal_records()[0]
    assert "EVIL" not in clean["conditions_cited"]
    assert "EVIL" not in clean["terms_snapshot"]["conditions"]


def test_from_dict_string_does_not_split_to_chars() -> None:
    terms = WithdrawalTerms.from_dict({"conditions": "single condition", "repair_owner": None})
    assert terms.conditions == ["single condition"]
    assert terms.repair_owner == ""


def test_inventory_records_withdrawal_without_conviction_impact() -> None:
    from tonesoul.vow_inventory import VowInventory

    inv = VowInventory()
    inv.record_check("ΣVow_T", passed=True, score=0.9, threshold=0.8)
    before = inv.get_state("ΣVow_T").conviction_score
    inv.record_withdrawal("ΣVow_T", reason="superseded", actor="tester")
    assert inv.get_state("ΣVow_T").conviction_score == before  # exit ≠ pass/fail
    events = inv.withdrawal_events()
    assert events[0]["vow_id"] == "ΣVow_T" and events[0]["actor"] == "tester"
    events[0]["reason"] = "EVIL"
    assert inv.withdrawal_events()[0]["reason"] == "superseded"  # copies out


def test_cli_list_renders_withdrawn_tag(capsys, tmp_path) -> None:
    import importlib

    cli = importlib.import_module("tonesoul.cli.main")

    reg = VowRegistry([_vow()])
    reg.withdraw("ΣVow_T", reason="retired in test", actor="tester")
    store = tmp_path / "vow_store.json"
    reg.save(str(store))

    rc = cli._cmd_vows(["--path", str(store)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "WITHDRAWN by tester: retired in test" in out
