"""
Regression tests for tonesoul.observer_window.build_low_drift_anchor

Three required cases (per 3-day plan Day 1):
  1. clean_stable_case      — all surfaces present, fresh, no hazards
  2. conflicting_continuity — compaction promotion hazard + claim collision
  3. stale_carry_forward    — stale compaction + absent evidence readout

Tests do NOT call any network, filesystem, or subprocess.
All inputs are synthesised dicts that mirror real packet/import_posture shapes.
"""

from __future__ import annotations

from tonesoul.hot_memory import build_canonical_center
from tonesoul.observer_window import build_low_drift_anchor
from tonesoul.subsystem_parity import build_subsystem_parity_readout

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_packet(
    *,
    launch_tier: str = "collaborator_beta",
    public_launch_ready: bool = False,
    launch_default: str = "file-backed",
    has_evidence_readout: bool = True,
    delta_new_compactions: int = 0,
    delta_new_checkpoints: int = 0,
    delta_new_traces: int = 0,
    first_observation: bool = True,
    has_coord_mode: bool = True,
    repo_head: str = "abc123",
    repo_dirty_count: int = 0,
    repo_change_changed: bool = False,
    repo_previous_head: str = "",
    repo_previous_dirty_count: int = 0,
) -> dict:
    evidence_readout: dict = (
        {"present": True, "tiers": ["tested", "runtime_present"]} if has_evidence_readout else {}
    )
    coord_mode: dict = (
        {"launch_default_mode": launch_default, "launch_alignment": "aligned"}
        if has_coord_mode
        else {}
    )
    return {
        "coordination_mode": coord_mode,
        "project_memory_summary": {
            "launch_claim_posture": {
                "current_tier": launch_tier,
                "public_launch_ready": public_launch_ready,
            },
            "evidence_readout_posture": evidence_readout,
            "repo_progress": {
                "head": repo_head,
                "dirty_count": repo_dirty_count,
            },
        },
        "delta_feed": {
            "first_observation": first_observation,
            "new_compactions": [{"id": f"c{i}"} for i in range(delta_new_compactions)],
            "new_checkpoints": [{"id": f"ck{i}"} for i in range(delta_new_checkpoints)],
            "new_traces": [{"id": f"t{i}"} for i in range(delta_new_traces)],
            "repo_change": {
                "changed": repo_change_changed,
                "previous_head": repo_previous_head,
                "current_head": repo_head,
                "previous_dirty_count": repo_previous_dirty_count,
                "current_dirty_count": repo_dirty_count,
            },
        },
    }


def _make_import_posture(
    *,
    posture_importable: bool = True,
    compaction_present: bool = True,
    compaction_freshness_hours: float = 12.0,
    compaction_hazards: list | None = None,
    compaction_obligation: str = "should_consider",
    compaction_closeout_status: str = "",
    compaction_stop_reason: str = "",
    compaction_unresolved_count: int = 0,
    compaction_human_input_required: bool = False,
    trace_present: bool = True,
    trace_freshness_hours: float = 6.0,
    snapshot_present: bool = True,
    snapshot_freshness_hours: float = 24.0,
    evidence_present: bool = True,
    council_present: bool = True,
    council_calibration: str = "descriptive_only",
    council_suppression_flag: bool = False,
    ws_observability_status: str = "reinforced",
) -> dict:
    compaction_hazards = compaction_hazards or []
    return {
        "posture": {
            "present": True,
            "import_posture": "directly_importable" if posture_importable else "advisory",
        },
        "readiness": {
            "present": True,
            "import_posture": "directly_importable",
        },
        "compactions": {
            "present": compaction_present,
            "import_posture": "advisory",
            "freshness_hours": compaction_freshness_hours if compaction_present else None,
            "promotion_hazards": compaction_hazards,
            "receiver_obligation": compaction_obligation,
            "closeout_status": compaction_closeout_status,
            "stop_reason": compaction_stop_reason,
            "unresolved_count": compaction_unresolved_count,
            "human_input_required": compaction_human_input_required,
        },
        "recent_traces": {
            "present": trace_present,
            "import_posture": "advisory",
            "freshness_hours": trace_freshness_hours if trace_present else None,
        },
        "subject_snapshot": {
            "present": snapshot_present,
            "import_posture": "advisory",
            "freshness_hours": snapshot_freshness_hours if snapshot_present else None,
        },
        "evidence_readout": {
            "present": evidence_present,
            "import_posture": "advisory",
        },
        "council_dossier": {
            "present": council_present,
            "import_posture": "advisory",
            "dossier_interpretation": (
                {
                    "calibration_status": council_calibration,
                    **({"evolution_suppression_flag": True} if council_suppression_flag else {}),
                }
                if council_present
                else {}
            ),
        },
        "working_style": {
            "present": True,
            "import_posture": "advisory",
            "working_style_observability": {
                "status": ws_observability_status,
                "receiver_note": f"working style status is {ws_observability_status}",
            },
        },
    }


