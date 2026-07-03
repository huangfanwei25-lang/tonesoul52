from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.trace_dataset.extract import (
    GIT_LOG_FORMAT,
    SCHEMA_KEYS,
    extract_commits,
    extract_events,
    extract_judgments,
)


def test_extract_events_from_fixture_has_schema_fields(tmp_path: Path) -> None:
    events_path = tmp_path / "events.json"
    events_path.write_text(
        json.dumps(
            [
                {
                    "lane": "self-check",
                    "claim": "這是一個 claim",
                    "evidence_at_claim": "E2",
                    "held": False,
                    "caught_by": "codex",
                    "correction": "修正",
                    "outcome": "refuted",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
        newline="\n",
    )

    traces = extract_events(json.loads(events_path.read_text(encoding="utf-8")))

    assert len(traces) == 1
    assert set(traces[0]) == set(SCHEMA_KEYS)
    assert traces[0]["trace_type"] == "counter_evidence"
    assert traces[0]["evidence_grade"] == "E2"
    assert traces[0]["label_provenance"] == "incident"


def test_extract_events_missing_judgment_fields_stay_null(tmp_path: Path) -> None:
    events_path = tmp_path / "events.json"
    events_path.write_text(
        json.dumps(
            [
                {
                    "lane": "co-observer",
                    "claim": "只有中文",
                    "evidence_at_claim": "—",
                    "held": False,
                    "caught_by": "人",
                    "correction": "不補 outcome",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
        newline="\n",
    )

    trace = extract_events(json.loads(events_path.read_text(encoding="utf-8")))[0]

    assert trace["outcome"] is None
    assert trace["evidence_grade"] == "unlabeled"
    assert trace["register"] == "mixed"


def test_extract_commits_from_fake_git_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "agent@example.test")
    _git(repo, "config", "user.name", "Agent")

    (repo / "a.txt").write_text("a\n", encoding="utf-8", newline="\n")
    _git(repo, "add", "a.txt")
    _git(
        repo,
        "commit",
        "-m",
        "unsigned subject",
    )

    (repo / "a.txt").write_text("a\nb\n", encoding="utf-8", newline="\n")
    _git(repo, "add", "a.txt")
    _git(
        repo,
        "commit",
        "-m",
        "signed subject",
        "-m",
        "Agent: codex\nTrace-Topic: trace dataset implementation",
    )

    git_log = _git(repo, "log", "--no-merges", f"--format={GIT_LOG_FORMAT}")
    traces = extract_commits(git_log)

    assert len(traces) == 1
    assert set(traces[0]) == set(SCHEMA_KEYS)
    assert traces[0]["trace_type"] == "signed_commitment"
    assert traces[0]["actors"] == {"claimant": "codex", "challenger": None}
    assert traces[0]["claim_or_action"] == "trace dataset implementation"
    assert traces[0]["source_ref"]


def test_extract_judgments_from_fixture(tmp_path: Path) -> None:
    judgment_path = tmp_path / "judgment.md"
    judgment_path.write_text(
        "# 誠實判斷記錄 — 測試\n\n"
        "> 2026-07-02,honest-judgment 協議——correlated-blind-spot 標記。\n\n"
        "**判決:REFINE** — 留開源。\n",
        encoding="utf-8",
        newline="\n",
    )

    traces = extract_judgments(judgment_path.read_text(encoding="utf-8"))

    assert len(traces) == 1
    assert set(traces[0]) == set(SCHEMA_KEYS)
    assert traces[0]["trace_type"] == "declared_stance"
    assert traces[0]["occurred_at"] == "2026-07-02"
    assert traces[0]["outcome"] == "REFINE"
    assert "correlated-blind-spot" in traces[0]["claim_or_action"]


def test_extractors_are_deterministic(tmp_path: Path) -> None:
    events = [
        {
            "lane": "self-check",
            "claim": "deterministic",
            "evidence_at_claim": "E1",
            "held": True,
            "caught_by": "test",
            "correction": "—",
        }
    ]
    judgment = "# Title\n\n> 2026-07-02\n\n**判決:DECLARE_STANCE**\n"
    git_log = "abc123\0" "2026-07-04T00:00:00+00:00\0" "codex\0" "deterministic topic\0" "subject\n"

    first = [*extract_events(events), *extract_commits(git_log), *extract_judgments(judgment)]
    second = [*extract_events(events), *extract_commits(git_log), *extract_judgments(judgment)]

    assert first == second
    assert all(trace["id"] for trace in first)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout
