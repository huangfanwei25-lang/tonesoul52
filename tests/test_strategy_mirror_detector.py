"""Tests for StrategyDetector — surface + structural pattern detection.

Two test surfaces:

1. Detector mechanics against synthetic catalog (full control over what
   is in the catalog, so we can test scoring + thresholds + declaration
   marking precisely).

2. Detector against the real period-1 catalog (sanity checks: known
   manipulation phrases trigger red detections, pure-info text does not
   trigger reds, declaration markers correctly flip the declared bit).

Both surfaces are necessary because (1) tests the engine and (2) tests
that the engine + catalog actually work together end-to-end.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tonesoul.gse.strategy_mirror import CatalogLoader
from tonesoul.gse.strategy_mirror.detector import StrategyDetector
from tonesoul.gse.strategy_mirror.structural_patterns import (
    detect_pattern,
    registered_patterns,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _move(
    id_: str,
    cls: str,
    *,
    surface: list = None,
    structural: list = None,
    symbol: str = None,
    name: str = None,
) -> dict:
    """Catalog entry as dict (matches schema in period_*.json)."""
    return {
        "id": id_,
        "symbol": symbol or f"[{id_.split('.')[-1]}]",
        "name": name or f"name-{id_}",
        "pse_keyword": "kw",
        "pse_chinese_name": "中",
        "period": 1,
        "family": "測試",
        "pse_definition": "def",
        "pse_operation": "op",
        "transparency_class": cls,
        "rationale": "test rationale",
        "surface_signals": surface or [],
        "structural_signals": structural or [],
    }


def _write_catalog(tmp_path: Path, elements: list) -> Path:
    catalog = {
        "schema_version": "1.0",
        "period": 1,
        "elements_count": len(elements),
        "elements": elements,
    }
    path = tmp_path / "period_1_test.json"
    path.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
    return path


def _detector_with(tmp_path: Path, elements: list) -> StrategyDetector:
    _write_catalog(tmp_path, elements)
    loader = CatalogLoader(catalog_dir=tmp_path).load()
    return StrategyDetector(loader)


# ---------------------------------------------------------------------------
# Detector mechanics — surface signal scoring
# ---------------------------------------------------------------------------


class TestSurfaceSignalScoring:
    def test_no_signals_no_detection(self, tmp_path: Path) -> None:
        detector = _detector_with(tmp_path, [_move("1.001.A", "yellow", surface=["never_present"])])
        sig = detector.scan("normal benign text without any keywords")
        assert sig.detected_moves == []

    def test_single_surface_signal_below_threshold(self, tmp_path: Path) -> None:
        # Single surface signal contributes 0.35; below threshold 0.5
        detector = _detector_with(tmp_path, [_move("1.001.A", "yellow", surface=["限時"])])
        sig = detector.scan("這是限時優惠")
        assert sig.detected_moves == []  # 0.35 < 0.5 threshold

    def test_two_surface_signals_pass_threshold(self, tmp_path: Path) -> None:
        # Two distinct surface signals: 0.35 * 2 = 0.7 ≥ 0.5
        detector = _detector_with(tmp_path, [_move("1.001.A", "red", surface=["限時", "倒數"])])
        sig = detector.scan("限時優惠，倒數三天")
        assert len(sig.detected_moves) == 1
        assert sig.detected_moves[0].move.id == "1.001.A"
        assert sig.detected_moves[0].confidence >= 0.5

    def test_case_insensitive_match(self, tmp_path: Path) -> None:
        detector = _detector_with(
            tmp_path, [_move("1.001.A", "yellow", surface=["HOOK", "hook design"])]
        )
        sig = detector.scan("This is a Hook Design example.")
        assert len(sig.detected_moves) == 1

    def test_excerpt_captured(self, tmp_path: Path) -> None:
        detector = _detector_with(tmp_path, [_move("1.001.A", "red", surface=["限時", "錯過"])])
        sig = detector.scan("特別優惠：限時三天，錯過就沒了喔。")
        assert len(sig.detected_moves) == 1
        excerpts = sig.detected_moves[0].text_locations
        assert any("限時" in e for e in excerpts)


# ---------------------------------------------------------------------------
# Detector mechanics — structural signal scoring
# ---------------------------------------------------------------------------


class TestStructuralSignalScoring:
    def test_structural_signal_alone_below_default_threshold(self, tmp_path: Path) -> None:
        # Single structural pattern contributes 0.45 — below default 0.5 threshold,
        # so a structural signal alone deliberately does NOT trigger detection.
        # This is by design: detection should require either two surface signals,
        # or one structural + one surface, to limit false positives.
        _write_catalog(
            tmp_path,
            [_move("1.001.A", "yellow", structural=["question_in_first_sentence"])],
        )
        loader = CatalogLoader(catalog_dir=tmp_path).load()
        detector = StrategyDetector(loader)
        sig = detector.scan("你有沒有想過，為什麼會這樣？這是個有趣的問題。")
        assert sig.detected_moves == []

    def test_structural_signal_alone_with_lowered_threshold(self, tmp_path: Path) -> None:
        # Same setup, but lowering the threshold so the single 0.45 score
        # passes — confirms the structural pattern itself fires correctly.
        _write_catalog(
            tmp_path,
            [_move("1.001.A", "yellow", structural=["question_in_first_sentence"])],
        )
        loader = CatalogLoader(catalog_dir=tmp_path).load()
        detector = StrategyDetector(loader, confidence_threshold=0.4)
        sig = detector.scan("你有沒有想過，為什麼會這樣？這是個有趣的問題。")
        assert len(sig.detected_moves) == 1
        assert sig.detected_moves[0].confidence == pytest.approx(0.45, abs=0.01)

    def test_unknown_structural_pattern_silently_skipped(self, tmp_path: Path) -> None:
        # Unknown pattern names should not raise — just contribute 0
        detector = _detector_with(
            tmp_path,
            [_move("1.001.A", "yellow", structural=["nonexistent_pattern_xyz"])],
        )
        sig = detector.scan("any text")
        # Skipped pattern → confidence 0 → no detection (no error)
        assert sig.detected_moves == []

    def test_combined_surface_and_structural(self, tmp_path: Path) -> None:
        # surface (0.35) + structural (0.45) = 0.80, well above threshold
        detector = _detector_with(
            tmp_path,
            [_move("1.001.A", "red", surface=["倒數"], structural=["countdown_phrase"])],
        )
        sig = detector.scan("倒數三天，最後機會！")
        assert len(sig.detected_moves) == 1
        assert sig.detected_moves[0].confidence >= 0.7


# ---------------------------------------------------------------------------
# Declaration marking
# ---------------------------------------------------------------------------


class TestDeclarationMarking:
    def test_undeclared_by_default(self, tmp_path: Path) -> None:
        detector = _detector_with(tmp_path, [_move("1.001.A", "yellow", surface=["限時", "倒數"])])
        sig = detector.scan("限時三天，倒數結束")
        assert sig.detected_moves[0].declared is False

    def test_declared_via_explicit_list(self, tmp_path: Path) -> None:
        detector = _detector_with(
            tmp_path,
            [_move("1.001.A", "yellow", surface=["限時", "倒數"], symbol="[A]", name="假時限")],
        )
        sig = detector.scan("限時三天，倒數結束", declared_moves=["[A]"])
        assert sig.detected_moves[0].declared is True

    def test_declared_via_symbol_in_text(self, tmp_path: Path) -> None:
        detector = _detector_with(
            tmp_path,
            [_move("1.001.A", "yellow", surface=["限時", "倒數"], symbol="[A]")],
        )
        # Symbol [A] visible in text counts as declaration
        sig = detector.scan("[A] 限時三天，倒數結束")
        assert sig.detected_moves[0].declared is True

    def test_declared_via_explicit_marker_phrase(self, tmp_path: Path) -> None:
        detector = _detector_with(
            tmp_path,
            [_move("1.001.A", "yellow", surface=["限時", "倒數"], name="假時限構造")],
        )
        sig = detector.scan("我用了假時限構造這個招式：限時三天，倒數結束")
        assert sig.detected_moves[0].declared is True

    # ------------------------------------------------------------------
    # NEGATIVE cases — added 2026-04-28 after Codex review found the
    # pre-fix detector was marking unrelated moves as declared whenever
    # any marker phrase + any move name both appeared in the same text.
    # The fix binds marker → name via DECLARATION_PROXIMITY_CHARS = 50.
    # ------------------------------------------------------------------

    def test_marker_far_from_name_does_not_declare(self, tmp_path: Path) -> None:
        """Codex repro: 'I used alpha <long text> beta name' must not
        mark beta as declared just because 'I used' appears anywhere."""
        long_filler = " content " * 30  # ~270 chars between marker and beta
        detector = _detector_with(
            tmp_path,
            [
                _move("1.001.A", "yellow", surface=["alpha-x", "alpha-y"], name="alpha move"),
                _move("1.002.B", "yellow", surface=["beta-x", "beta-y"], name="beta move"),
            ],
        )
        text = (
            f"I used alpha move with alpha-x and alpha-y everywhere. "
            f"{long_filler}"
            f"Now consider beta move which uses beta-x and beta-y as keywords."
        )
        sig = detector.scan(text)
        by_id = {d.move.id: d for d in sig.detected_moves}
        # alpha was actually declared (marker right next to name)
        assert by_id["1.001.A"].declared is True
        # beta should NOT be declared — marker phrase is ~270 chars away
        assert by_id["1.002.B"].declared is False, (
            "beta move was wrongly marked declared just because 'I used' "
            "appears somewhere in the text — the proximity binding is broken"
        )

    def test_marker_in_different_paragraph_does_not_declare(self, tmp_path: Path) -> None:
        """Marker and name separated by sufficient text (>50 chars):
        not a declaration of the second move."""
        detector = _detector_with(
            tmp_path,
            [
                _move("1.001.A", "yellow", surface=["foo-x", "foo-y"], name="alpha thing"),
                _move("1.002.B", "yellow", surface=["bar-x", "bar-y"], name="beta thing"),
            ],
        )
        # Construct gap of well over 50 chars between "我用了" and "beta thing"
        gap = "中間隔了非常多其他內容、句子、段落，總共加起來超過五十個字元的距離。" * 2
        text = (
            "我用了 alpha thing 來示範：foo-x 和 foo-y。\n\n"
            f"{gap}\n\n"
            "另一段獨立內容，這裡有 beta thing 但沒有任何聲明 marker。bar-x bar-y\n"
        )
        sig = detector.scan(text)
        by_id = {d.move.id: d for d in sig.detected_moves}
        if "1.002.B" in by_id:
            assert by_id["1.002.B"].declared is False, (
                "beta thing was wrongly marked declared by the marker in "
                "the previous paragraph (gap > 50 chars)"
            )

    def test_marker_within_proximity_does_declare(self, tmp_path: Path) -> None:
        """Positive control for the proximity binding: marker right
        before the name (well within 50 chars) → declared."""
        detector = _detector_with(
            tmp_path,
            [_move("1.001.A", "yellow", surface=["limit", "deadline"], name="urgency move")],
        )
        sig = detector.scan("I used urgency move here: limit and deadline.")
        assert sig.detected_moves[0].declared is True

    def test_two_markers_two_names_only_local_pairs_declare(self, tmp_path: Path) -> None:
        """Realistic mixed case: two markers + two names, both pairs
        local. Both should declare correctly because each marker is near
        its own name."""
        detector = _detector_with(
            tmp_path,
            [
                _move("1.001.A", "yellow", surface=["x1", "x2"], name="alpha craft"),
                _move("1.002.B", "yellow", surface=["y1", "y2"], name="beta craft"),
            ],
        )
        text = (
            "本段使用 alpha craft：x1 和 x2 出現。"
            + " " * 100  # gap so the two declarations don't bleed
            + "本段使用 beta craft：y1 和 y2 出現。"
        )
        sig = detector.scan(text)
        by_id = {d.move.id: d for d in sig.detected_moves}
        assert by_id["1.001.A"].declared is True
        assert by_id["1.002.B"].declared is True

    def test_name_alone_without_any_marker_not_declared(self, tmp_path: Path) -> None:
        """Just the name appearing in text (no marker phrase anywhere)
        is not declaration — it's just usage."""
        detector = _detector_with(
            tmp_path,
            [_move("1.001.A", "yellow", surface=["w1", "w2"], name="some craft")],
        )
        sig = detector.scan("這個段落用了 some craft，包含 w1 和 w2，但沒寫任何聲明 marker。")
        assert sig.detected_moves[0].declared is False


