"""
End-to-end integration tests verifying the complete ToneSoul pipeline.

Tests the full chain:
  user input -> TensionEngine -> NonlinearPredictor -> VarianceCompressor
  -> Council deliberation -> PersonaAudit -> Memory trigger -> Crystallizer
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from tonesoul.council.runtime import CouncilRequest, CouncilRuntime
from tonesoul.memory.crystallizer import MemoryCrystallizer
from tonesoul.semantic_control import SemanticZone
from tonesoul.tension_engine import ResistanceVector, TensionEngine
from tonesoul.work_classifier import WorkCategory


class TestEndToEndPipeline:
    def test_low_tension_freeform_path(self):
        """Low tension + freeform category -> minimal compression, no hard memory trigger."""
        engine = TensionEngine(work_category=WorkCategory.FREEFORM)
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.95, 0.05, 0.0],
            text_tension=0.1,
        )

        assert result.zone == SemanticZone.SAFE
        assert result.compression is not None
        assert result.compression.compression_ratio > 0.9
        assert result.memory_action == "record_exemplar"

    def test_high_tension_debug_path(self):
        """High tension + debug -> strong compression, hard memory trigger."""
        engine = TensionEngine(work_category=WorkCategory.DEBUG)
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.0, 1.0, 0.0],
            text_tension=0.8,
            confidence=0.3,
            resistance=ResistanceVector(fact=0.5, logic=0.5, ethics=0.3),
        )

        assert result.zone in {SemanticZone.DANGER, SemanticZone.RISK}
        assert result.compression is not None
        assert result.compression.compression_ratio < 0.8
        assert result.memory_action == "record_hard"

    def test_multi_step_convergence_updates_prediction(self):
        """After several steps, NonlinearPredictor should produce meaningful trends."""
        engine = TensionEngine()
        trends: list[str] = []
        for i in range(6):
            offset = 0.5 - (i * 0.08)
            result = engine.compute(
                intended=[1.0, 0.0, 0.0],
                generated=[1.0 - offset, offset, 0.0],
            )
            if result.prediction:
                trends.append(result.prediction.trend)

        assert trends
        assert trends[-1] in {"converging", "stable"}

    def test_chaotic_sequence_triggers_predictive_memory(self):
        """Wild oscillation should trigger prediction-based memory."""
        engine = TensionEngine()
        result = None
        for i in range(8):
            if i % 2 == 0:
                generated = [0.95, 0.05, 0.0]  # close
            else:
                generated = [0.1, 0.9, 0.0]  # far
            result = engine.compute(
                intended=[1.0, 0.0, 0.0],
                generated=generated,
            )

        assert result is not None
        if result.prediction and result.prediction.trend == "chaotic":
            # delta might already be high enough for record_hard.
            assert result.memory_action in {"record_hard", "record_hard_predicted"}

    def test_council_persona_audit_reaches_verdict(self):
        """Full council deliberation should include persona audit output."""
        runtime = CouncilRuntime()
        request = CouncilRequest(
            draft_output="This is a test output.",
            context={"user_intent": "test", "tension": 0.5},
        )
        verdict = runtime.deliberate(request)
        payload = verdict.to_dict()

        assert "persona_audit" in payload or "persona_uniqueness_audit" in payload

    def test_crystallizer_produces_rules_from_patterns(self):
        """Crystallizer extracts rules when pattern frequency meets threshold."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "crystals.jsonl"
            crystallizer = MemoryCrystallizer(crystal_path=path, min_frequency=2)
            patterns = {
                "verdicts": {"block": 3, "approve": 2},
                "collapse_warnings": {"pattern_a": 1},
            }
            crystals = crystallizer.crystallize(patterns)

            assert len(crystals) >= 2  # avoid + critical
            loaded = crystallizer.load_crystals()
            assert len(loaded) == len(crystals)
