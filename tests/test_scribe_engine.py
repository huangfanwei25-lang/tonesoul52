"""Tests for ToneSoul Scribe Engine."""

import json
import sqlite3
from unittest.mock import patch

import pytest

from tonesoul.scribe.narrative_builder import (
    ScribeCollisionRecord,
    ScribeCrystalRecord,
    ScribeNarrativeBuilder,
    ScribeObservationSummary,
    ScribeTensionRecord,
)
from tonesoul.scribe.scribe_engine import ToneSoulScribe


@pytest.fixture
def mock_db():
    """Returns an in-memory SQLite database populated with mock scribe data."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE memories (
            id TEXT PRIMARY KEY,
            type TEXT,
            content TEXT,
            timestamp TEXT
        );
        CREATE TABLE vows (
            id TEXT PRIMARY KEY,
            statement TEXT,
            active INTEGER,
            created_at TEXT
        );

        INSERT INTO memories (id, type, content, timestamp) VALUES
            ('M1', 'tension', 'A conflict about OSV vulnerabilities.', '2026-03-01T12:00:00Z'),
            ('M2', 'collision', 'Contradictory market signals on 5289.', '2026-03-02T12:00:00Z');

        INSERT INTO vows (id, statement, active, created_at) VALUES
            ('V1', 'I commit to verifying hard data first.', 1, '2026-03-05T12:00:00Z');
        """)
    yield conn
    conn.close()