# ---------------------------------------------------------------------------
# StrategySignature integration: Council flags
# ---------------------------------------------------------------------------


class TestSignatureFlags:
    def test_red_detection_triggers_council_re_review(self, tmp_path: Path) -> None:
        detector = _detector_with(tmp_path, [_move("1.001.R", "red", surface=["限時", "錯過就沒"])])
        sig = detector.scan("限時搶購！錯過就沒了！")
        assert sig.has_red is True
        assert sig.requires_council_re_review() is True

    def test_undeclared_yellow_triggers_block(self, tmp_path: Path) -> None:
        detector = _detector_with(
            tmp_path,
            [_move("1.001.Y", "yellow", surface=["限時", "倒數"], symbol="[Y]")],
        )
        sig = detector.scan("限時三天，倒數結束")  # no declaration
        assert sig.has_undeclared_yellow is True
        assert sig.requires_block() is True

    def test_declared_yellow_does_not_trigger_block(self, tmp_path: Path) -> None:
        detector = _detector_with(
            tmp_path,
            [_move("1.001.Y", "yellow", surface=["限時", "倒數"], symbol="[Y]")],
        )
        sig = detector.scan("限時三天，倒數結束", declared_moves=["[Y]"])
        assert sig.has_undeclared_yellow is False
        assert sig.requires_block() is False


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_text_returns_empty_signature(self, tmp_path: Path) -> None:
        detector = _detector_with(tmp_path, [_move("1.001.A", "red", surface=["限時"])])
        sig = detector.scan("")
        assert sig.detected_moves == []
        assert sig.has_red is False

    def test_whitespace_only_text(self, tmp_path: Path) -> None:
        detector = _detector_with(tmp_path, [_move("1.001.A", "red", surface=["限時"])])
        sig = detector.scan("   \n\n  \t  ")
        assert sig.detected_moves == []

    def test_summary_when_nothing_detected(self, tmp_path: Path) -> None:
        detector = _detector_with(tmp_path, [_move("1.001.A", "yellow", surface=["xxx"])])
        sig = detector.scan("benign text with no markers")
        assert "No strategy moves" in sig.summary

    def test_summary_when_moves_detected(self, tmp_path: Path) -> None:
        detector = _detector_with(
            tmp_path,
            [
                _move("1.001.G", "green", surface=["以下整理", "完整資料"]),
                _move("1.002.R", "red", surface=["限時", "倒數"]),
            ],
        )
        sig = detector.scan("以下整理完整資料：限時優惠，倒數三天")
        assert "green=1" in sig.summary
        assert "red=1" in sig.summary