def _make_readiness(
    *, claim_conflict_count: int = 0, status: str = "pass", risk_level: str = "low"
) -> dict:
    return {
        "status": status,
        "ready": status == "pass",
        "risk_level": risk_level,
        "claim_conflict_count": claim_conflict_count,
        "other_agent_claims": [],
    }


def _make_canonical_center(*short_board_items: str) -> dict:
    items = list(short_board_items or ("Phase 743: hot-memory ladder readout",))
    task_text = "\n".join(
        [
            "# Task",
            "",
            "## Water-Bucket Snapshot",
            "- Current short board:",
            *[f"  - {item}" for item in items],
            "- After that:",
            "  - rotate to the next shortest board",
        ]
    )
    return build_canonical_center(task_text=task_text)


def _make_subsystem_parity(*, packet: dict, import_posture: dict, readiness: dict) -> dict:
    return build_subsystem_parity_readout(
        project_memory_summary=packet.get("project_memory_summary") or {},
        import_posture={
            "receiver_rule": "ack/apply/promote ladder visible",
            "surfaces": import_posture,
        },
        readiness=readiness,
        task_track_hint={
            "suggested_track": "feature_track",
            "claim_recommendation": "required",
        },
        working_style_validation={"status": "caution"},
        mutation_preflight={
            "summary_text": "shared_code=claim_before_shared_edits",
            "next_followup": {"target": "task_board.parking_preflight"},
        },
        canonical_center=_make_canonical_center("Phase 743: hot-memory ladder readout"),
    )


# ---------------------------------------------------------------------------
# Case 1: Clean stable state
# ---------------------------------------------------------------------------


