from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from memory.consolidator import MemoryConsolidator
from tonesoul.memory.crystallizer import Crystal, MemoryCrystallizer


def _iso_days_ago(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def test_crystallize_generates_expected_rules(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=3)
    patterns = {
        "verdicts": {"block": 4, "approve": 6},
        "low_tension_approvals": 5,
        "autonomous_high_delta": 3,
        "collapse_warnings": {"autonomous_high_delta_without_trigger": 1},
    }

    crystals = crystallizer.crystallize(patterns)

    assert len(crystals) == 4
    assert any("avoid" in c.rule for c in crystals)
    assert any("prefer" in c.rule for c in crystals)
    assert any("attention" in c.rule for c in crystals)
    assert any("critical" in c.rule for c in crystals)
    assert len(crystallizer.load_crystals()) == 4


def test_crystallize_respects_min_frequency(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=3)
    patterns = {
        "verdicts": {"block": 2, "approve": 2},
        "low_tension_approvals": 4,
        "autonomous_high_delta": 2,
        "collapse_warnings": {},
    }

    crystals = crystallizer.crystallize(patterns)

    assert crystals == []
    assert crystallizer.load_crystals() == []


def test_crystals_weight_stays_within_unit_interval(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1)
    patterns = {
        "verdicts": {"block": 3, "approve": 8},
        "low_tension_approvals": 8,
        "autonomous_high_delta": 4,
        "collapse_warnings": {"warn": 2},
    }
    crystals = crystallizer.crystallize(patterns)

    assert len(crystals) >= 3
    for crystal in crystals:
        assert 0.0 <= crystal.weight <= 1.0


def test_top_crystals_sorted_by_weight_access_and_recency(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    entries = [
        Crystal(
            rule="rule-low",
            source_pattern="p1",
            weight=0.7,
            created_at=_iso_days_ago(3),
            access_count=10,
            tags=["prefer"],
        ),
        Crystal(
            rule="rule-high",
            source_pattern="p2",
            weight=1.0,
            created_at=_iso_days_ago(10),
            access_count=0,
            tags=["critical"],
        ),
        Crystal(
            rule="rule-mid",
            source_pattern="p3",
            weight=0.9,
            created_at=_iso_days_ago(1),
            access_count=20,
            tags=["attention"],
        ),
    ]
    crystal_path.parent.mkdir(parents=True, exist_ok=True)
    with crystal_path.open("w", encoding="utf-8") as handle:
        for item in entries:
            handle.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")

    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1)
    top = crystallizer.top_crystals(n=2)

    assert [item.rule for item in top] == ["rule-mid", "rule-high"]


def test_load_crystals_filters_by_age(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    old = Crystal(
        rule="old-rule",
        source_pattern="old",
        weight=0.8,
        created_at=_iso_days_ago(30),
        tags=["avoid"],
    )
    fresh = Crystal(
        rule="fresh-rule",
        source_pattern="new",
        weight=0.9,
        created_at=_iso_days_ago(1),
        tags=["attention"],
    )
    with crystal_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(old.to_dict(), ensure_ascii=False) + "\n")
        handle.write(json.dumps(fresh.to_dict(), ensure_ascii=False) + "\n")

    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1)
    recent = crystallizer.load_crystals(max_age_days=7)

    assert [item.rule for item in recent] == ["fresh-rule"]


