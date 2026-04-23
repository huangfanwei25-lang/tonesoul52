"""Tests for tonesoul.corpus.pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

from tonesoul.corpus.pipeline import (
    CorpusPipeline,
    PipelineResponse,
    create_corpus_pipeline,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_pipeline() -> CorpusPipeline:
    """Create a CorpusPipeline with mocked storage backends."""
    with (
        patch("tonesoul.corpus.pipeline.ConsentManager") as mock_cm,
        patch("tonesoul.corpus.pipeline.CorpusStorage") as mock_cs,
    ):
        pipeline = CorpusPipeline(
            consent_db=":memory:",
            corpus_db=":memory:",
            corpus_jsonl="/dev/null",
        )
    pipeline.consent_manager = MagicMock()
    pipeline.corpus_storage = MagicMock()
    return pipeline


# ── PipelineResponse ──────────────────────────────────────────────────────────

class TestPipelineResponse:
    def test_basic_fields(self):
        r = PipelineResponse(
            response="hello",
            conversation_id="conv-1",
            turn_index=0,
        )
        assert r.response == "hello"
        assert r.conversation_id == "conv-1"
        assert r.turn_index == 0

    def test_deliberation_defaults_none(self):
        r = PipelineResponse(response="x", conversation_id="y", turn_index=0)
        assert r.deliberation is None

    def test_suggested_replies_defaults_none(self):
        r = PipelineResponse(response="x", conversation_id="y", turn_index=0)
        assert r.suggested_replies is None

    def test_to_dict_basic(self):
        r = PipelineResponse(response="hello", conversation_id="c1", turn_index=2)
        d = r.to_dict()
        assert d["response"] == "hello"
        assert d["conversation_id"] == "c1"
        assert d["turn_index"] == 2

    def test_to_dict_no_deliberation_key(self):
        r = PipelineResponse(response="x", conversation_id="y", turn_index=0)
        d = r.to_dict()
        assert "deliberation" not in d

    def test_to_dict_no_suggested_replies_key(self):
        r = PipelineResponse(response="x", conversation_id="y", turn_index=0)
        d = r.to_dict()
        assert "suggested_replies" not in d

    def test_to_dict_with_deliberation(self):
        r = PipelineResponse(
            response="x",
            conversation_id="y",
            turn_index=0,
            deliberation={"verdict": "approve"},
        )
        d = r.to_dict()
        assert "deliberation" in d
        assert d["deliberation"]["verdict"] == "approve"

    def test_to_dict_with_suggested_replies(self):
        r = PipelineResponse(
            response="x",
            conversation_id="y",
            turn_index=0,
            suggested_replies=[{"text": "yes"}],
        )
        d = r.to_dict()
        assert "suggested_replies" in d
        assert d["suggested_replies"][0]["text"] == "yes"


# ── CorpusPipeline.generate_session_id ───────────────────────────────────────

class TestGenerateSessionId:
    def test_starts_with_session_prefix(self):
        pipeline = _make_pipeline()
        sid = pipeline.generate_session_id()
        assert sid.startswith("session_")

    def test_unique_each_call(self):
        pipeline = _make_pipeline()
        ids = {pipeline.generate_session_id() for _ in range(20)}
        assert len(ids) == 20

    def test_length_reasonable(self):
        pipeline = _make_pipeline()
        sid = pipeline.generate_session_id()
        assert len(sid) > 10


# ── CorpusPipeline.has_consent ────────────────────────────────────────────────

class TestHasConsent:
    def test_delegates_to_consent_manager(self):
        pipeline = _make_pipeline()
        pipeline.consent_manager.has_valid_consent.return_value = True
        assert pipeline.has_consent("sess-1") is True
        pipeline.consent_manager.has_valid_consent.assert_called_once_with("sess-1")

    def test_returns_false_when_manager_returns_false(self):
        pipeline = _make_pipeline()
        pipeline.consent_manager.has_valid_consent.return_value = False
        assert pipeline.has_consent("sess-x") is False


# ── CorpusPipeline.record_consent ─────────────────────────────────────────────

class TestRecordConsent:
    def test_delegates_to_consent_manager(self):
        pipeline = _make_pipeline()
        mock_consent = MagicMock()
        pipeline.consent_manager.record_consent.return_value = mock_consent
        result = pipeline.record_consent("sess-2")
        assert result is mock_consent

    def test_passes_ip_and_user_agent(self):
        pipeline = _make_pipeline()
        pipeline.record_consent("s", ip_address="1.2.3.4", user_agent="Mozilla")
        call_kwargs = pipeline.consent_manager.record_consent.call_args
        assert "1.2.3.4" in str(call_kwargs)
        assert "Mozilla" in str(call_kwargs)


# ── CorpusPipeline.withdraw_consent ──────────────────────────────────────────

class TestWithdrawConsent:
    def test_returns_combined_result(self):
        pipeline = _make_pipeline()
        pipeline.consent_manager.withdraw_consent.return_value = True
        pipeline.corpus_storage.delete_session_data.return_value = 3
        result = pipeline.withdraw_consent("sess-del")
        assert result["consent_withdrawn"] is True
        assert result["conversations_deleted"] == 3

    def test_calls_both_managers(self):
        pipeline = _make_pipeline()
        pipeline.consent_manager.withdraw_consent.return_value = False
        pipeline.corpus_storage.delete_session_data.return_value = 0
        pipeline.withdraw_consent("s")
        pipeline.consent_manager.withdraw_consent.assert_called_once_with("s")
        pipeline.corpus_storage.delete_session_data.assert_called_once_with("s")


# ── CorpusPipeline.start_conversation ────────────────────────────────────────

class TestStartConversation:
    def test_raises_if_no_consent(self):
        pipeline = _make_pipeline()
        pipeline.consent_manager.has_valid_consent.return_value = False
        with pytest.raises(ValueError, match="consent"):
            pipeline.start_conversation("no-consent-session")

    def test_returns_conversation_id(self):
        pipeline = _make_pipeline()
        pipeline.consent_manager.has_valid_consent.return_value = True
        mock_consent = MagicMock()
        mock_consent.consent_version = "1.0"
        pipeline.consent_manager.get_consent.return_value = mock_consent
        mock_conv = MagicMock()
        mock_conv.id = "conv-abc"
        pipeline.corpus_storage.create_conversation.return_value = mock_conv
        result = pipeline.start_conversation("good-session")
        assert result == "conv-abc"

    def test_passes_model_to_storage(self):
        pipeline = _make_pipeline()
        pipeline.consent_manager.has_valid_consent.return_value = True
        mock_consent = MagicMock()
        mock_consent.consent_version = "2.0"
        pipeline.consent_manager.get_consent.return_value = mock_consent
        mock_conv = MagicMock()
        mock_conv.id = "c"
        pipeline.corpus_storage.create_conversation.return_value = mock_conv
        pipeline.start_conversation("s", model="test-model")
        call_kwargs = pipeline.corpus_storage.create_conversation.call_args
        assert "test-model" in str(call_kwargs)


# ── CorpusPipeline._fallback_response ────────────────────────────────────────

class TestFallbackResponse:
    def test_contains_truncated_input(self):
        pipeline = _make_pipeline()
        msg = pipeline._fallback_response("Hello!")
        assert "Hello!" in msg

    def test_long_input_truncated(self):
        pipeline = _make_pipeline()
        long_input = "x" * 200
        msg = pipeline._fallback_response(long_input)
        assert len(msg) < len(long_input) + 100

    def test_returns_string(self):
        pipeline = _make_pipeline()
        assert isinstance(pipeline._fallback_response("test"), str)


# ── CorpusPipeline.process_message ───────────────────────────────────────────

class TestProcessMessage:
    def test_returns_pipeline_response(self):
        pipeline = _make_pipeline()
        pipeline.corpus_storage.add_turn.return_value = 0
        result = pipeline.process_message("conv-1", "hello", use_deliberation=False)
        assert isinstance(result, PipelineResponse)

    def test_response_is_fallback_without_deliberation(self):
        pipeline = _make_pipeline()
        pipeline.corpus_storage.add_turn.return_value = 0
        result = pipeline.process_message("conv-1", "test input", use_deliberation=False)
        assert "test input" in result.response

    def test_turn_stored_in_corpus(self):
        pipeline = _make_pipeline()
        pipeline.corpus_storage.add_turn.return_value = 1
        pipeline.process_message("conv-1", "msg", use_deliberation=False)
        pipeline.corpus_storage.add_turn.assert_called_once()

    def test_conversation_id_in_response(self):
        pipeline = _make_pipeline()
        pipeline.corpus_storage.add_turn.return_value = 0
        result = pipeline.process_message("conv-xyz", "msg", use_deliberation=False)
        assert result.conversation_id == "conv-xyz"

    def test_deliberation_engine_none_gives_fallback(self):
        pipeline = _make_pipeline()
        pipeline._deliberation_engine = None
        pipeline.corpus_storage.add_turn.return_value = 0
        result = pipeline.process_message("conv-1", "msg", use_deliberation=True)
        assert isinstance(result, PipelineResponse)

    def test_deliberation_import_error_gives_fallback(self):
        pipeline = _make_pipeline()
        pipeline.corpus_storage.add_turn.return_value = 0
        with patch("builtins.__import__", side_effect=ImportError("no deliberation")):
            result = pipeline.process_message("conv-1", "msg", use_deliberation=True)
        assert isinstance(result, PipelineResponse)


# ── CorpusPipeline.end_conversation ──────────────────────────────────────────

class TestEndConversation:
    def test_calls_save_to_jsonl_when_conv_exists(self):
        pipeline = _make_pipeline()
        mock_conv = MagicMock()
        pipeline.corpus_storage.get_conversation.return_value = mock_conv
        pipeline.end_conversation("conv-1")
        pipeline.corpus_storage.save_to_jsonl.assert_called_once_with(mock_conv)

    def test_no_error_when_conv_not_found(self):
        pipeline = _make_pipeline()
        pipeline.corpus_storage.get_conversation.return_value = None
        pipeline.end_conversation("missing-conv")  # should not raise


# ── CorpusPipeline.get_stats ─────────────────────────────────────────────────

class TestGetStats:
    def test_returns_combined_dict(self):
        pipeline = _make_pipeline()
        pipeline.consent_manager.get_consent_stats.return_value = {"total": 5}
        pipeline.corpus_storage.get_corpus_stats.return_value = {"conversations": 3}
        stats = pipeline.get_stats()
        assert stats["consent"]["total"] == 5
        assert stats["corpus"]["conversations"] == 3


# ── create_corpus_pipeline factory ───────────────────────────────────────────

class TestCreateCorpusPipeline:
    def test_returns_corpus_pipeline_instance(self):
        with (
            patch("tonesoul.corpus.pipeline.ConsentManager"),
            patch("tonesoul.corpus.pipeline.CorpusStorage"),
        ):
            result = create_corpus_pipeline(
                consent_db=":memory:",
                corpus_db=":memory:",
                corpus_jsonl="/dev/null",
            )
        assert isinstance(result, CorpusPipeline)