class TestCleanStableCase:
    """
    All surfaces present, fresh, no hazards.
    Expect: meaningful stable items, council always contested (by design),
            no stale items, delta reflects first observation.
    """

    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(first_observation=True),
            import_posture=_make_import_posture(),
            readiness=_make_readiness(),
        )

    def test_has_required_keys(self):
        assert "stable" in self.anchor
        assert "contested" in self.anchor
        assert "stale" in self.anchor
        assert "delta_summary" in self.anchor
        assert "closeout_attention" in self.anchor
        assert "consumer_contract" in self.anchor
        assert "generated_at" in self.anchor
        assert "receiver_note" in self.anchor
        assert "summary_text" in self.anchor
        assert "counts" in self.anchor

    def test_consumer_contract_lifts_first_hop_order(self):
        consumer_contract = self.anchor["consumer_contract"]
        assert consumer_contract["present"] is True
        assert consumer_contract["required_read_order"][0]["surface"] == "readiness"
        assert consumer_contract["required_read_order"][1]["surface"] == "canonical_center"
        assert consumer_contract["required_read_order"][2]["surface"] == "closeout_attention"
        assert any(
            guard["name"] == "working_style_not_identity"
            for guard in consumer_contract["misread_guards"]
        )
        assert consumer_contract["priority_misread_guard"]["name"] == "observer_stable_not_verified"
        assert (
            consumer_contract["priority_misread_guard"]["trigger_surface"]
            == "observer_window.stable"
        )

    def test_surface_versioning_stays_visible(self):
        surface_versioning = self.anchor["surface_versioning"]
        assert surface_versioning["present"] is True
        assert surface_versioning["runtime_surfaces"][1]["surface"] == "observer_window"
        assert surface_versioning["consumer_shells"][2]["consumer"] == "claude_style_shell"

    def test_stable_has_items(self):
        assert len(self.anchor["stable"]) >= 1, "Expected at least one stable item in clean state"

    def test_launch_tier_in_stable(self):
        claims = [item["claim"] for item in self.anchor["stable"]]
        assert any(
            "collaborator_beta" in c for c in claims
        ), "Expected collaborator_beta launch tier in stable items"

    def test_file_backed_in_stable(self):
        claims = [item["claim"] for item in self.anchor["stable"]]
        assert any(
            "file-backed" in c for c in claims
        ), "Expected file-backed backend in stable items"

    def test_council_always_contested(self):
        # Council calibration is always contested by design
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert any(
            "descriptive_only" in c or "council" in c for c in contested_claims
        ), "Expected council to be contested even in clean state"

    def test_no_stale_items_in_clean_state(self):
        # All surfaces fresh and present → stale bucket should be empty
        assert (
            len(self.anchor["stale"]) == 0
        ), f"Expected no stale items in clean state, got: {self.anchor['stale']}"

    def test_delta_first_observation(self):
        delta = self.anchor["delta_summary"]
        assert delta["first_observation"] is True

    def test_closeout_attention_not_lifted_when_complete(self):
        attention = self.anchor["closeout_attention"]
        assert attention["present"] is False
        assert attention["status"] == "complete"
        assert attention["source_family"] == ""
        assert attention["attention_pressures"] == []
        assert attention["operator_action"] == ""

    def test_counts_match_lists(self):
        counts = self.anchor["counts"]
        assert counts["stable"] == len(self.anchor["stable"])
        assert counts["contested"] == len(self.anchor["contested"])
        assert counts["stale"] == len(self.anchor["stale"])

    def test_receiver_note_present(self):
        assert "advisory only" in self.anchor["receiver_note"].lower()

    def test_summary_text_format(self):
        text = self.anchor["summary_text"]
        assert "stable=" in text
        assert "contested=" in text
        assert "stale=" in text
        assert "repo_state=baseline_unset" in text
        assert "closeout_attention=complete" in text

    def test_repo_state_awareness_is_visible(self):
        repo_state = self.anchor["repo_state_awareness"]
        assert repo_state["classification"] == "baseline_unset"
        assert repo_state["misread_risk"] is True
        assert "does not imply" in repo_state["receiver_note"]


# ---------------------------------------------------------------------------
# Case 2: Conflicting continuity
# ---------------------------------------------------------------------------


class TestConflictingContinuityCase:
    """
    Compaction promotion hazard + claim collision.
    Expect: hazard and collision appear in contested bucket.
    """

    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(first_observation=False, delta_new_compactions=1),
            import_posture=_make_import_posture(
                compaction_hazards=["recycled_carry_forward_without_new_evidence"],
                compaction_obligation="must_not_promote",
            ),
            readiness=_make_readiness(claim_conflict_count=2, status="needs_clarification"),
        )

    def test_promotion_hazard_in_contested(self):
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert any(
            "must_not_promote" in c or "carry_forward" in c or "hazard" in c
            for c in contested_claims
        ), f"Expected carry_forward promotion hazard in contested. Got: {contested_claims}"

    def test_claim_collision_in_contested(self):
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert any(
            "claim collision" in c or "conflict" in c for c in contested_claims
        ), f"Expected claim collision in contested. Got: {contested_claims}"

    def test_delta_has_updates(self):
        delta = self.anchor["delta_summary"]
        assert delta["has_updates"] is True
        assert delta["new_compaction_count"] == 1

    def test_stable_still_populated(self):
        # Even in conflict state, stable posture items should remain
        assert len(self.anchor["stable"]) >= 1

    def test_counts_still_correct(self):
        counts = self.anchor["counts"]
        assert counts["contested"] == len(self.anchor["contested"])