def test_memory_consolidator_calls_crystallizer(tmp_path: Path, monkeypatch):
    class DummyHippo:
        def __init__(self) -> None:
            self.items = []

        def memorize(self, **kwargs):
            self.items.append(kwargs)

    class DummyCrystallizer:
        def __init__(self) -> None:
            self.called_patterns = None

        def crystallize(self, patterns):
            self.called_patterns = patterns
            return [
                Crystal(
                    rule="attention: autonomous high-delta outputs require explicit self-check",
                    source_pattern="genesis:autonomous_high_delta x1",
                    weight=0.9,
                    created_at=_iso_days_ago(0),
                    tags=["attention"],
                )
            ]

    dummy_hippo = DummyHippo()
    dummy_crystallizer = DummyCrystallizer()
    consolidator = MemoryConsolidator(
        hippocampus=dummy_hippo,
        crystallizer=dummy_crystallizer,  # type: ignore[arg-type]
        min_episodes=1,
    )

    monkeypatch.setattr(
        consolidator,
        "_load_unconsolidated_episodes",
        lambda: [
            {
                "timestamp": _iso_days_ago(0),
                "is_mine": True,
                "verdict": "approve",
                "genesis": "autonomous",
                "tsr_delta_norm": 0.8,
                "context": {"tension": 0.2},
            }
        ],
    )
    monkeypatch.setattr(consolidator, "_form_semantics", lambda patterns: [])
    monkeypatch.setattr(consolidator.state, "mark_consolidated", lambda timestamp, count: None)

    result = consolidator.consolidate(force=True)

    assert dummy_crystallizer.called_patterns is not None
    assert result["crystals_formed"] == 1
    assert result["crystals_generated"] == 1
    assert isinstance(result["crystals"], list)


def test_crystallize_adds_resonance_rule_when_convergence_count_high(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=2)
    patterns = {
        "verdicts": {"block": 1, "approve": 1},
        "low_tension_approvals": 0,
        "autonomous_high_delta": 0,
        "collapse_warnings": {},
        "resonance_convergences": 3,
    }

    crystals = crystallizer.crystallize(patterns)

    assert any("genuine resonance" in c.rule for c in crystals)
    assert any("resonance" in c.tags for c in crystals)


def test_crystallizer_dedupes_same_rule_and_keeps_latest_pattern(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=2)

    first = {
        "verdicts": {"block": 3, "approve": 0},
        "low_tension_approvals": 0,
        "autonomous_high_delta": 0,
        "collapse_warnings": {},
        "resonance_convergences": 0,
    }
    second = {
        "verdicts": {"block": 5, "approve": 0},
        "low_tension_approvals": 0,
        "autonomous_high_delta": 0,
        "collapse_warnings": {},
        "resonance_convergences": 0,
    }

    crystallizer.crystallize(first)
    crystallizer.crystallize(second)

    loaded = crystallizer.load_crystals()
    avoid_rules = [c for c in loaded if "avoid high-risk actions" in c.rule]
    assert len(avoid_rules) == 1
    assert avoid_rules[0].source_pattern == "verdict:block x5"


