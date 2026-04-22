"""Tests for tonesoul.yuhun.context_assembler."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tonesoul.yuhun.context_assembler import (
    FORBIDDEN_PREFIXES,
    ContextAssembler,
    ContextPackage,
    ContextViolationError,
    _classify_conflict_type,
    validate_context_sources,
)
from tonesoul.yuhun.dpr import DPRResult, RoutingDecision


def _fast_dpr(request="hello") -> DPRResult:
    return DPRResult(
        decision=RoutingDecision.FAST_PATH,
        complexity_score=0.1,
        conflict_detected=False,
        conflict_triggers=[],
        estimated_token_cost="1x",
        reason="simple request",
    )


def _council_dpr(triggers=None) -> DPRResult:
    return DPRResult(
        decision=RoutingDecision.COUNCIL_PATH,
        complexity_score=0.8,
        conflict_detected=True,
        conflict_triggers=triggers or ["uncertainty"],
        estimated_token_cost="4x",
        reason="high complexity",
    )


class TestClassifyConflictType:
    def test_legal_keyword_returns_legal_ethics(self):
        assert _classify_conflict_type(["倫理", "隱私"]) == "legal_ethics"

    def test_legal_english_keyword(self):
        assert _classify_conflict_type(["ethics", "privacy"]) == "legal_ethics"

    def test_uncertainty_keyword(self):
        assert _classify_conflict_type(["應該", "風險"]) == "uncertainty"

    def test_research_keyword(self):
        assert _classify_conflict_type(["架構", "系統"]) == "research"

    def test_empty_triggers_defaults_to_uncertainty(self):
        assert _classify_conflict_type([]) == "uncertainty"

    def test_unknown_triggers_defaults_to_uncertainty(self):
        assert _classify_conflict_type(["random_word_xyz"]) == "uncertainty"


class TestValidateContextSources:
    def test_clean_sources_pass(self):
        sources = ["AXIOMS.json", "docs/architecture/DESIGN.md", "tonesoul/cli/main.py"]
        assert validate_context_sources(sources) is True

    @pytest.mark.parametrize("forbidden", FORBIDDEN_PREFIXES)
    def test_forbidden_prefix_raises(self, forbidden):
        bad_source = f"{forbidden}some_file.md"
        with pytest.raises(ContextViolationError, match="CONTEXT_BUDGET_SPEC"):
            validate_context_sources([bad_source])

    def test_empty_list_passes(self):
        assert validate_context_sources([]) is True


class TestContextPackage:
    def test_to_prompt_sections_always_ends_with_user_request(self):
        pkg = ContextPackage(
            routing=RoutingDecision.FAST_PATH,
            user_request="my question",
            axioms_content="P1: honesty",
        )
        sections = pkg.to_prompt_sections()
        assert sections[-1].startswith("[USER REQUEST]")
        assert "my question" in sections[-1]

    def test_to_prompt_sections_includes_axioms(self):
        pkg = ContextPackage(
            routing=RoutingDecision.FAST_PATH,
            user_request="q",
            axioms_content="P1: honesty\nP2: continuity",
        )
        sections = pkg.to_prompt_sections()
        assert any("[AXIOMS]" in s for s in sections)

    def test_to_prompt_sections_includes_anchors_when_present(self):
        pkg = ContextPackage(
            routing=RoutingDecision.COUNCIL_PATH,
            user_request="q",
            anchor_memory=["anchor 1", "anchor 2"],
        )
        sections = pkg.to_prompt_sections()
        assert any("[STABLE ANCHORS]" in s for s in sections)

    def test_to_prompt_sections_includes_contracts_when_present(self):
        pkg = ContextPackage(
            routing=RoutingDecision.COUNCIL_PATH,
            user_request="q",
            contracts=["Contract A", "Contract B"],
        )
        sections = pkg.to_prompt_sections()
        assert any("[ARCHITECTURE CONTRACTS]" in s for s in sections)

    def test_to_prompt_sections_includes_council_frame_when_present(self):
        pkg = ContextPackage(
            routing=RoutingDecision.COUNCIL_PATH,
            user_request="q",
            council_frame="四向平行推演",
        )
        sections = pkg.to_prompt_sections()
        assert any("[COUNCIL FRAME]" in s for s in sections)

    def test_fast_path_only_axioms_and_request(self):
        pkg = ContextPackage(
            routing=RoutingDecision.FAST_PATH,
            user_request="simple question",
            axioms_content="P1: honesty",
        )
        sections = pkg.to_prompt_sections()
        assert len(sections) == 2
        assert not any("[STABLE ANCHORS]" in s for s in sections)


class TestContextAssembler:
    def test_fast_path_skips_layers_2_through_4(self, tmp_path):
        (tmp_path / "AXIOMS.json").write_text(
            json.dumps({"axioms": [{"id": 1, "one_line": "Be honest"}]}),
            encoding="utf-8",
        )
        assembler = ContextAssembler(repo_root=tmp_path)
        pkg = assembler.assemble(_fast_dpr("hello"), "hello")

        assert pkg.routing == RoutingDecision.FAST_PATH
        assert pkg.anchor_memory == []
        assert pkg.contracts == []
        assert pkg.council_frame == ""
        assert "AXIOMS.json" in pkg.sources_used

    def test_fast_path_axioms_loaded_from_file(self, tmp_path):
        (tmp_path / "AXIOMS.json").write_text(
            json.dumps({"axioms": [{"id": 1, "one_line": "Be honest"}, {"id": 2, "one_line": "Maintain continuity"}]}),
            encoding="utf-8",
        )
        assembler = ContextAssembler(repo_root=tmp_path)
        pkg = assembler.assemble(_fast_dpr(), "test")
        assert "P1: Be honest" in pkg.axioms_content
        assert "P2: Maintain continuity" in pkg.axioms_content

    def test_axioms_missing_file_degrades_gracefully(self, tmp_path):
        assembler = ContextAssembler(repo_root=tmp_path)
        pkg = assembler.assemble(_fast_dpr(), "test")
        assert pkg.axioms_content == ""

    def test_council_path_includes_council_frame(self, tmp_path):
        (tmp_path / "AXIOMS.json").write_text(
            json.dumps({"axioms": []}), encoding="utf-8"
        )
        assembler = ContextAssembler(repo_root=tmp_path)
        pkg = assembler.assemble(_council_dpr(), "complex question", include_anchor_memory=False)

        assert pkg.routing == RoutingDecision.COUNCIL_PATH
        assert pkg.council_frame != ""
        assert "council_frame_summary" in pkg.sources_used

    def test_estimated_tokens_positive(self, tmp_path):
        (tmp_path / "AXIOMS.json").write_text(
            json.dumps({"axioms": [{"id": 1, "one_line": "Be honest"}]}),
            encoding="utf-8",
        )
        assembler = ContextAssembler(repo_root=tmp_path)
        pkg = assembler.assemble(_fast_dpr("a long user request"), "a long user request")
        assert pkg.estimated_tokens > 0

    def test_axioms_are_cached_across_calls(self, tmp_path):
        (tmp_path / "AXIOMS.json").write_text(
            json.dumps({"axioms": [{"id": 1, "one_line": "Be honest"}]}),
            encoding="utf-8",
        )
        assembler = ContextAssembler(repo_root=tmp_path)
        assembler.assemble(_fast_dpr(), "first call")
        (tmp_path / "AXIOMS.json").write_text(
            json.dumps({"axioms": [{"id": 1, "one_line": "CHANGED"}]}),
            encoding="utf-8",
        )
        pkg2 = assembler.assemble(_fast_dpr(), "second call")
        # Still uses cached content — won't see "CHANGED"
        assert "CHANGED" not in pkg2.axioms_content