class TestBlockedCloseoutCase:
    """
    A blocked compaction closeout should surface as contested even without
    promotion hazards, so later agents do not mistake the handoff for done work.
    """

    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(first_observation=False),
            import_posture=_make_import_posture(
                compaction_closeout_status="blocked",
                compaction_stop_reason="external_blocked",
                compaction_unresolved_count=1,
                compaction_human_input_required=True,
                compaction_obligation="must_review",
            ),
            readiness=_make_readiness(status="needs_clarification"),
        )

    def test_blocked_closeout_in_contested(self):
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert any(
            "closeout is 'blocked'" in c for c in contested_claims
        ), f"Expected blocked closeout in contested. Got: {contested_claims}"

    def test_blocked_closeout_detail_contains_stop_reason(self):
        items = [
            item
            for item in self.anchor["contested"]
            if "closeout is 'blocked'" in item.get("claim", "")
        ]
        assert items
        assert "stop_reason=external_blocked" in items[0].get("detail", "")

    def test_closeout_attention_is_lifted_to_top_level(self):
        attention = self.anchor["closeout_attention"]
        assert attention["present"] is True
        assert attention["status"] == "blocked"
        assert attention["source_family"] == "bounded_handoff_closeout"
        assert "status=blocked" in attention["attention_pressures"]
        assert "human_input_required=true" in attention["attention_pressures"]
        assert "Do not continue shared mutation yet" in attention["operator_action"]
        assert "do not treat the handoff summary as completed work" in attention["summary_text"]
        assert "stop_reason=external_blocked" in attention["detail"]

    def test_summary_text_includes_closeout_attention_status(self):
        assert "closeout_attention=blocked" in self.anchor["summary_text"]


class TestRepoChangedWithoutCoordinationCase:
    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(
                first_observation=False,
                repo_change_changed=True,
                repo_previous_head="old123",
                repo_head="new456",
            ),
            import_posture=_make_import_posture(),
            readiness=_make_readiness(),
        )

    def test_repo_state_awareness_flags_misread_risk(self):
        repo_state = self.anchor["repo_state_awareness"]
        assert repo_state["classification"] == "repo_changed_without_coordination"
        assert repo_state["misread_risk"] is True
        assert "without fresh coordination surfaces" in repo_state["receiver_note"]


# ---------------------------------------------------------------------------
# Case 3: Stale carry-forward
# ---------------------------------------------------------------------------