def test_crystallizer_retains_top_weighted_rules_under_cap(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(
        crystal_path=crystal_path,
        min_frequency=1,
        max_crystals_keep=2,
    )
    crystallizer._append_crystals(
        [
            Crystal(
                rule="rule-low",
                source_pattern="p-low",
                weight=0.2,
                created_at=_iso_days_ago(1),
                tags=["low"],
            ),
            Crystal(
                rule="rule-mid",
                source_pattern="p-mid",
                weight=0.7,
                created_at=_iso_days_ago(1),
                tags=["mid"],
            ),
            Crystal(
                rule="rule-high",
                source_pattern="p-high",
                weight=0.9,
                created_at=_iso_days_ago(1),
                tags=["high"],
            ),
        ]
    )

    loaded = crystallizer.load_crystals()
    assert len(loaded) == 2
    assert {item.rule for item in loaded} == {"rule-high", "rule-mid"}


def test_freshness_decay_marks_old_crystal_needs_verification(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(
        crystal_path=crystal_path,
        min_frequency=1,
        freshness_half_life_days=10,
    )
    old = Crystal(
        rule="old-support-rule",
        source_pattern="old",
        weight=0.8,
        created_at=_iso_days_ago(30),
        tags=["old"],
    )
    crystallizer._write_crystals([old])

    loaded = crystallizer.load_crystals()
    assert len(loaded) == 1
    assert loaded[0].freshness_score < 0.55
    assert loaded[0].freshness_status in {"needs_verification", "stale"}


def test_mark_support_refreshes_freshness_status(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(
        crystal_path=crystal_path,
        min_frequency=1,
        freshness_half_life_days=10,
    )
    crystal = Crystal(
        rule="refresh-me",
        source_pattern="legacy",
        weight=0.7,
        created_at=_iso_days_ago(45),
        tags=["legacy"],
    )
    crystallizer._write_crystals([crystal])

    assert crystallizer.mark_support("refresh-me") is True
    loaded = crystallizer.load_crystals()
    assert loaded[0].last_supported_at is not None
    assert loaded[0].freshness_status == "active"


def test_top_crystals_uses_effective_weight_with_freshness(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(
        crystal_path=crystal_path,
        min_frequency=1,
        freshness_half_life_days=10,
    )
    stale_high = Crystal(
        rule="stale-high",
        source_pattern="stale",
        weight=1.0,
        created_at=_iso_days_ago(120),
        tags=["stale"],
    )
    fresh_mid = Crystal(
        rule="fresh-mid",
        source_pattern="fresh",
        weight=0.75,
        created_at=_iso_days_ago(1),
        tags=["fresh"],
    )
    crystallizer._write_crystals([stale_high, fresh_mid])

    top = crystallizer.top_crystals(n=1)
    assert top[0].rule == "fresh-mid"


def test_freshness_summary_counts_statuses(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(
        crystal_path=crystal_path,
        min_frequency=1,
        freshness_half_life_days=10,
    )
    crystals = [
        Crystal(
            rule="fresh-rule",
            source_pattern="new",
            weight=0.8,
            created_at=_iso_days_ago(1),
            tags=["fresh"],
        ),
        Crystal(
            rule="aging-rule",
            source_pattern="mid",
            weight=0.8,
            created_at=_iso_days_ago(18),
            tags=["aging"],
        ),
        Crystal(
            rule="stale-rule",
            source_pattern="old",
            weight=0.8,
            created_at=_iso_days_ago(100),
            tags=["stale"],
        ),
    ]
    crystallizer._write_crystals(crystals)

    summary = crystallizer.freshness_summary(top_n_stale=2)

    assert summary["total_crystals"] == 3
    assert summary["active_count"] >= 1
    assert summary["stale_count"] >= 1
    assert isinstance(summary["stale_rules"], list)


# Phase 543: retire_crystal tests


def test_retire_crystal_removes_matching_rule(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1)
    crystallizer._write_crystals(
        [
            Crystal(
                rule="keep-me",
                source_pattern="a",
                weight=0.8,
                created_at=_iso_days_ago(1),
                tags=["a"],
            ),
            Crystal(
                rule="remove-me",
                source_pattern="b",
                weight=0.6,
                created_at=_iso_days_ago(1),
                tags=["b"],
            ),
        ]
    )

    removed = crystallizer.retire_crystal("remove-me")

    assert removed is True
    loaded = crystallizer.load_crystals()
    assert len(loaded) == 1
    assert loaded[0].rule == "keep-me"


def test_retire_crystal_case_insensitive(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1)
    crystallizer._write_crystals(
        [
            Crystal(
                rule="Remove Me",
                source_pattern="x",
                weight=0.5,
                created_at=_iso_days_ago(1),
                tags=["x"],
            )
        ]
    )

    assert crystallizer.retire_crystal("  REMOVE ME  ") is True
    assert crystallizer.load_crystals() == []


def test_retire_crystal_returns_false_when_not_found(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1)
    crystallizer._write_crystals(
        [
            Crystal(
                rule="keep", source_pattern="x", weight=0.5, created_at=_iso_days_ago(1), tags=["x"]
            )
        ]
    )

    assert crystallizer.retire_crystal("nonexistent") is False
    assert len(crystallizer.load_crystals()) == 1


def test_retire_crystal_empty_string_returns_false(tmp_path: Path):
    crystal_path = tmp_path / "crystals.jsonl"
    crystallizer = MemoryCrystallizer(crystal_path=crystal_path, min_frequency=1)

    assert crystallizer.retire_crystal("") is False
    assert crystallizer.retire_crystal(None) is False