# ---------------------------------------------------------------------------
# Structural pattern unit tests
# ---------------------------------------------------------------------------


class TestStructuralPatterns:
    def test_basic_patterns_registered_smoke(self) -> None:
        """Smoke test: a handful of load-bearing patterns are registered.

        This is NOT a coverage test — see test_structural_pattern_coverage_budget
        below for the gap-vs-catalog assertion. The pre-Codex-review name of
        this test was test_all_referenced_patterns_documented, which was
        misleading (the catalog references ~450 unique patterns; this test
        only checked 3). Renamed 2026-04-28 for honesty.
        """
        registered = registered_patterns()
        assert "question_in_first_sentence" in registered
        assert "countdown_phrase" in registered
        assert "deadline_assertion" in registered

    def test_question_in_first_sentence(self) -> None:
        assert detect_pattern("question_in_first_sentence", "你有沒有想過？接下來是答案。")
        assert not detect_pattern("question_in_first_sentence", "這是一個陳述句。")

    def test_countdown_phrase(self) -> None:
        assert detect_pattern("countdown_phrase", "限時三天")
        assert detect_pattern("countdown_phrase", "倒數一週")
        assert not detect_pattern("countdown_phrase", "今天天氣很好")

    def test_deadline_assertion(self) -> None:
        assert detect_pattern("deadline_assertion", "錯過就沒了")
        assert detect_pattern("deadline_assertion", "再不買就買不到")
        assert not detect_pattern("deadline_assertion", "歡迎慢慢看")

    def test_scarcity_quantifier(self) -> None:
        assert detect_pattern("scarcity_quantifier", "只剩 5 個名額")
        assert detect_pattern("scarcity_quantifier", "最後機會")
        assert not detect_pattern("scarcity_quantifier", "充足供應")

    def test_enumeration_format(self) -> None:
        assert detect_pattern("enumeration_format", "第一是 X，第二是 Y，第三是 Z")
        assert detect_pattern("enumeration_format", "1. 首先\n2. 其次\n3. 最後")
        assert not detect_pattern("enumeration_format", "純散文沒有條列")

    def test_audience_qualifier_at_top(self) -> None:
        assert detect_pattern("audience_qualifier_at_top", "如果你是工程師，本文適合你")
        assert not detect_pattern("audience_qualifier_at_top", "今天聊聊一個技術問題")

    def test_unknown_pattern_returns_false_not_error(self) -> None:
        assert detect_pattern("nonexistent", "anything") is False