class TestStaleCarryForwardCase:
    """
    Stale compaction (>72h) + absent evidence readout.
    Expect: items in stale bucket flagging both conditions.
    """

    _STALE_COMPACTION_HOURS = 120.0  # deliberately older than threshold (72h)
    _STALE_TRACE_HOURS = 96.0  # also older than threshold (48h)

    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(has_evidence_readout=False),
            import_posture=_make_import_posture(
                compaction_freshness_hours=self._STALE_COMPACTION_HOURS,
                trace_freshness_hours=self._STALE_TRACE_HOURS,
                evidence_present=False,
            ),
            readiness=_make_readiness(),
        )

    def test_stale_compaction_flagged(self):
        stale_claims = [item["claim"] for item in self.anchor["stale"]]
        assert any(
            "compaction" in c for c in stale_claims
        ), f"Expected stale compaction in stale bucket. Got: {stale_claims}"

    def test_stale_trace_flagged(self):
        stale_claims = [item["claim"] for item in self.anchor["stale"]]
        assert any(
            "trace" in c or "recent_trace" in c for c in stale_claims
        ), f"Expected stale traces in stale bucket. Got: {stale_claims}"

    def test_absent_evidence_readout_flagged(self):
        stale_claims = [item["claim"] for item in self.anchor["stale"]]
        assert any(
            "evidence_readout" in c or "evidence" in c for c in stale_claims
        ), f"Expected absent evidence_readout in stale bucket. Got: {stale_claims}"

    def test_stale_bucket_not_empty(self):
        assert (
            len(self.anchor["stale"]) >= 2
        ), f"Expected at least 2 stale items. Got: {len(self.anchor['stale'])}"

    def test_contested_still_has_council(self):
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert any("council" in c or "descriptive_only" in c for c in contested_claims)

    def test_summary_text_reflects_stale(self):
        text = self.anchor["summary_text"]
        # stale= should be > 0
        import re

        match = re.search(r"stale=(\d+)", text)
        assert match is not None, f"Could not find stale= in summary_text: {text}"
        assert int(match.group(1)) >= 2


# ---------------------------------------------------------------------------
# Case 4: Session-end lifecycle (fresh traces → not stale)
# ---------------------------------------------------------------------------


class TestSessionEndLifecycle:
    """
    After a session-end that wrote fresh compaction + traces, the observer
    window should NOT report traces or compaction as stale.
    """

    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(
                first_observation=False,
                delta_new_compactions=1,
                delta_new_checkpoints=1,
                delta_new_traces=1,
            ),
            import_posture=_make_import_posture(
                compaction_freshness_hours=0.5,  # 30 min old
                trace_freshness_hours=0.5,  # 30 min old
                snapshot_freshness_hours=0.5,
            ),
            readiness=_make_readiness(),
        )

    def test_no_stale_items(self):
        assert (
            len(self.anchor["stale"]) == 0
        ), f"Fresh traces/compaction should not be stale. Got: {self.anchor['stale']}"

    def test_delta_shows_updates(self):
        delta = self.anchor["delta_summary"]
        assert delta["has_updates"] is True
        assert delta["new_compaction_count"] == 1
        assert delta["new_checkpoint_count"] == 1
        assert delta["new_trace_count"] == 1

    def test_stable_items_present(self):
        assert (
            len(self.anchor["stable"]) >= 3
        ), "Expected at least 3 stable items after fresh session-end"

    def test_summary_stale_zero(self):
        assert "stale=0" in self.anchor["summary_text"]


# ---------------------------------------------------------------------------
# Case 5: Concurrent claims (multiple agents, overlapping paths)
# ---------------------------------------------------------------------------


class TestConcurrentClaims:
    """
    Two agents hold claims on overlapping paths.
    The observer should flag this in contested.
    """

    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(first_observation=False),
            import_posture=_make_import_posture(),
            readiness=_make_readiness(claim_conflict_count=2, status="needs_clarification"),
        )

    def test_claim_collision_in_contested(self):
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert any(
            "collision" in c or "conflict" in c for c in contested_claims
        ), f"Expected claim collision in contested. Got: {contested_claims}"

    def test_collision_count_visible(self):
        collisions = [
            item
            for item in self.anchor["contested"]
            if "collision" in item.get("claim", "") or "conflict" in item.get("claim", "")
        ]
        assert len(collisions) >= 1
        detail = collisions[0].get("detail", "")
        assert "2" in detail, f"Expected conflict_count=2 in detail. Got: {detail}"

    def test_stable_still_valid(self):
        assert (
            len(self.anchor["stable"]) >= 1
        ), "Stable items should survive despite claim conflicts"

    def test_stale_unaffected(self):
        # Fresh data — stale should be 0
        assert len(self.anchor["stale"]) == 0


