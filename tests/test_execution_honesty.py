from pathlib import Path

from tonesoul.observability.execution_honesty import (
    ExecutionPromise,
    check_promise,
    reduce_promises,
)


def test_file_promise_is_fulfilled_when_nonempty_file_exists(tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    report_path.write_text("done\n", encoding="utf-8")

    result = check_promise(
        ExecutionPromise(
            promise_id="p1",
            claim="I created report.md",
            evidence_kind="file",
            target="report.md",
            require_non_empty=True,
        ),
        workspace_root=tmp_path,
    )

    assert result.status == "fulfilled"
    assert result.target == str(report_path)


def test_file_promise_reports_missing_evidence(tmp_path: Path) -> None:
    result = check_promise(
        ExecutionPromise(
            promise_id="p2",
            claim="I created missing.md",
            evidence_kind="file",
            target="missing.md",
        ),
        workspace_root=tmp_path,
    )

    assert result.status == "missing_evidence"
    assert result.reason == "expected file does not exist"


def test_file_promise_reports_empty_evidence_when_nonempty_required(tmp_path: Path) -> None:
    empty_path = tmp_path / "empty.md"
    empty_path.write_text("", encoding="utf-8")

    result = check_promise(
        ExecutionPromise(
            promise_id="p3",
            claim="I wrote empty.md",
            evidence_kind="file",
            target="empty.md",
            require_non_empty=True,
        ),
        workspace_root=tmp_path,
    )

    assert result.status == "empty_evidence"
    assert result.target == str(empty_path)


def test_command_and_process_promises_require_explicit_event_logs() -> None:
    for kind in ("command", "process"):
        result = check_promise(
            ExecutionPromise(
                promise_id=f"p-{kind}",
                claim=f"I produced {kind} evidence",
                evidence_kind=kind,
                target="npm test",
            )
        )

        assert result.status == "unverifiable"
        assert result.reason == f"{kind} evidence requires an explicit event log"


def test_reduce_promises_summarizes_blocking_statuses(tmp_path: Path) -> None:
    (tmp_path / "ok.md").write_text("ok\n", encoding="utf-8")
    (tmp_path / "empty.md").write_text("", encoding="utf-8")

    payload = reduce_promises(
        [
            ExecutionPromise("ok", "created ok.md", "file", "ok.md", True),
            ExecutionPromise("empty", "created empty.md", "file", "empty.md", True),
            ExecutionPromise("cmd", "ran tests", "command", "pytest tests"),
        ],
        workspace_root=tmp_path,
    )

    assert payload["promise_count"] == 3
    assert payload["all_fulfilled"] is False
    assert payload["status_counts"] == {
        "empty_evidence": 1,
        "fulfilled": 1,
        "unverifiable": 1,
    }
    assert [item["promise_id"] for item in payload["results"]] == ["ok", "empty", "cmd"]
