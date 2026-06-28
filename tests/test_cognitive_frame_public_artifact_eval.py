from __future__ import annotations

from pathlib import Path

from tools.probe.cognitive_frame_public_artifact_eval import (
    FIXTURE_PATH,
    REPO_ROOT,
    evaluate_cases,
    load_cases,
    render_report,
)


def test_public_artifact_frames_are_valid_and_public() -> None:
    rows = evaluate_cases(load_cases())

    assert rows
    assert all(row.ok for row in rows)
    assert all(row.actual_accepted for row in rows)
    assert sum(row.artifact_count for row in rows) >= len(rows)


def test_fixture_evidence_refs_point_to_existing_public_files() -> None:
    rows = evaluate_cases(load_cases(FIXTURE_PATH))

    for row in rows:
        assert row.missing_refs == ()
        assert row.forbidden_refs == ()


def test_public_artifact_eval_report_surfaces_scope_boundary() -> None:
    rows = evaluate_cases(load_cases())
    report = render_report(rows)

    assert "Cognitive Frame Public Artifact Eval" in report
    assert "semantic evidence sufficiency" in report
    assert "externalized_cognition_anchor" in report
    assert "failures: **0**" in report


def test_fixture_path_is_inside_public_repo() -> None:
    fixture = Path(FIXTURE_PATH).resolve()
    repo = Path(REPO_ROOT).resolve()

    assert fixture.is_relative_to(repo)
    assert "tests" in fixture.parts