# ---------------------------------------------------------------------------
# Case 6: Working-style fully reinforced
# ---------------------------------------------------------------------------


class TestWorkingStyleReinforced:
    """
    When observability status is 'reinforced', working_style drift should
    NOT appear in contested.
    """

    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(),
            import_posture=_make_import_posture(
                ws_observability_status="reinforced",
            ),
            readiness=_make_readiness(),
        )

    def test_no_drift_in_contested(self):
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert not any(
            "working_style" in c and "drift" in c for c in contested_claims
        ), f"Reinforced working style should NOT have drift in contested. Got: {contested_claims}"

    def test_working_style_partial_in_contested(self):
        """When status is partial, drift SHOULD appear."""
        anchor_partial = build_low_drift_anchor(
            packet=_make_packet(),
            import_posture=_make_import_posture(
                ws_observability_status="partial",
            ),
            readiness=_make_readiness(),
        )
        contested_claims = [item["claim"] for item in anchor_partial["contested"]]
        assert any(
            "working_style" in c for c in contested_claims
        ), f"Partial working style should appear in contested. Got: {contested_claims}"

    def test_stable_count_unchanged(self):
        assert (
            len(self.anchor["stable"]) >= 3
        ), "Stable items should not be affected by working style reinforcement"


# ---------------------------------------------------------------------------
# Case 7: Council evolution suppression flagged
# ---------------------------------------------------------------------------


class TestCouncilSuppressionFlagged:
    """
    When evolution_suppression_flag=True in council dossier interpretation,
    a suppression-note item should appear in contested.
    """

    def setup_method(self):
        self.anchor = build_low_drift_anchor(
            packet=_make_packet(),
            import_posture=_make_import_posture(
                council_calibration="descriptive_only",
                council_suppression_flag=True,
            ),
            readiness=_make_readiness(),
        )

    def test_suppression_note_in_contested(self):
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert any(
            "suppression" in c for c in contested_claims
        ), f"Expected suppression note in contested when evolution_suppression_flag=True. Got: {contested_claims}"

    def test_suppression_note_has_correct_source(self):
        suppression_items = [
            item for item in self.anchor["contested"] if "suppression" in item.get("claim", "")
        ]
        assert suppression_items, "Suppression item not found"
        assert (
            suppression_items[0]["evidence_source"]
            == "import_posture.council_dossier.dossier_interpretation"
        )

    def test_suppression_note_detail(self):
        suppression_items = [
            item for item in self.anchor["contested"] if "suppression" in item.get("claim", "")
        ]
        assert suppression_items[0].get("detail") == "evolution_suppression_flag=True"

    def test_council_calibration_still_present(self):
        # The calibration item should still be there alongside the suppression note
        contested_claims = [item["claim"] for item in self.anchor["contested"]]
        assert any(
            "descriptive_only" in c or "calibrated accuracy" in c for c in contested_claims
        ), "Council calibration item should still appear alongside suppression note"

    def test_no_suppression_when_flag_absent(self):
        """Without suppression flag, no suppression note in contested."""
        anchor_no_flag = build_low_drift_anchor(
            packet=_make_packet(),
            import_posture=_make_import_posture(
                council_calibration="descriptive_only",
                council_suppression_flag=False,
            ),
            readiness=_make_readiness(),
        )
        contested_claims = [item["claim"] for item in anchor_no_flag["contested"]]
        assert not any(
            "suppression" in c for c in contested_claims
        ), f"No suppression note expected when flag is absent. Got: {contested_claims}"


