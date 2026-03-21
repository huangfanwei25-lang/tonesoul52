import sys
from pathlib import Path

import yaml

from tonesoul import constraint_stack as constraint_mod


def test_merge_constraints_handles_present_and_missing_lists():
    assert constraint_mod._merge_constraints({"constraints": ["c1"], "assumptions": ["a1"]}) == [
        "Context constraints:",
        "- c1",
        "",
        "Assumptions:",
        "- a1",
    ]
    assert constraint_mod._merge_constraints({"constraints": "bad", "assumptions": None}) == [
        "Context constraints:",
        "",
        "Assumptions:",
    ]


def test_format_action_set_includes_policy_and_rationale():
    lines = constraint_mod._format_action_set(
        {"time_island": {"kairos": {"decision_mode": "cautious"}}}
    )

    assert lines == [
        "## Action Set",
        "- Decision mode: cautious",
        "- Allowed actions:",
        "  - verify",
        "  - inquire",
        "- Strict mode policy:",
        "  - cautious: verify, inquire",
        "  - lockdown: verify, cite, inquire",
        "- Rationale: Minimal action set to reduce risk under strict modes.",
    ]


def test_format_mercy_objective_uses_explicit_objective():
    lines = constraint_mod._format_mercy_objective(
        {},
        objective={
            "decision_mode": "normal",
            "score": 0.5,
            "weights": {"care": 0.2},
            "signals": {"care": 0.3},
            "rationale": "balance caution and care",
        },
    )

    assert lines == [
        "## Mercy Objective",
        "- Decision mode: normal",
        "- Score: 0.5",
        "- Weights:",
        "  - care: 0.200",
        "- Signals:",
        "  - care: 0.30",
        "- Rationale: balance caution and care",
    ]


def test_build_constraints_doc_includes_template_metadata_and_sections(monkeypatch):
    monkeypatch.setattr(constraint_mod, "utc_now", lambda: "2026-03-20T00:00:00Z")
    monkeypatch.setattr(constraint_mod, "stable_hash", lambda value: "hash123")

    doc = constraint_mod.build_constraints_doc(
        {
            "constraints": ["c1"],
            "assumptions": ["a1"],
            "time_island": {"kairos": {"decision_mode": "normal"}},
        },
        "Template text",
        frame_plan_path="frame_plan.json",
        mercy_objective={
            "decision_mode": "normal",
            "score": 0.4,
            "weights": {"care": 0.2},
            "signals": {"care": 0.1},
            "rationale": "steady",
        },
    )

    assert "# Constraint Stack" in doc
    assert "- Generated at: 2026-03-20T00:00:00Z" in doc
    assert "- Context hash: hash123" in doc
    assert "- Frame plan: frame_plan.json" in doc
    assert "## Template" in doc
    assert "Template text" in doc
    assert "## Action Set" in doc
    assert "## Mercy Objective" in doc


def test_resolve_output_and_main_write_constraints_file(tmp_path, monkeypatch):
    context_path = tmp_path / "context.yaml"
    template_path = tmp_path / "template.md"
    output_path = tmp_path / "constraints.md"
    context_path.write_text(
        yaml.safe_dump(
            {
                "constraints": ["c1"],
                "assumptions": ["a1"],
                "time_island": {"kairos": {"decision_mode": "normal"}},
            }
        ),
        encoding="utf-8",
    )
    template_path.write_text("Template body", encoding="utf-8")

    monkeypatch.setattr(constraint_mod, "utc_now", lambda: "2026-03-20T00:00:00Z")
    monkeypatch.setattr(constraint_mod, "stable_hash", lambda value: "hash123")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "constraint_stack",
            "--context",
            str(context_path),
            "--template",
            str(template_path),
            "--output",
            str(output_path),
        ],
    )

    result = constraint_mod.main()
    saved = output_path.read_text(encoding="utf-8")

    assert Path(result["constraints"]) == output_path.resolve()
    assert constraint_mod._resolve_output(None, str(context_path)) == str(
        tmp_path / "constraints.md"
    )
    assert saved.startswith("# Constraint Stack")
    assert "Template body" in saved
