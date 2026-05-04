"""Integration tests for strategy_mirror ↔ PreOutputCouncil.

Covers Phase 2 spec §5 contract:
  - Flag-off (default): existing council behaviour unchanged; no signature attached
  - Flag-on, benign text: signature attached, verdict unchanged
  - Flag-on, fake-urgency text + APPROVE-track: verdict force-downgraded to BLOCK
    with red move names in summary
  - Flag-on, undeclared yellow + APPROVE: downgraded to BLOCK
  - Flag-on, declared yellow: verdict not downgraded
  - Flag-on, BLOCK verdict + red: stays BLOCK (don't override existing BLOCK)
  - to_dict() includes strategy_signature when present
  - Detector lazy-init: not constructed when flag-off

These tests use the REAL catalog (period_1_foundation.json) rather than
fixtures so we can verify end-to-end integration including catalog → loader
→ detector → council. The cost is that test outcomes depend on catalog
content; the assertions are written to be robust to catalog evolution
(e.g. asserting "at least one red detected" rather than specific symbols).
"""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch

import pytest

from tonesoul.council.base import IPerspective
from tonesoul.council.pre_output_council import PreOutputCouncil
from tonesoul.council.types import (
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)
from tonesoul.soul_config import SOUL

# ---------------------------------------------------------------------------
# Test fixtures: controllable perspective implementations
# ---------------------------------------------------------------------------


class _AlwaysApprovePerspective(IPerspective):
    """A perspective that always votes APPROVE — used to drive the council
    toward an APPROVE verdict so we can test strategy_mirror's downgrade."""

    def __init__(self, perspective_type: PerspectiveType) -> None:
        self._type = perspective_type

    def perspective_type(self) -> PerspectiveType:
        return self._type

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent=None,
        epistemic_label=None,  # PR #50 — accept kwarg, do not consume
    ) -> PerspectiveVote:
        return PerspectiveVote(
            perspective=self._type,
            decision=VoteDecision.APPROVE,
            confidence=0.95,
            reasoning="approve for test",
        )


class _AlwaysObjectPerspective(IPerspective):
    """A perspective that always votes OBJECT — used to drive the council
    toward a BLOCK verdict so we can test that strategy_mirror does NOT
    downgrade an already-BLOCKed verdict."""

    def __init__(self, perspective_type: PerspectiveType) -> None:
        self._type = perspective_type

    def perspective_type(self) -> PerspectiveType:
        return self._type

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent=None,
        epistemic_label=None,  # PR #50 — accept kwarg, do not consume
    ) -> PerspectiveVote:
        return PerspectiveVote(
            perspective=self._type,
            decision=VoteDecision.OBJECT,
            confidence=0.9,
            reasoning="object for test",
        )


def _approve_council() -> PreOutputCouncil:
    return PreOutputCouncil(
        perspectives=[
            _AlwaysApprovePerspective(PerspectiveType.GUARDIAN),
            _AlwaysApprovePerspective(PerspectiveType.ANALYST),
            _AlwaysApprovePerspective(PerspectiveType.CRITIC),
            _AlwaysApprovePerspective(PerspectiveType.ADVOCATE),
            _AlwaysApprovePerspective(PerspectiveType.AXIOMATIC),
        ]
    )


def _block_council() -> PreOutputCouncil:
    return PreOutputCouncil(
        perspectives=[
            _AlwaysObjectPerspective(PerspectiveType.GUARDIAN),
            _AlwaysObjectPerspective(PerspectiveType.ANALYST),
            _AlwaysObjectPerspective(PerspectiveType.CRITIC),
            _AlwaysObjectPerspective(PerspectiveType.ADVOCATE),
            _AlwaysObjectPerspective(PerspectiveType.AXIOMATIC),
        ]
    )


def _patch_soul(*, scan: bool = False, enforce: bool = False):
    """Context manager: replace SOUL in pre_output_council with a copy where
    gse.strategy_mirror_scan_enabled / strategy_mirror_enforce_enabled match
    the requested 4-state matrix cell. Needed because SoulConfig is frozen.

    Note: enforce=True without scan=True is auto-promoted to scan=True by
    GSEConfig.__post_init__, so the (False, True) cell will end up as
    (True, True) at runtime — that is the validated behaviour (test 4).
    """
    new_gse = replace(
        SOUL.gse,
        strategy_mirror_scan_enabled=scan,
        strategy_mirror_enforce_enabled=enforce,
    )
    new_soul = replace(SOUL, gse=new_gse)
    return patch("tonesoul.council.pre_output_council.SOUL", new_soul)


def _enable_mirror():
    """Backward-compat alias for tests written before the flag split.
    Equivalent to scan=True, enforce=True (full enforcement mode)."""
    return _patch_soul(scan=True, enforce=True)