class TestCanonicalCenterAndHotMemoryLadder:
    def setup_method(self):
        packet = _make_packet(first_observation=False)
        import_posture = _make_import_posture(
            compaction_hazards=["recycled_carry_forward_without_new_evidence"],
            compaction_obligation="must_not_promote",
            council_calibration="descriptive_only",
            ws_observability_status="partial",
        )
        readiness = _make_readiness(status="needs_clarification")
        self.anchor = build_low_drift_anchor(
            packet=packet,
            import_posture=import_posture,
            readiness=readiness,
            canonical_center=_make_canonical_center(
                "Phase 743: hot-memory ladder readout",
                "Phase 744: observer-window misread correction",
            ),
            subsystem_parity=_make_subsystem_parity(
                packet=packet,
                import_posture=import_posture,
                readiness=readiness,
            ),
        )

    def test_canonical_center_present(self):
        canonical_center = self.anchor["canonical_center"]
        assert canonical_center["present"] is True
        assert canonical_center["parent_surfaces"] == ["task.md", "DESIGN.md"]
        assert canonical_center["canonical_anchor_references"][0] == "AXIOMS.json"
        assert canonical_center["source_precedence"][0]["layer"] == "canonical_anchors"
        assert canonical_center["current_short_board"]["present"] is True

    def test_canonical_center_exposes_short_board_items(self):
        items = self.anchor["canonical_center"]["current_short_board"]["items"]
        assert items == [
            "Phase 743: hot-memory ladder readout",
            "Phase 744: observer-window misread correction",
        ]

    def test_canonical_center_exposes_successor_correction(self):
        correction = self.anchor["canonical_center"]["successor_correction"]
        assert correction["highest_risk_misread"] == "observer_stable_is_execution_permission"
        assert "confirm live_coordination first" in correction["summary_text"]
        assert "claim_view.claims" in correction["required_checks"]

    def test_hot_memory_ladder_has_expected_layers(self):
        layers = self.anchor["hot_memory_ladder"]["layers"]
        assert [layer["layer"] for layer in layers] == [
            "canonical_center",
            "low_drift_anchor",
            "live_coordination",
            "bounded_handoff",
            "working_identity",
            "replay_review",
        ]

    def test_hot_memory_ladder_marks_canonical_center_stable(self):
        layer = next(
            entry
            for entry in self.anchor["hot_memory_ladder"]["layers"]
            if entry["layer"] == "canonical_center"
        )
        assert layer["status"] == "stable"
        assert layer["receiver_rule"] == "treat_as_parent_truth"

    def test_hot_memory_ladder_marks_handoff_contested_when_not_promotable(self):
        layer = next(
            entry
            for entry in self.anchor["hot_memory_ladder"]["layers"]
            if entry["layer"] == "bounded_handoff"
        )
        assert layer["status"] == "contested"
        assert "must_not_promote" in layer["note"]

    def test_hot_memory_decay_map_quarantines_bounded_handoff(self):
        layer = next(
            entry
            for entry in self.anchor["hot_memory_decay_map"]["layers"]
            if entry["layer"] == "bounded_handoff"
        )
        assert layer["use_posture"] == "quarantine"
        assert layer["compression_posture"] == "compress_with_closeout_guards"

    def test_hot_memory_decay_map_keeps_canonical_center_operational(self):
        layer = next(
            entry
            for entry in self.anchor["hot_memory_decay_map"]["layers"]
            if entry["layer"] == "canonical_center"
        )
        assert layer["use_posture"] == "operational"

    def test_subsystem_parity_is_present(self):
        parity = self.anchor["subsystem_parity"]
        assert parity["present"] is True
        assert parity["counts"]["baseline"] == 3
        assert parity["counts"]["beta_usable"] == 5
        assert parity["counts"]["partial"] == 2
        assert parity["counts"]["deferred"] == 1

    def test_subsystem_parity_marks_observer_window_baseline(self):
        by_name = {item["name"]: item for item in self.anchor["subsystem_parity"]["families"]}
        assert by_name["observer_window"]["status"] == "baseline"
        assert by_name["mutation_preflight_hooks"]["status"] == "beta_usable"
        assert by_name["mutation_preflight_hooks"]["next_bounded_move"] == (
            "task_board.parking_preflight"
        )
