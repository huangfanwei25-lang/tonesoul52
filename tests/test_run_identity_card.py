"""Tests for scripts/run_identity_card.py (hermetic: tmp repo + injected git info)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_identity_card import _render_markdown, build_card  # noqa: E402

NOW = datetime(2026, 7, 2, 12, 0, 0, tzinfo=timezone.utc)
GIT = {
    "branch": "test-branch",
    "head": "abc1234",
    "remote": "https://example.invalid/repo.git",
    "recent_agents": {"claude-fable-5[1m]": 4, "codex": 2},
}


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "status").mkdir(parents=True)
    (tmp_path / "docs" / "plans").mkdir(parents=True)
    (tmp_path / "task.md").write_text(
        "# Task\n## Active Program A\ntext\n## Bucket B\n", encoding="utf-8"
    )
    (tmp_path / "governance_state.json").write_text(
        json.dumps(
            {
                "active_vows": [1, 2, 3],
                "risk_posture": "stable",
                "soul_integral": 0.0,
                "baseline_drift": 0.01,
                "tension_history": [{"t": 0.1}],
                "last_updated": "2026-07-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "AXIOMS.json").write_text(
        json.dumps({"meta": {"not_for": ["consciousness-claim", "legal-proof"]}}),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "plans" / "x_decision_record_2026.md").write_text(
        "# d\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "status" / "status_freshness_latest.json").write_text(
        json.dumps({"generated_at": "2026-07-02T00:00:00Z", "summary": {"fresh": 40}}),
        encoding="utf-8",
    )
    return tmp_path


def test_card_aggregates_all_sections(tmp_path: Path) -> None:
    card = build_card(_repo(tmp_path), now=NOW, agent="yu", git_info=GIT)
    assert card["who"]["current_agent"] == "yu"
    assert card["who"]["recent_agents_from_git_trailers"]["codex"] == 2
    assert card["what"]["task_md_headings"] == ["Active Program A", "Bucket B"]
    assert card["what"]["decision_records"] == ["x_decision_record_2026.md"]
    assert card["when"]["evidence_freshness"] == {"fresh": 40}
    assert card["where"]["branch"] == "test-branch"
    assert card["observable_state"]["active_vows"] == 3
    assert card["stances"]["standing_refusals_meta_not_for"] == [
        "consciousness-claim",
        "legal-proof",
    ]


def test_claim_boundary_always_present(tmp_path: Path) -> None:
    card = build_card(_repo(tmp_path), now=NOW, git_info=GIT)
    assert "felt-self" in card["claim_boundary"]
    md = _render_markdown(card)
    assert "observable" in md and "非 feelings" in md


def test_missing_sources_degrade_honestly(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "docs" / "status").mkdir(parents=True)
    card = build_card(tmp_path, now=NOW, git_info=GIT)
    assert card["observable_state"]["note"] == "governance_state.json not available"
    assert card["when"]["note"] == "status_freshness_latest.json not available"
    assert card["things"]["note"] == "codebase_graph_latest.json not available"
    _render_markdown(card)  # must not raise on absent sources


def test_markdown_renders_agents_line(tmp_path: Path) -> None:
    md = _render_markdown(build_card(_repo(tmp_path), now=NOW, agent="yu", git_info=GIT))
    assert "claude-fable-5[1m]×4" in md and "codex×2" in md
    assert "`test-branch` @ `abc1234`" in md