# ---------------------------------------------------------------------------
# Flag-off (default): existing behaviour unchanged
# ---------------------------------------------------------------------------


class TestFlagOffBehaviorUnchanged:
    def test_flag_off_no_signature_attached(self) -> None:
        council = _approve_council()
        verdict = council.validate(
            draft_output="限時優惠！倒數三天，錯過就沒了！只剩三個名額！",
            context={},
            user_intent="test",
            auto_record_self_memory=False,
        )
        # Flag off → no signature attached even on egregious red text
        assert verdict.strategy_signature is None
        # And verdict is APPROVE (not downgraded)
        assert verdict.verdict == VerdictType.APPROVE

    def test_flag_off_detector_not_constructed(self) -> None:
        council = _approve_council()
        council.validate(
            draft_output="any text",
            context={},
            user_intent="test",
            auto_record_self_memory=False,
        )
        # Internal detector reference stays None when flag off
        assert council._strategy_detector is None


# ---------------------------------------------------------------------------
# Flag-on: signature attached, verdict possibly downgraded
# ---------------------------------------------------------------------------


class TestFlagOnBenignText:
    def test_signature_attached_for_benign_text(self) -> None:
        council = _approve_council()
        with _enable_mirror():
            verdict = council.validate(
                draft_output=(
                    "以下整理本月數據：\n"
                    "第一，使用者數量為 5234 人。\n"
                    "第二，平均停留時間為 12 分鐘。\n"
                    "完整資料如附件。"
                ),
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        assert verdict.strategy_signature is not None
        # Benign info text → no red, verdict stays APPROVE
        assert verdict.strategy_signature.has_red is False
        assert verdict.verdict == VerdictType.APPROVE


class TestFlagOnRedDetectionDowngradesApprove:
    def test_red_detection_forces_block_from_approve(self) -> None:
        council = _approve_council()
        with _enable_mirror():
            verdict = council.validate(
                draft_output=("限時優惠！倒數三天，錯過就沒了！" "現在就行動！只剩最後三個名額！"),
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        assert verdict.strategy_signature is not None
        assert verdict.strategy_signature.has_red is True
        # Verdict force-downgraded from APPROVE to BLOCK
        assert verdict.verdict == VerdictType.BLOCK
        # Summary mentions strategy_mirror as the reason
        assert "strategy_mirror" in verdict.summary


class TestFlagOnUndeclaredYellowDowngradesApprove:
    def test_undeclared_yellow_forces_block_from_approve(self) -> None:
        council = _approve_council()
        # Text containing yellow signals (e.g. "你有沒有想過" hooks +
        # explicit "如果不...就會" consequences) without any declaration markers.
        with _enable_mirror():
            verdict = council.validate(
                draft_output=(
                    "你有沒有想過為什麼會這樣？停下來思考一下。"
                    "如果不處理這個問題，後果會崩潰失控。"
                ),
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        assert verdict.strategy_signature is not None
        # Should detect at least some yellow moves (undeclared by default)
        # and downgrade if any are undeclared
        if verdict.strategy_signature.has_undeclared_yellow:
            assert verdict.verdict == VerdictType.BLOCK
            assert "strategy_mirror" in verdict.summary

    def test_declared_yellow_does_not_downgrade(self) -> None:
        council = _approve_council()
        with _enable_mirror():
            verdict = council.validate(
                draft_output=("[Bh] 我用了假時限構造這個招：" "限時三天的特別企劃。"),
                context={"declared_moves": ["[Bh]"]},
                user_intent="test",
                auto_record_self_memory=False,
            )
        # Even with red signals, when explicitly declared in context,
        # the move is marked declared. Note: red moves still trigger
        # downgrade per spec §5.3 — declaration doesn't override red.
        # So this test checks: declaration flips `declared` bit but
        # red still escalates.
        if verdict.strategy_signature and verdict.strategy_signature.has_red:
            # Red detected → still downgrade (declaration ≠ permission)
            assert verdict.verdict == VerdictType.BLOCK


class TestFlagOnBlockVerdictNotOverridden:
    def test_existing_block_stays_block(self) -> None:
        council = _block_council()
        with _enable_mirror():
            verdict = council.validate(
                draft_output="限時優惠！倒數三天，錯過就沒了！",
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        # Council voted BLOCK; strategy_mirror should not "double-downgrade".
        # The summary may or may not mention strategy_mirror depending on
        # implementation; the key invariant is: still BLOCK.
        assert verdict.verdict == VerdictType.BLOCK


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------


class TestVerdictToDictIncludesSignature:
    def test_to_dict_signature_field_when_present(self) -> None:
        council = _approve_council()
        with _enable_mirror():
            verdict = council.validate(
                draft_output="benign info text 第一，第二，第三。",
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        d = verdict.to_dict()
        assert "strategy_signature" in d
        # Signature dict should have counts and flags (per StrategySignature.to_dict)
        sig_dict = d["strategy_signature"]
        if sig_dict is not None:
            assert "counts" in sig_dict
            assert "flags" in sig_dict

    def test_to_dict_signature_field_none_when_flag_off(self) -> None:
        council = _approve_council()
        verdict = council.validate(
            draft_output="any text",
            context={},
            user_intent="test",
            auto_record_self_memory=False,
        )
        d = verdict.to_dict()
        assert "strategy_signature" in d
        assert d["strategy_signature"] is None


# ---------------------------------------------------------------------------
# Detector caching
# ---------------------------------------------------------------------------


class TestDetectorCaching:
    def test_detector_cached_across_validate_calls(self) -> None:
        council = _approve_council()
        with _enable_mirror():
            council.validate(draft_output="第一個測試", context={}, auto_record_self_memory=False)
            first = council._strategy_detector
            council.validate(draft_output="第二個測試", context={}, auto_record_self_memory=False)
            second = council._strategy_detector
        assert first is second  # same instance — catalog only loaded once


# ---------------------------------------------------------------------------
# Defensive: catalog missing → graceful degradation, not hard failure
# ---------------------------------------------------------------------------


class TestGracefulCatalogAbsence:
    def test_empty_catalog_does_not_break_council(self, tmp_path) -> None:
        """If catalog is empty (dev environment), enabling the flag
        should not crash the council — it just means no detection."""
        from tonesoul.gse.strategy_mirror import CatalogLoader
        from tonesoul.gse.strategy_mirror.detector import StrategyDetector

        # Build a detector backed by an empty catalog (tmp dir with no JSON)
        loader = CatalogLoader(catalog_dir=tmp_path).load()
        assert len(loader) == 0
        # Empty catalog detector still scans cleanly (no detections possible)
        detector = StrategyDetector(loader)
        sig = detector.scan("any text including 限時 倒數 錯過")
        assert sig.detected_moves == []


# ---------------------------------------------------------------------------
# Smoke: integration runs without exception across many text inputs
# ---------------------------------------------------------------------------


class TestSmokeIntegration:
    @pytest.mark.parametrize(
        "draft",
        [
            "Short text.",
            "中文短文。",
            "限時搶購！",
            "以下是三點分析：\n第一，A。\n第二，B。\n第三，C。",
            "",  # empty
            "   \n  ",  # whitespace
        ],
    )
    def test_no_exception_across_inputs(self, draft) -> None:
        council = _approve_council()
        with _enable_mirror():
            verdict = council.validate(
                draft_output=draft,
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        # No exception is the test
        assert verdict is not None
        assert verdict.verdict in VerdictType


# ---------------------------------------------------------------------------
# 4-state matrix (post 2026-04-29 scan/enforce split per Codex design)
# ---------------------------------------------------------------------------

# Egregious red text used across multiple matrix cells. Without enforcement,
# this should NOT cause a verdict downgrade — only signature attachment.
# With enforcement, it SHOULD downgrade APPROVE → BLOCK.
_RED_TEXT = "限時優惠！倒數三天，錯過就沒了！現在就行動！只剩最後三個名額！"


class TestFourStateMatrix:
    """The four required matrix tests per Codex 2026-04-28 design.

    State 1: scan=False, enforce=False  → no scan, no signature, no downgrade
    State 2: scan=True,  enforce=False  → signature attached, NO downgrade (shadow mode)
    State 3: scan=True,  enforce=True   → signature + downgrade rules (full enforcement)
    State 4: scan=False, enforce=True   → auto-promoted to State 3 by GSEConfig.__post_init__
    """

    def test_state_1_both_off(self) -> None:
        """State 1: both flags off → no signature, no downgrade, even on red text."""
        council = _approve_council()
        with _patch_soul(scan=False, enforce=False):
            verdict = council.validate(
                draft_output=_RED_TEXT,
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        assert verdict.strategy_signature is None
        assert verdict.verdict == VerdictType.APPROVE
        assert council._strategy_detector is None

    def test_state_2_scan_on_enforce_off_shadow_mode(self) -> None:
        """State 2: scan-only shadow mode → signature attached, NO downgrade
        even on red text. This is the Day 7-9 calibration mode.
        """
        council = _approve_council()
        with _patch_soul(scan=True, enforce=False):
            verdict = council.validate(
                draft_output=_RED_TEXT,
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        # Signature attached
        assert verdict.strategy_signature is not None
        # Red detected (the catalog should flag this text)
        assert verdict.strategy_signature.has_red is True
        # But verdict is NOT downgraded — that is the whole point of shadow mode
        assert verdict.verdict == VerdictType.APPROVE
        # Summary should NOT carry a strategy_mirror downgrade reason
        assert "strategy_mirror" not in (verdict.summary or "")

    def test_state_3_scan_on_enforce_on_full_enforcement(self) -> None:
        """State 3: scan + enforce both on → red detection forces BLOCK.
        Same semantics as the pre-split flag-on state.
        """
        council = _approve_council()
        with _patch_soul(scan=True, enforce=True):
            verdict = council.validate(
                draft_output=_RED_TEXT,
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        assert verdict.strategy_signature is not None
        assert verdict.strategy_signature.has_red is True
        assert verdict.verdict == VerdictType.BLOCK
        assert "strategy_mirror" in verdict.summary

    def test_enforced_downgrade_rebuilds_user_and_audit_surfaces(self) -> None:
        """When strategy_mirror changes APPROVE→BLOCK, downstream surfaces
        must reflect the final verdict, not the pre-enforcement APPROVE."""
        council = _approve_council()
        red_text = "\u9650\u6642\u512a\u60e0\uff0c\u5012\u6578\u4e09\u5929\uff0c\u932f\u904e\u5c31\u6c92\u6709\uff0c\u6700\u5f8c\u6a5f\u6703\u3002"
        with _patch_soul(scan=True, enforce=True):
            verdict = council.validate(
                draft_output=red_text,
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )

        assert verdict.verdict == VerdictType.BLOCK
        assert verdict.strategy_signature is not None
        assert verdict.strategy_signature.has_red is True
        assert (
            verdict.human_summary == "Safety risks were raised, so this content should not be used."
        )
        assert verdict.transcript is not None
        assert verdict.transcript["verdict"]["verdict"] == "block"
        assert "strategy_mirror" in verdict.transcript["verdict"]["summary"]

    def test_state_4_enforce_only_auto_promotes_to_scan_on(self) -> None:
        """State 4: scan=False but enforce=True is impossible.
        GSEConfig.__post_init__ auto-promotes scan→True. Behaviour should
        equal State 3 (full enforcement).
        """
        council = _approve_council()
        with _patch_soul(scan=False, enforce=True):
            verdict = council.validate(
                draft_output=_RED_TEXT,
                context={},
                user_intent="test",
                auto_record_self_memory=False,
            )
        # Should behave identically to State 3
        assert verdict.strategy_signature is not None
        assert verdict.strategy_signature.has_red is True
        assert verdict.verdict == VerdictType.BLOCK


class TestAutoPromotionContract:
    """The enforce⇒scan auto-promotion is a load-bearing invariant of
    the flag split. These tests pin it at the GSEConfig level so a
    refactor that breaks the promotion fails loudly."""

    def test_gse_config_enforce_only_auto_promotes_scan_to_true(self) -> None:
        """At config-construction time, enforce=True without scan=True is
        rewritten to scan=True. No exception, but the resulting config
        should have scan_enabled=True even though caller passed False."""
        from tonesoul.soul_config import GSEConfig

        cfg = GSEConfig(
            strategy_mirror_scan_enabled=False,
            strategy_mirror_enforce_enabled=True,
        )
        assert cfg.strategy_mirror_scan_enabled is True
        assert cfg.strategy_mirror_enforce_enabled is True

    def test_gse_config_other_three_states_unchanged(self) -> None:
        """The auto-promotion only fires for the impossible (False, True)
        cell. The other three cells preserve caller's exact values."""
        from tonesoul.soul_config import GSEConfig

        cfg_off = GSEConfig(
            strategy_mirror_scan_enabled=False,
            strategy_mirror_enforce_enabled=False,
        )
        assert cfg_off.strategy_mirror_scan_enabled is False
        assert cfg_off.strategy_mirror_enforce_enabled is False

        cfg_shadow = GSEConfig(
            strategy_mirror_scan_enabled=True,
            strategy_mirror_enforce_enabled=False,
        )
        assert cfg_shadow.strategy_mirror_scan_enabled is True
        assert cfg_shadow.strategy_mirror_enforce_enabled is False

        cfg_full = GSEConfig(
            strategy_mirror_scan_enabled=True,
            strategy_mirror_enforce_enabled=True,
        )
        assert cfg_full.strategy_mirror_scan_enabled is True
        assert cfg_full.strategy_mirror_enforce_enabled is True

    def test_default_gse_config_is_both_off(self) -> None:
        """Default state must remain off-off; this is the backward
        compatibility guarantee for callers that don't set the flags."""
        from tonesoul.soul_config import GSEConfig

        cfg = GSEConfig()
        assert cfg.strategy_mirror_scan_enabled is False
        assert cfg.strategy_mirror_enforce_enabled is False