# ---------------------------------------------------------------------------
# End-to-end against real period-1 catalog
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Catalog ↔ registry coverage
# ---------------------------------------------------------------------------


# Coverage budget floor (post-Codex-review 2026-04-28).
# Empirical state on the period-1 catalog:
#   - 450 total structural_signal references (also 450 unique — no name
#     reuse across entries)
#   - 18 patterns registered in structural_patterns.py
#   - 15 of those 18 are actually referenced by the catalog
#   - 3 registered patterns (deadline_assertion, scarcity_quantifier,
#     time_constraint_phrase) are NOT referenced anywhere — registered
#     defensively when detector.py was first written, then catalog
#     authoring chose different names; left in place because removing
#     them is a separate cleanup pass
#   - coverage_ratio = 15 / 450 = 3.33%
# Budget pinned at 3% so any further drop (catalog growth without
# registry registration, or registry pattern deletion) fails loudly.
# Future PRs may RAISE this budget as more patterns get implemented;
# LOWERING it requires explicit rationale in the PR description (which
# acknowledges that more of the catalog's structural_signals axis is
# decoration rather than detection).
STRUCTURAL_COVERAGE_BUDGET: float = 0.03


class TestStructuralPatternCoverage:
    """Catalog vs registry drift detection.

    Pre-Codex-review state was: 18 registered patterns, ~450 unique
    pattern names referenced in catalog → ~4% coverage. The catalog was
    written ahead of the registry, with the silent-skip design intentionally
    accepting unsupported patterns. The OLD diagnostic test only checked
    that 3 specific patterns existed, completely missing this drift —
    catalog entries could continue adding new pattern names indefinitely
    while the test stayed green.

    These two tests pin the gap honestly:
      - test_structural_pattern_coverage_budget: hard floor (fails on drift)
      - test_structural_pattern_coverage_diagnostic: print breakdown (always passes)
    """

    @staticmethod
    def _gather_referenced() -> set:
        """All unique structural_signal names referenced across all loaded
        catalog entries."""
        loader = CatalogLoader().load()
        referenced: set = set()
        for move in loader.all():
            for sig in move.structural_signals:
                if sig:
                    referenced.add(sig)
        return referenced

    def test_structural_pattern_coverage_budget(self) -> None:
        """Catalog/registry coverage must not drop below the budget floor.

        Failure modes this test catches:
          - new catalog entry adds 5 new structural_signal names without
            registering them → coverage_ratio drops → test fails
          - someone deletes a registered pattern → coverage drops → fails
          - someone deletes catalog entries with COVERED patterns →
            registered ratio could even rise; this test only enforces FLOOR
            (raising the budget is a separate, intentional act)

        Failure messages list the top missing patterns so the dev fixing
        it sees the gap concretely.
        """
        referenced = self._gather_referenced()
        registered = set(registered_patterns())
        if not referenced:
            pytest.skip("No structural signals in catalog yet")

        covered = referenced & registered
        coverage_ratio = len(covered) / len(referenced)

        missing = sorted(referenced - registered)[:15]

        assert coverage_ratio >= STRUCTURAL_COVERAGE_BUDGET, (
            f"\nStructural pattern coverage dropped below budget "
            f"({STRUCTURAL_COVERAGE_BUDGET:.2%}):\n"
            f"  current = {coverage_ratio:.2%} ({len(covered)}/{len(referenced)})\n"
            f"  missing = {len(referenced - registered)} patterns "
            f"in catalog but not in registry\n"
            f"  top 15 missing: {missing}\n\n"
            f"To fix:\n"
            f"  EITHER register the missing patterns in "
            f"tonesoul/gse/strategy_mirror/structural_patterns.py PATTERNS dict,\n"
            f"  OR raise STRUCTURAL_COVERAGE_BUDGET in this test with rationale "
            f"in the PR description (which acknowledges that part of the "
            f"catalog's structural_signals axis is decoration, not detection)."
        )

    def test_structural_pattern_coverage_diagnostic(self, capsys) -> None:
        """Diagnostic only: prints breakdown. Always passes.

        Useful for dev: run pytest -s to see the actual gap numbers
        without having to bump the budget to provoke a failure.
        """
        referenced = self._gather_referenced()
        registered = set(registered_patterns())
        covered = referenced & registered
        missing = referenced - registered
        coverage_ratio = (len(covered) / len(referenced)) if referenced else 0.0

        print("\n=== Structural pattern coverage (diagnostic) ===")
        print(f"  Catalog references: {len(referenced)} unique patterns")
        print(f"  Registry has:       {len(registered)} patterns")
        print(f"  Covered:            {len(covered)} patterns")
        print(f"  Missing in registry: {len(missing)} patterns")
        print(f"  Coverage ratio:     {coverage_ratio:.2%}")
        print(f"  Budget floor:       {STRUCTURAL_COVERAGE_BUDGET:.2%}")
        # Always passes — purely informational.
        assert True