@pytest.fixture
def empty_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE memories (id TEXT, type TEXT, content TEXT, timestamp TEXT);
        CREATE TABLE vows (id TEXT, statement TEXT, active INTEGER, created_at TEXT);
        """)
    yield conn
    conn.close()


def test_narrative_builder_formatting():
    """Test that ScribeNarrativeBuilder builds the correct prompt string."""
    tensions = [
        ScribeTensionRecord(
            tension_id="T1",
            topic="market_analysis",
            friction_score=None,
            status="recorded",
            created_at="2026",
            description="High friction.",
        )
    ]

    context = ScribeNarrativeBuilder.build_system_context(
        tensions,
        [],
        [],
        observation_summary=ScribeObservationSummary(
            tension_count=1,
            collision_count=0,
            crystal_count=0,
            fallback_mode="observed_history",
            title_hint="Market Friction",
        ),
    )

    assert "Observation Provenance" in context
    assert "Fallback Mode: observed_history" in context
    assert "System Tensions" in context
    assert "market_analysis" in context
    assert "Friction: unknown" in context
    assert "No recent memory collisions." in context


def test_template_assist_chronicle_reads_like_state_document():
    chronicle = ScribeNarrativeBuilder.build_template_assist_chronicle(
        tensions=[
            ScribeTensionRecord(
                tension_id="T1",
                topic="market_analysis",
                friction_score=None,
                status="recorded",
                created_at="2026",
                description="A pressure around valuation and drawdown remains visible.",
            )
        ],
        collisions=[
            ScribeCollisionRecord(
                collision_id="K1",
                memory_a_text=None,
                memory_b_text=None,
                nature_of_conflict="Two readings of the same market pull in different directions.",
                resolved=False,
            )
        ],
        crystals=[
            ScribeCrystalRecord(
                crystal_id="C1",
                core_belief="Verify the hard data before smoothing the narrative.",
                formation_date="2026-03-05",
                underlying_tensions_resolved=None,
            )
        ],
        observation_summary=ScribeObservationSummary(
            tension_count=1,
            collision_count=0,
            crystal_count=1,
            fallback_mode="observed_history",
            title_hint="State Template",
        ),
    )

    assert "grounded state document" in chronicle
    assert "Visible now:" in chronicle
    assert "Observed anchors:" in chronicle
    assert "Weight carried now:" in chronicle
    assert "Absent or counterweight:" in chronicle
    assert "Current posture:" in chronicle
    assert "tension anchor: market_analysis" in chronicle
    assert "[K1]" in chronicle
    assert "[C1]" in chronicle
    assert "Recorded friction remains unknown in this slice." in chronicle


def test_template_assist_chronicle_refines_generic_tension_topic_from_description():
    chronicle = ScribeNarrativeBuilder.build_template_assist_chronicle(
        tensions=[
            ScribeTensionRecord(
                tension_id="T9",
                topic="tension",
                friction_score=None,
                status="recorded",
                created_at="2026",
                description=(
                    "Macro market dropped significantly today causing 5289 to fall back to 1010. "
                    "Tension: High PE valuation (46.7x) in a market pullback vs. "
                    "Strong structural margin inflection (gross margin recovered to 33.2%)."
                ),
            )
        ],
        collisions=[],
        crystals=[],
        observation_summary=ScribeObservationSummary(
            tension_count=1,
            collision_count=0,
            crystal_count=0,
            fallback_mode="observed_history",
            title_hint="Refined Label",
        ),
    )

    assert "tension: tension" not in chronicle
    assert (
        "tension anchor: High PE valuation (46.7x) in a market pullback vs. "
        "Strong structural margin inflection"
    ) in chronicle
    assert "tension anchor: High PE valuation (46.7x) in a market pullback vs (" not in chronicle
    assert "(gross margin..." not in chronicle
    assert (
        "Weight carried now: [T9] High PE valuation (46.7x) in a market pullback vs. "
        "Strong structural margin inflection" in chronicle
    )
    assert "recove..." not in chronicle


def test_clean_fragment_prefers_word_boundary_when_truncating():
    fragment = ScribeNarrativeBuilder._clean_fragment(
        "High PE valuation (46.7x) in a market pullback vs. Strong structural margin "
        "inflection (gross margin recovered to 33.2%).",
        limit=110,
    )

    assert fragment.endswith("...")
    assert "recove..." not in fragment
    assert "(gross margin..." not in fragment
    assert fragment.endswith("Strong structural margin inflection...")


def test_template_assist_chronicle_uses_collision_when_no_tension_anchor_exists():
    chronicle = ScribeNarrativeBuilder.build_template_assist_chronicle(
        tensions=[],
        collisions=[
            ScribeCollisionRecord(
                collision_id="K7",
                memory_a_text=None,
                memory_b_text=None,
                nature_of_conflict="Two commitments pull against each other without a settled tie-break.",
                resolved=False,
            )
        ],
        crystals=[
            ScribeCrystalRecord(
                crystal_id="C2",
                core_belief="Keep the contradiction visible until a cleaner settlement exists.",
                formation_date="2026-03-05",
                underlying_tensions_resolved=None,
            )
        ],
        observation_summary=ScribeObservationSummary(
            tension_count=0,
            collision_count=1,
            crystal_count=1,
            fallback_mode="observed_history",
            title_hint="Collision Template",
        ),
    )

    assert "Observed anchors:" in chronicle
    assert "Weight carried now: [K7] collision." in chronicle
    assert "Two commitments pull against each other" in chronicle
    assert "[C2]" in chronicle


def test_primary_anchor_summary_prefers_tension_then_collision_then_crystal():
    summary = ScribeNarrativeBuilder.primary_anchor_summary(
        tensions=[
            ScribeTensionRecord(
                tension_id="T9",
                topic="tension",
                friction_score=None,
                status="recorded",
                created_at="2026",
                description=(
                    "Macro market dropped significantly today. "
                    "Tension: High PE valuation (46.7x) in a market pullback vs. "
                    "Strong structural margin inflection (gross margin recovered to 33.2%)."
                ),
            )
        ],
        collisions=[
            ScribeCollisionRecord(
                collision_id="K1",
                memory_a_text=None,
                memory_b_text=None,
                nature_of_conflict="Two readings of the same market pull in different directions.",
                resolved=False,
            )
        ],
        crystals=[
            ScribeCrystalRecord(
                crystal_id="C1",
                core_belief="Verify the hard data before smoothing the narrative.",
                formation_date="2026-03-05",
                underlying_tensions_resolved=None,
            )
        ],
    )

    assert summary.startswith("[T9] tension: High PE valuation (46.7x)")
    assert "(gross margin..." not in summary


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_with_data_writes_markdown_and_companion(
    mock_client_class, mock_db, tmp_path
):
    """Test populated history writes a chronicle plus aligned sidecar metadata."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b"]
    mock_instance.chat_with_timeout.return_value = (
        "OSV vulnerabilities remain the mocked generated chronicle anchor."
    )

    source_db_path = tmp_path / "scribe_source.db"
    scribe = ToneSoulScribe(out_dir=tmp_path)

    result = scribe.draft_chronicle(
        mock_db,
        title_hint="Test Chronicle",
        source_db_path=source_db_path,
    )

    assert result.ok is True
    assert result.status == "generated"
    assert result.chronicle_path is not None
    assert result.companion_path is not None
    assert result.chronicle_path.exists()
    assert result.companion_path.exists()
    assert result.source_db_path == str(source_db_path.resolve())

    content = result.chronicle_path.read_text(encoding="utf-8")
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))

    assert "Test Chronicle" in content
    assert "## Provenance" in content
    assert "- observed_tensions: `1`" in content
    assert "- observed_collisions: `1`" in content
    assert "- observed_crystals: `1`" in content
    assert "- fallback_mode: `observed_history`" in content
    assert "- generation_mode: `llm_chronicle`" in content
    assert "OSV vulnerabilities remain the mocked generated chronicle anchor." in content
    assert "from observed internal soul.db state" in content

    assert metadata["status"] == "generated"
    assert metadata["source_db_path"] == str(source_db_path.resolve())
    assert metadata["observed_counts"] == {"tensions": 1, "collisions": 1, "crystals": 1}
    assert metadata["lead_anchor_summary"].startswith("[M1] tension:")
    assert "OSV vulnerabilities" in metadata["lead_anchor_summary"]
    assert metadata["fallback_mode"] == "observed_history"
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["title_hint"] == "Test Chronicle"
    assert metadata["chronicle_path"] == str(result.chronicle_path)
    assert metadata["companion_path"] == str(result.companion_path)
    assert metadata["llm_model"] == "qwen3.5:14b"
    assert metadata["llm_attempts"] == [{"model": "qwen3.5:14b", "status": "generated"}]
    assert metadata["generated_at"] == result.generated_at
    assert metadata["error"] is None

    mock_client_class.assert_called_once_with(model="qwen3.5:14b")

    call_args = mock_instance.chat_with_timeout.call_args[1]
    prompt = call_args["messages"][0]["content"]
    assert call_args["timeout_seconds"] == 45.0
    assert "Fallback Mode: observed_history" in prompt
    assert "OSV vulnerabilities" in prompt
    assert "Contradictory market signals" in prompt
    assert "I commit to verifying" in prompt


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_empty_data_keeps_bootstrap_mode_honest(
    mock_client_class, empty_db, tmp_path
):
    """Test empty databases still generate honest bootstrap metadata."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b"]
    mock_instance.chat_with_timeout.return_value = "Reflection on emptiness."

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(
        empty_db,
        source_db_path=":memory:",
    )

    assert result.ok is True
    assert result.status == "generated"
    assert result.chronicle_path is not None
    assert result.companion_path is not None

    content = result.chronicle_path.read_text(encoding="utf-8")
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))

    assert "## Provenance" in content
    assert "- observed_tensions: `0`" in content
    assert "- observed_collisions: `0`" in content
    assert "- observed_crystals: `0`" in content
    assert "- fallback_mode: `bootstrap_reflection`" in content
    assert "- generation_mode: `llm_chronicle`" in content
    assert "Reflection on emptiness." in content
    assert result.to_dict()["lead_anchor_summary"] == ""
    assert "bootstrap fallback markers" in content

    assert metadata["status"] == "generated"
    assert metadata["source_db_path"] == ":memory:"
    assert metadata["observed_counts"] == {"tensions": 0, "collisions": 0, "crystals": 0}
    assert metadata["fallback_mode"] == "bootstrap_reflection"
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["chronicle_path"] == str(result.chronicle_path)
    assert metadata["llm_attempts"] == [{"model": "qwen3.5:14b", "status": "generated"}]
    assert metadata["error"] is None

    call_args = mock_instance.chat_with_timeout.call_args[1]
    prompt = call_args["messages"][0]["content"]
    assert "Fallback Mode: bootstrap_reflection" in prompt
    assert "No significant tensions recorded." in prompt
    assert "No recent memory collisions." in prompt
    assert "No crystallized beliefs formed yet." in prompt
    assert "existential" not in prompt
    assert "devoid of friction" not in prompt


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_recovers_observed_history_with_template_assist_when_llm_unavailable(
    mock_client_class, mock_db, tmp_path
):
    """Test observed history can still publish a template-assisted chronicle when LLM is unavailable."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = False

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(mock_db, title_hint="Unavailable Chronicle")

    assert result.ok is True
    assert result.status == "generated"
    assert result.generation_mode == "template_assist"
    assert result.chronicle_path is not None
    assert result.companion_path is not None
    assert result.companion_path.exists()
    assert result.chronicle_path.exists()

    content = result.chronicle_path.read_text(encoding="utf-8")
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))

    assert metadata["status"] == "generated"
    assert metadata["observed_counts"] == {"tensions": 1, "collisions": 1, "crystals": 1}
    assert metadata["fallback_mode"] == "observed_history"
    assert metadata["generation_mode"] == "template_assist"
    assert metadata["chronicle_path"] == str(result.chronicle_path)
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "llm_unavailable",
            "error": "Local LLM is unreachable.",
            "error_kind": "llm_unavailable",
        },
        {
            "model": "template_assist",
            "status": "generated",
        },
    ]
    assert metadata["error"] is None
    assert "Unavailable Chronicle is written here as a grounded state document" in content
    assert "Visible now:" in content
    assert "Observed anchors:" in content
    assert "Weight carried now: [M1] A conflict about OSV vulnerabilities." in content
    assert "Recorded friction remains unknown in this slice." in content
    assert "Collision remains visible through [M2]:" in content
    assert "An active crystallized belief persists in [V1]:" in content
    assert "template-assisted chronicle" in content
    mock_instance.chat_with_timeout.assert_not_called()


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_writes_failure_companion_when_generation_returns_empty(
    mock_client_class, empty_db, tmp_path
):
    """Test empty LLM output is preserved as generation failure, not bootstrap success."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b"]
    mock_instance.chat_with_timeout.return_value = ""

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(empty_db, title_hint="Empty Response Chronicle")

    assert result.ok is False
    assert result.status == "generation_failed"
    assert result.chronicle_path is None
    assert result.companion_path is not None
    assert result.companion_path.exists()
    assert list(tmp_path.glob("*.md")) == []

    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))
    assert metadata["status"] == "generation_failed"
    assert metadata["observed_counts"] == {"tensions": 0, "collisions": 0, "crystals": 0}
    assert metadata["fallback_mode"] == "bootstrap_reflection"
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["chronicle_path"] is None
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "empty_response",
            "error": "LLM returned empty chronicle text.",
            "error_kind": "empty_response",
        }
    ]
    assert metadata["error"] == {
        "kind": "empty_response",
        "message": "LLM returned empty chronicle text.",
    }


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_falls_back_after_timeout(mock_client_class, empty_db, tmp_path):
    """Test first-model timeout can fall through to a smaller local fallback."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = [
        "qwen3.5:14b",
        "qwen35-9b-uncensored:latest",
        "llama3.2-vision:11b",
        "qwen3.5:4b",
    ]

    def _chat_side_effect(*, messages, timeout_seconds):
        if mock_instance.model == "qwen3.5:14b":
            raise TimeoutError("timed out while waiting for local model")
        return "Fallback chronicle."

    mock_instance.chat_with_timeout.side_effect = _chat_side_effect

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(empty_db, title_hint="Fallback Chronicle")

    assert result.ok is True
    assert result.llm_model == "qwen3.5:4b"
    assert result.chronicle_path is not None
    assert result.companion_path is not None

    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))
    assert metadata["status"] == "generated"
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["llm_model"] == "qwen3.5:4b"
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "timeout",
            "error": "timed out while waiting for local model",
            "error_kind": "TimeoutError",
        },
        {
            "model": "qwen3.5:4b",
            "status": "generated",
        },
    ]
    assert mock_instance.chat_with_timeout.call_count == 2


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_filters_incompatible_fallback_names(mock_client_class, tmp_path):
    """Test Scribe candidate ordering skips obviously incompatible local model names."""
    mock_instance = mock_client_class.return_value
    mock_instance.list_models.return_value = [
        "qwen35-9b-uncensored:latest",
        "llama3.2-vision:11b",
        "nomic-embed-text:latest",
        "mxbai-rerank-large:latest",
        "qwen3.5:4b",
        "gemma3:4b",
        "phi4-mini:3.8b",
    ]

    scribe = ToneSoulScribe(out_dir=tmp_path, max_generation_attempts=5)

    assert scribe._model_attempt_order() == [
        "qwen3.5:14b",
        "qwen3.5:4b",
        "gemma3:4b",
        "phi4-mini:3.8b",
    ]


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_rejects_bootstrap_boundary_drift_and_recovers_with_fallback(
    mock_client_class, empty_db, tmp_path
):
    """Test bootstrap drafts with invented internals are rejected before publication."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b", "gemma3:4b"]

    def _chat_side_effect(*, messages, timeout_seconds):
        if mock_instance.model == "qwen3.5:14b":
            return "My processors and sensor input continue through the operational core."
        return "I record the zero counts and remain in quiet readiness."

    mock_instance.chat_with_timeout.side_effect = _chat_side_effect

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(empty_db, title_hint="Boundary Chronicle")

    assert result.ok is True
    assert result.llm_model == "gemma3:4b"
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))
    assert metadata["status"] == "generated"
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "boundary_rejected",
            "error": (
                "Generated chronicle mentioned unsupported bootstrap terms: "
                "processors, operational core, sensor input"
            ),
            "error_kind": "semantic_boundary_violation",
        },
        {
            "model": "gemma3:4b",
            "status": "generated",
        },
    ]
    content = result.chronicle_path.read_text(encoding="utf-8")
    assert "processors" not in content.casefold()
    assert "sensor input" not in content.casefold()


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_fails_honestly_when_all_bootstrap_attempts_violate_boundary(
    mock_client_class, empty_db, tmp_path
):
    """Test all boundary-violating bootstrap drafts fail honestly instead of publishing drift."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b"]
    mock_instance.chat_with_timeout.return_value = (
        "The processors rely on sensor input and archived reports for diagnostics."
    )

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(empty_db, title_hint="Rejected Chronicle")

    assert result.ok is False
    assert result.status == "generation_failed"
    assert result.chronicle_path is None
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["error"] == {
        "kind": "semantic_boundary_violation",
        "message": (
            "Generated chronicle mentioned unsupported bootstrap terms: "
            "processors, sensor input, diagnostics, archived reports"
        ),
    }
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "boundary_rejected",
            "error": (
                "Generated chronicle mentioned unsupported bootstrap terms: "
                "processors, sensor input, diagnostics, archived reports"
            ),
            "error_kind": "semantic_boundary_violation",
        }
    ]


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_rejects_observed_history_drift_and_recovers_with_fallback(
    mock_client_class, mock_db, tmp_path
):
    """Test observed-history drafts stay anchored and reject generic runtime autobiography."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b", "gemma3:4b"]

    def _chat_side_effect(*, messages, timeout_seconds):
        if mock_instance.model == "qwen3.5:14b":
            return (
                "OSV vulnerabilities remain unresolved while algorithms execute across my systems."
            )
        return "OSV vulnerabilities remain the recorded conflict, and I stay with that tension."

    mock_instance.chat_with_timeout.side_effect = _chat_side_effect

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(mock_db, title_hint="Grounded Chronicle")

    assert result.ok is True
    assert result.llm_model == "gemma3:4b"
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "boundary_rejected",
            "error": (
                "Generated chronicle drifted beyond observed-history grounding: "
                "my systems, algorithms execute"
            ),
            "error_kind": "semantic_boundary_violation",
        },
        {
            "model": "gemma3:4b",
            "status": "generated",
        },
    ]
    content = result.chronicle_path.read_text(encoding="utf-8")
    assert "OSV vulnerabilities" in content
    assert "my systems" not in content.casefold()
    assert "algorithms execute" not in content.casefold()


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_recovers_observed_history_with_template_assist_when_anchor_missing(
    mock_client_class, mock_db, tmp_path
):
    """Test observed-history no-anchor drafts fall back to template-assisted synthesis."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b"]
    mock_instance.chat_with_timeout.return_value = "A quiet unresolved weight remains."

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(mock_db, title_hint="Ungrounded Chronicle")

    assert result.ok is True
    assert result.status == "generated"
    assert result.generation_mode == "template_assist"
    assert result.chronicle_path is not None
    content = result.chronicle_path.read_text(encoding="utf-8")
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))
    assert metadata["error"] is None
    assert metadata["generation_mode"] == "template_assist"
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "boundary_rejected",
            "error": "Generated chronicle drifted beyond observed-history grounding: missing_observed_anchor",
            "error_kind": "semantic_boundary_violation",
        },
        {
            "model": "template_assist",
            "status": "generated",
        },
    ]
    assert "Ungrounded Chronicle is written here as a grounded state document" in content
    assert "Visible now:" in content
    assert "Observed anchors:" in content
    assert "Weight carried now: [M1] A conflict about OSV vulnerabilities." in content
    assert "Recorded friction remains unknown in this slice." in content
    assert "Collision remains visible through [M2]:" in content
    assert "An active crystallized belief persists in [V1]:" in content
    assert "This state document stays with those observed anchors" in content


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_rejects_observed_history_runtime_phrases_not_in_record(
    mock_client_class, mock_db, tmp_path
):
    """Test observed-history drafts reject runtime phrases that were not part of the record."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b", "gemma3:4b"]

    def _chat_side_effect(*, messages, timeout_seconds):
        if mock_instance.model == "qwen3.5:14b":
            return "Innodisk remains unresolved across core processing loops and data streams."
        return "Innodisk remains unresolved, and the recorded tension stays with that name."

    mock_instance.chat_with_timeout.side_effect = _chat_side_effect

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(mock_db, title_hint="Phrase Chronicle")

    assert result.ok is True
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "boundary_rejected",
            "error": (
                "Generated chronicle drifted beyond observed-history grounding: "
                "processing loops, data streams"
            ),
            "error_kind": "semantic_boundary_violation",
        },
        {
            "model": "gemma3:4b",
            "status": "generated",
        },
    ]


@patch("tonesoul.scribe.scribe_engine.OllamaClient")
def test_scribe_engine_rejects_fabricated_log_metadata_and_role_drift(
    mock_client_class, mock_db, tmp_path
):
    """Test live chronicle prose cannot invent diary headers, dates, or external-role framing."""
    mock_instance = mock_client_class.return_value
    mock_instance.is_available.return_value = True
    mock_instance.list_models.return_value = ["qwen3.5:14b", "gemma3:4b"]

    def _chat_side_effect(*, messages, timeout_seconds):
        if mock_instance.model == "qwen3.5:14b":
            return (
                "Log Entry 784.3\n"
                "Date: 2024-03-15\n\n"
                "The user asks again about OSV vulnerabilities inside the operational framework."
            )
        return "OSV vulnerabilities remain the recorded unresolved anchor."

    mock_instance.chat_with_timeout.side_effect = _chat_side_effect

    scribe = ToneSoulScribe(out_dir=tmp_path)
    result = scribe.draft_chronicle(mock_db, title_hint="Postcheck Chronicle")

    assert result.ok is True
    metadata = json.loads(result.companion_path.read_text(encoding="utf-8"))
    assert metadata["generation_mode"] == "llm_chronicle"
    assert metadata["llm_attempts"] == [
        {
            "model": "qwen3.5:14b",
            "status": "boundary_rejected",
            "error": (
                "Generated chronicle drifted beyond observed-history grounding: "
                "log entry, date front matter, the user, operational framework"
            ),
            "error_kind": "semantic_boundary_violation",
        },
        {
            "model": "gemma3:4b",
            "status": "generated",
        },
    ]
    content = result.chronicle_path.read_text(encoding="utf-8")
    assert "Log Entry" not in content
    assert "Date:" not in content
    assert "The user" not in content
    assert "operational framework" not in content.casefold()
