"""Tests for tonesoul.yuhun.context_assembler — pure helpers and ContextPackage."""

from __future__ import annotations

import pytest

from tonesoul.yuhun.context_assembler import (
    FORBIDDEN_PREFIXES,
    ContextPackage,
    ContextViolationError,
    _classify_conflict_type,
    validate_context_sources,
)
from tonesoul.yuhun.dpr import RoutingDecision

# ── _classify_conflict_type ───────────────────────────────────────────────────


class TestClassifyConflictType:
    def test_legal_keywords(self):
        result = _classify_conflict_type(["倫理", "法律"])
        assert result == "legal_ethics"

    def test_english_legal(self):
        result = _classify_conflict_type(["ethics concern"])
        assert result == "legal_ethics"

    def test_uncertainty_keyword(self):
        result = _classify_conflict_type(["should we", "risk analysis"])
        assert result == "uncertainty"

    def test_research_keyword(self):
        result = _classify_conflict_type(["architecture discussion"])
        assert result == "research"

    def test_empty_defaults_uncertainty(self):
        result = _classify_conflict_type([])
        assert result == "uncertainty"

    def test_no_match_defaults_uncertainty(self):
        result = _classify_conflict_type(["random trigger"])
        assert result == "uncertainty"


# ── validate_context_sources ──────────────────────────────────────────────────


class TestValidateContextSources:
    def test_valid_sources_return_true(self):
        result = validate_context_sources(["AXIOMS.json", "docs/architecture/spec.md"])
        assert result is True

    def test_empty_sources_return_true(self):
        assert validate_context_sources([]) is True

    def test_forbidden_prefix_raises(self):
        with pytest.raises(ContextViolationError):
            validate_context_sources(["docs/chronicles/task_archive_2026.md"])

    def test_archive_prefix_raises(self):
        with pytest.raises(ContextViolationError):
            validate_context_sources([".archive/old_file.md"])

    def test_memory_prefix_raises(self):
        with pytest.raises(ContextViolationError):
            validate_context_sources(["memory/handoff/file.jsonl"])

    def test_error_message_mentions_source(self):
        try:
            validate_context_sources(["temp/scratch.txt"])
        except ContextViolationError as e:
            assert "temp/" in str(e)

    def test_all_forbidden_prefixes_covered(self):
        for prefix in FORBIDDEN_PREFIXES:
            with pytest.raises(ContextViolationError):
                validate_context_sources([f"{prefix}test.txt"])


# ── ContextPackage.to_prompt_sections ─────────────────────────────────────────


class TestContextPackageToPromptSections:
    def _make(self, routing=RoutingDecision.FAST_PATH, **kw):
        defaults = dict(routing=routing, user_request="test query")
        defaults.update(kw)
        return ContextPackage(**defaults)

    def test_user_request_always_last(self):
        pkg = self._make(axioms_content="axioms here")
        sections = pkg.to_prompt_sections()
        assert sections[-1].startswith("[USER REQUEST]")

    def test_axioms_section_present_when_set(self):
        pkg = self._make(axioms_content="P1: something")
        sections = pkg.to_prompt_sections()
        assert any("[AXIOMS]" in s for s in sections)

    def test_axioms_not_present_when_empty(self):
        pkg = self._make(axioms_content="")
        sections = pkg.to_prompt_sections()
        assert not any("[AXIOMS]" in s for s in sections)

    def test_anchor_memory_section_when_set(self):
        pkg = self._make(anchor_memory=["anchor1", "anchor2"])
        sections = pkg.to_prompt_sections()
        assert any("[STABLE ANCHORS]" in s for s in sections)

    def test_no_anchor_section_when_empty(self):
        pkg = self._make(anchor_memory=[])
        sections = pkg.to_prompt_sections()
        assert not any("[STABLE ANCHORS]" in s for s in sections)

    def test_contracts_section_when_set(self):
        pkg = self._make(contracts=["contract text"])
        sections = pkg.to_prompt_sections()
        assert any("[ARCHITECTURE CONTRACTS]" in s for s in sections)

    def test_council_frame_section_when_set(self):
        pkg = self._make(council_frame="frame content")
        sections = pkg.to_prompt_sections()
        assert any("[COUNCIL FRAME]" in s for s in sections)

    def test_fast_path_minimal_sections(self):
        pkg = self._make(routing=RoutingDecision.FAST_PATH)
        sections = pkg.to_prompt_sections()
        # Only user request (axioms empty, no anchors, no contracts, no frame)
        assert len(sections) == 1
        assert sections[0].startswith("[USER REQUEST]")

    def test_full_package_section_order(self):
        pkg = self._make(
            axioms_content="axioms",
            anchor_memory=["anchor"],
            contracts=["contract"],
            council_frame="frame",
        )
        sections = pkg.to_prompt_sections()
        # Order: AXIOMS → ANCHORS → CONTRACTS → COUNCIL FRAME → USER REQUEST
        labels = [s.split("\n")[0] for s in sections]
        assert labels.index("[AXIOMS]") < labels.index("[STABLE ANCHORS]")
        assert labels.index("[STABLE ANCHORS]") < labels.index("[ARCHITECTURE CONTRACTS]")
        assert labels.index("[ARCHITECTURE CONTRACTS]") < labels.index("[COUNCIL FRAME]")
        assert labels.index("[COUNCIL FRAME]") < labels.index("[USER REQUEST]")