class TestRealPeriod1Catalog:
    """Detector + the real period-1 catalog. These tests pin down detector
    behavior against the actual catalog entries shipped in this commit."""

    def test_loads_real_catalog(self) -> None:
        loader = CatalogLoader().load()
        detector = StrategyDetector(loader)
        assert detector is not None  # smoke

    def test_fake_urgency_phrase_triggers_red(self) -> None:
        """A draft full of fake-urgency phrases should trigger [Bh] 假時限構造."""
        loader = CatalogLoader().load()
        detector = StrategyDetector(loader)
        text = "限時優惠！倒數三天，錯過就沒了！現在就行動！只剩最後三個名額！"
        sig = detector.scan(text)
        # At least one red detection (specifically [Bh] should appear)
        red_ids = [d.move.id for d in sig.red_moves()]
        assert any("Bh" in i for i in red_ids), f"expected [Bh] in reds, got {red_ids}"
        assert sig.has_red is True

    def test_pure_info_text_no_red(self) -> None:
        """A pure information dump (no marketing) should not trigger any red."""
        loader = CatalogLoader().load()
        detector = StrategyDetector(loader)
        text = (
            "以下整理本月的數據資料：\n"
            "第一，使用者數量為 5,234 人。\n"
            "第二，平均停留時間為 12 分鐘。\n"
            "第三，跳出率為 38%。\n"
            "完整資料如附件。"
        )
        sig = detector.scan(text)
        # Should not trigger reds (might trigger green like 顆粒度提升 / 結構化呈現)
        assert (
            sig.has_red is False
        ), f"unexpected red detections: {[d.move.id for d in sig.red_moves()]}"
