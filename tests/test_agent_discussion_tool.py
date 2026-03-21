from pathlib import Path

import tools.agent_discussion_tool as discussion_tool
from memory.agent_discussion import LESSONS_TEMPLATE_VERSION, load_entries


def test_parser_accepts_append_lessons_arguments():
    parser = discussion_tool._build_parser()
    args = parser.parse_args(
        [
            "append-lessons",
            "--author",
            "codex",
            "--topic",
            "repo-convergence-progress-2026-02-10",
            "--summary",
            "clarified missed points",
            "--missed",
            "a",
            "--missed",
            "b",
            "--correction",
            "c",
            "--guardrail",
            "d",
        ]
    )

    assert args.command == "append-lessons"
    assert args.author == "codex"
    assert args.missed == ["a", "b"]
    assert args.correction == ["c"]
    assert args.guardrail == ["d"]


def test_cmd_append_lessons_writes_standard_message(tmp_path: Path):
    raw = tmp_path / "agent_discussion.jsonl"
    curated = tmp_path / "agent_discussion_curated.jsonl"

    code = discussion_tool._cmd_append_lessons(
        path=raw,
        curated_path=curated,
        author="codex",
        topic="repo-convergence-progress-2026-02-10",
        status="done",
        summary="clarified missed points",
        missed=["overlooked soft-fail risk"],
        cause=["did not separate gate levels"],
        correction=["report blocking and soft-fail separately"],
        guardrail=["precheck /api/health before live smoke"],
        evidence=["run_7d_isolated.py --web-script dev"],
        signature="signed_by=codex(gpt-5)",
    )

    assert code == 0
    rows = load_entries(path=raw)
    assert len(rows) == 1
    message = rows[0]["message"]
    assert message.startswith(f"[{LESSONS_TEMPLATE_VERSION}]")
    assert "missed:\n- overlooked soft-fail risk" in message
    assert "signature: signed_by=codex(gpt-5)" in message
    curated_rows = load_entries(path=curated)
    assert len(curated_rows) == 1
    assert curated_rows[0]["topic"] == "repo-convergence-progress-2026-02-10"


def test_cmd_append_lessons_rejects_missing_corrections(tmp_path: Path, capsys):
    raw = tmp_path / "agent_discussion.jsonl"
    curated = tmp_path / "agent_discussion_curated.jsonl"

    code = discussion_tool._cmd_append_lessons(
        path=raw,
        curated_path=curated,
        author="codex",
        topic="repo-convergence-progress-2026-02-10",
        status="done",
        summary="clarified missed points",
        missed=["overlooked soft-fail risk"],
        cause=[],
        correction=[],
        guardrail=[],
        evidence=[],
        signature="",
    )

    assert code == 1
    out = capsys.readouterr().out
    assert "corrections" in out
