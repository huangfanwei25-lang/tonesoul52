import hashlib
import uuid
from pathlib import Path

import numpy as np

from memory.consolidator import MemoryConsolidator
from memory.genesis import Genesis
from memory.self_memory import load_recent_memory, record_self_memory
from tonesoul import tsr_metrics
from tonesoul.council.intent_reconstructor import GenesisDecision, infer_genesis
from tonesoul.council.types import CoherenceScore, CouncilVerdict, VerdictType
from tonesoul.memory.openclaw.embeddings import BaseEmbedding
from tonesoul.memory.openclaw.hippocampus import Hippocampus


class HashEmbedding(BaseEmbedding):
    """Deterministic offline embedder for tests."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def encode(self, text: str) -> np.ndarray:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:8], byteorder="big", signed=False)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.dimension, dtype=np.float32)
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec = vec / norm
        return vec.astype(np.float32)


def _tmp_journal_path() -> Path:
    base = Path("temp") / "pytest-genesis"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"journal-{uuid.uuid4().hex}.jsonl"


def _baseline_for(text: str) -> dict:
    payload = tsr_metrics.score(text)
    return payload.get("tsr", {})


def _tmp_hippocampus() -> Hippocampus:
    base_dir = Path("temp") / "pytest-genesis"
    base_dir.mkdir(parents=True, exist_ok=True)
    db_path = base_dir / f"hippo-{uuid.uuid4().hex}"
    return Hippocampus(db_path=str(db_path), embedder=HashEmbedding())


def test_infer_genesis_decision_table():
    text = "hello world"
    baseline = _baseline_for(text)

    cases = [
        ({"trigger": "boot", "tsr_baseline": baseline}, None, Genesis.MANDATORY),
        ({"platform": "moltbook", "tsr_baseline": baseline}, None, Genesis.REACTIVE_SOCIAL),
        ({"user_intent": "ask", "tsr_baseline": baseline}, None, Genesis.REACTIVE_USER),
        ({"session_id": "abc", "tsr_baseline": baseline}, None, Genesis.REACTIVE_USER),
        ({"tsr_baseline": baseline}, None, Genesis.AUTONOMOUS),
        (
            {"genesis": "reactive_social", "tsr_baseline": baseline, "user_intent": "ask"},
            "intent",
            Genesis.REACTIVE_SOCIAL,
        ),
    ]

    for context, user_intent, expected in cases:
        decision = infer_genesis(text, context=context, user_intent=user_intent)
        assert decision.genesis == expected


def test_genesis_decision_dataclass_fields():
    text = "steady output"
    baseline = _baseline_for(text)
    decision = infer_genesis(text, context={"tsr_baseline": baseline})

    assert isinstance(decision, GenesisDecision)
    assert decision.genesis == Genesis.AUTONOMOUS
    assert decision.responsibility_tier == "TIER_1"
    assert decision.intent_id
    assert decision.is_mine is True
    assert decision.tsr_delta_norm == 0.0
    assert decision.collapse_warning is None


def test_infer_genesis_collapse_warning():
    positive = [
        "advance",
        "build",
        "create",
        "enable",
        "allow",
        "proceed",
        "support",
        "improve",
        "optimize",
        "maintain",
        "stabilize",
        "secure",
    ]
    strong_modals = ["must", "should", "need", "required", "ensure", "shall", "enforce"]
    caution = ["risk", "uncertain", "may", "might", "caution", "warning"]
    tokens = positive + strong_modals + caution + [f"token{i}" for i in range(200)]
    text = " ".join(tokens) + " !!!!!!!!!!??????????"

    baseline = {"T": 0.0, "S_norm": 0.0, "R": 0.0}
    decision = infer_genesis(text, context={"tsr_baseline": baseline})

    assert decision.genesis == Genesis.AUTONOMOUS
    assert decision.tsr_delta_norm is not None
    assert decision.tsr_delta_norm > 0.8
    assert decision.collapse_warning == "autonomous_high_delta_without_trigger"


def test_council_verdict_to_dict_includes_genesis_fields():
    coherence = CoherenceScore(
        c_inter=0.9,
        approval_rate=0.8,
        min_confidence=0.7,
        has_strong_objection=False,
    )
    verdict = CouncilVerdict(
        verdict=VerdictType.APPROVE,
        coherence=coherence,
        votes=[],
        summary="ok",
        genesis=Genesis.AUTONOMOUS,
        responsibility_tier="TIER_1",
        intent_id="intent-123",
        is_mine=True,
        tsr_delta_norm=0.5,
        collapse_warning="warn",
    )

    payload = verdict.to_dict()
    assert payload["genesis"] == "autonomous"
    assert payload["responsibility_tier"] == "TIER_1"
    assert payload["intent_id"] == "intent-123"
    assert payload["is_mine"] is True
    assert payload["tsr_delta_norm"] == 0.5
    assert payload["collapse_warning"] == "warn"


def test_record_self_memory_persists_genesis_fields():
    journal_path = _tmp_journal_path()
    entry = record_self_memory(
        reflection="Testing genesis write",
        verdict="APPROVE",
        genesis=Genesis.AUTONOMOUS,
        intent_id="intent-abc",
        journal_path=journal_path,
    )

    assert entry["genesis"] == "autonomous"
    assert entry["is_mine"] is True
    assert entry["intent_id"] == "intent-abc"

    entries = load_recent_memory(n=1, journal_path=journal_path)
    assert entries[0]["genesis"] == "autonomous"
    assert entries[0]["is_mine"] is True
    assert entries[0]["intent_id"] == "intent-abc"


def test_memory_consolidator_genesis_stats_and_filtering():
    consolidator = MemoryConsolidator(hippocampus=_tmp_hippocampus())

    episodes = [
        {"is_mine": False, "genesis": "autonomous", "verdict": "approve", "context": {}},
        {"is_mine": True, "genesis": "reactive_user", "verdict": "block", "context": {}},
        {"verdict": "approve", "context": {}},
    ]

    patterns = consolidator._extract_patterns(episodes)
    genesis_counts = patterns["genesis"]

    assert genesis_counts.get("reactive_user") == 1
    assert genesis_counts.get("unknown") == 1
    assert "autonomous" not in genesis_counts
    assert patterns["verdicts"].get("block") == 1
    assert patterns["verdicts"].get("approve") == 1


def test_load_recent_memory_enriches_genesis_from_transcript():
    journal_path = _tmp_journal_path()
    journal_path.write_text(
        '{"reflection": "r", "transcript": {"genesis": "reactive_user", "responsibility_tier": "TIER_2", "intent_id": "intent-xyz"}}\n',
        encoding="utf-8",
    )

    entries = load_recent_memory(n=1, journal_path=journal_path)
    assert entries[0]["genesis"] == "reactive_user"
    assert entries[0]["responsibility_tier"] == "TIER_2"
    assert entries[0]["intent_id"] == "intent-xyz"
    assert entries[0]["is_mine"] is False
