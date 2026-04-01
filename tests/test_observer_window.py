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

from tonesoul.observer_window import build_low_drift_anchor

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
        },
        "delta_feed": {
            "first_observation": first_observation,
            "new_compactions": [{"id": f"c{i}"} for i in range(delta_new_compactions)],
            "new_checkpoints": [{"id": f"ck{i}"} for i in range(delta_new_checkpoints)],
            "new_traces": [{"id": f"t{i}"} for i in range(delta_new_traces)],
        },
    }


def _make_import_posture(
    *,
    posture_importable: bool = True,
    compaction_present: bool = True,
    compaction_freshness_hours: float = 12.0,
    compaction_hazards: list | None = None,
    compaction_obligation: str = "should_consider",
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
        assert "generated_at" in self.anchor
        assert "receiver_note" in self.anchor
        assert "summary_text" in self.anchor
        assert "counts" in self.anchor

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
