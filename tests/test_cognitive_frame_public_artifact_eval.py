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
    assert all(row.actual_accepted == row.expected_accepted for row in rows)
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


def test_fixture_includes_a_rejected_negative_case() -> None:
    # The committed fixture must exercise the reject path, not only happy-path acceptance, so a
    # regression that wrongly accepts an unsupported factual claim is caught by the eval itself.
    rows = evaluate_cases(load_cases())

    rejected = [row for row in rows if not row.expected_accepted]
    assert rejected, "fixture must commit at least one expected-reject case"
    for row in rejected:
        assert row.actual_accepted is False
        assert "missing_evidence_refs" in row.issue_codes


def test_eval_flags_forbidden_and_missing_evidence_refs() -> None:
    # Exercise the ref guards directly (kept out of the committed fixture so the fixture stays
    # all-public): a synthetic case pointing at a private-memory path and a missing file must be
    # flagged and reported as not-ok.
    case = {
        "id": "synthetic_guard_check",
        "expected_accepted": True,
        "artifact_paths": [
            "memory/self_journal.jsonl",
            "docs/this_file_does_not_exist_zzz.md",
        ],
        "frame": {
            "question": "Synthetic frame exercising the public-artifact ref guards.",
            "known_facts": [
                {
                    "text": "A fact pointing at a private path and a missing file.",
                    "evidence_refs": [
                        "file:memory/self_journal.jsonl",
                        "file:docs/this_file_does_not_exist_zzz.md",
                    ],
                    "confidence": "observed",
                }
            ],
        },
    }

    [row] = evaluate_cases([case])

    assert "memory/self_journal.jsonl" in row.forbidden_refs
    assert "docs/this_file_does_not_exist_zzz.md" in row.missing_refs
    assert row.ok is False
