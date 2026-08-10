from __future__ import annotations

import json
from pathlib import Path

import scripts.run_changed_surface_checks as runner


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _check_names(payload: dict[str, object]) -> list[str]:
    return [str(check["name"]) for check in payload["checks"]]  # type: ignore[index]


def _assert_receipt_matches_schema_profile(
    payload: dict[str, object], schema: dict[str, object]
) -> None:
    """Check the executable v0.1 profile without adding a JSON Schema dependency."""
    for field in schema["required"]:  # type: ignore[index]
        assert field in payload

    properties = schema["properties"]  # type: ignore[index]
    assert isinstance(payload["plan_ok"], bool)
    assert isinstance(payload["overall_ok"], bool)
    assert isinstance(payload["changed_paths"], list)
    assert isinstance(payload["checks"], list)
    assert isinstance(payload["metrics"], dict)
    assert isinstance(payload["issues"], list)

    routing = payload["routing"]
    assert isinstance(routing, dict)
    routing_schema = properties["routing"]  # type: ignore[index]
    for field in routing_schema["required"]:  # type: ignore[index]
        assert field in routing

    routing_properties = routing_schema["properties"]  # type: ignore[index]
    assert routing["protocol_version"] == routing_properties["protocol_version"]["const"]
    assert routing["adoption_status"] == routing_properties["adoption_status"]["const"]
    for field in ("derived_level", "effective_level", "external_effect_status"):
        assert routing[field] in routing_properties[field]["enum"]
    for field in ("matched_rules", "missing_external_requirements", "required_checks"):
        assert isinstance(routing[field], list)
        assert all(isinstance(value, str) for value in routing[field])
    for field in ("external_effect", "publish_ready"):
        assert isinstance(routing[field], bool)
    for field in ("external_target", "grant_ref", "owner_review_ref"):
        assert routing[field] is None or isinstance(routing[field], str)


def test_documentation_change_does_not_plan_full_pytest(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "guide.md", "# Guide\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["docs/guide.md"],
        python_executable="python",
    )

    assert payload["routing"]["derived_level"] == "documentation"
    assert payload["routing"]["external_effect_status"] == "not_assessed"
    assert "python_full_regression" not in _check_names(payload)
    assert _check_names(payload) == [
        "protected_paths",
        "docs_consistency",
        "doc_links",
        "diff_check",
    ]


def test_workflow_change_is_core_not_documentation(tmp_path: Path) -> None:
    _write(tmp_path / ".github" / "workflows" / "ci.yml", "name: CI\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=[".github/workflows/ci.yml"],
        python_executable="python",
    )

    assert payload["routing"]["derived_level"] == "core_boundary"
    assert "python_full_regression" in _check_names(payload)


def test_unknown_path_defaults_to_local_code(tmp_path: Path) -> None:
    _write(tmp_path / "tooling" / "custom.asset", "opaque\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["tooling/custom.asset"],
        python_executable="python",
    )

    assert payload["routing"]["derived_level"] == "local_code"
    assert "smoke_tests" in _check_names(payload)
    assert "python_full_regression" not in _check_names(payload)


def test_mixed_change_uses_highest_derived_level(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "guide.md", "# Guide\n")
    _write(tmp_path / "tonesoul" / "governance" / "policy.py", "POLICY = True\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["docs/guide.md", "tonesoul/governance/policy.py"],
        python_executable="python",
    )

    assert payload["routing"]["derived_level"] == "core_boundary"
    assert "core_prefix:tonesoul/governance/" in payload["routing"]["matched_rules"]


def test_external_action_requires_scoped_inputs_and_preflights(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "release.md", "# Release\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["docs/release.md"],
        action="push",
        python_executable="python",
    )

    assert payload["routing"]["derived_level"] == "documentation"
    assert payload["routing"]["external_effect_status"] == "owner_gate"
    assert payload["routing"]["publish_ready"] is False
    assert set(payload["routing"]["missing_external_requirements"]) == {
        "external_target",
        "target_allowlist",
        "grant_ref",
        "owner_review_ref",
    }
    assert "pii_secret_scan" in _check_names(payload)
    assert "publish_push_preflight" in _check_names(payload)
    assert "python_full_regression" not in _check_names(payload)


def test_external_action_with_scoped_inputs_is_preflight_pending(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "release.md", "# Release\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["docs/release.md"],
        action="push",
        external_target="private:backup/working-tree",
        allowed_targets=("private:backup/working-tree",),
        grant_ref="owner-message:current-task",
        owner_review_ref="owner-message:current-review",
        python_executable="python",
    )

    assert payload["routing"]["external_effect_status"] == "preflight_pending"
    assert payload["routing"]["missing_external_requirements"] == []
    assert payload["routing"]["publish_ready"] is False


def test_external_action_missing_scope_never_executes_checks(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "release.md", "# Release\n")
    calls: list[str] = []

    def fake_runner(name: str, _command: list[str], _cwd: Path) -> dict[str, object]:
        calls.append(name)
        return {"name": name, "status": "pass", "ok": True, "exit_code": 0}

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["docs/release.md"],
        action="push",
        execute=True,
        runner=fake_runner,
        python_executable="python",
    )

    assert calls == []
    assert payload["checks_ok"] is None
    assert payload["overall_ok"] is False


def test_requested_level_can_escalate_but_not_downgrade(tmp_path: Path) -> None:
    _write(tmp_path / "tonesoul" / "memory" / "store.py", "STORE = True\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["tonesoul/memory/store.py"],
        requested_level="documentation",
        python_executable="python",
    )

    assert payload["plan_ok"] is False
    assert payload["routing"]["derived_level"] == "core_boundary"
    assert "requested_level_would_downgrade" in payload["issues"]


def test_empty_change_is_not_publish_ready(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        runner.protected_paths,
        "collect_changed_paths",
        lambda **_kwargs: {"mode": "explicit", "exit_code": 0, "paths": []},
    )
    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=[],
        action="push",
        external_target="origin",
        allowed_targets=("origin",),
        grant_ref="owner-message:current-task",
        owner_review_ref="owner-message:current-review",
        python_executable="python",
    )

    assert payload["plan_ok"] is False
    assert payload["routing"]["publish_ready"] is False
    assert "no_changed_paths" in payload["issues"]


def test_preregistered_cases_match_runtime_and_receipt_schema(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    fixture = json.loads(
        (root / "tests/fixtures/proportional_validation_v01_cases.json").read_text(encoding="utf-8")
    )
    schema = json.loads(
        (root / "spec/verification/proportional_validation_receipt_v0_1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(fixture["cases"]) == 12
    for case in fixture["cases"]:
        for path in case["paths"]:
            _write(tmp_path / path, "fixture\n")
        kwargs: dict[str, object] = {}
        if case["external"]:
            kwargs = {
                "action": case["action"],
                "external_target": f"fixture:{case['case_id']}",
                "allowed_targets": (f"fixture:{case['case_id']}",),
                "grant_ref": "owner-message:fixture",
                "owner_review_ref": "owner-message:fixture-review",
            }
        payload = runner.build_report(
            repo_root=tmp_path,
            changed_files=case["paths"],
            python_executable="python",
            **kwargs,
        )
        assert payload["routing"]["derived_level"] == case["expected_level"]
        assert payload["routing"]["external_effect"] is case["external"]
        _assert_receipt_matches_schema_profile(payload, schema)


def test_external_preflight_receives_scoped_grant_and_owner_review(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "release.md", "# Release\n")
    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["docs/release.md"],
        action="push",
        external_target="public:owner/repo:branch:feature",
        allowed_targets=("public:owner/repo:branch:feature",),
        grant_ref="owner-message:scoped-grant",
        owner_review_ref="owner-message:reviewed-draft-pr",
        python_executable="python",
    )

    preflight = next(
        check for check in payload["checks"] if check["name"] == "publish_push_preflight"
    )
    assert "--grant-ref owner-message:scoped-grant" in preflight["command"]
    assert "--owner-review-ref owner-message:reviewed-draft-pr" in preflight["command"]


def test_external_action_without_owner_review_never_becomes_publish_ready(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "release.md", "# Release\n")
    calls: list[str] = []

    def fake_runner(name: str, _command: list[str], _cwd: Path) -> dict[str, object]:
        calls.append(name)
        return {"name": name, "status": "pass", "ok": True, "exit_code": 0}

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["docs/release.md"],
        action="push",
        external_target="public:owner/repo:branch:feature",
        allowed_targets=("public:owner/repo:branch:feature",),
        grant_ref="owner-message:scoped-grant",
        execute=True,
        runner=fake_runner,
        python_executable="python",
    )

    assert calls == []
    assert payload["routing"]["external_effect_status"] == "owner_gate"
    assert payload["routing"]["publish_ready"] is False
    assert "owner_review_ref" in payload["routing"]["missing_external_requirements"]


def test_targeted_test_overflow_escalates_instead_of_falling_back_to_smoke(
    monkeypatch, tmp_path: Path
) -> None:
    _write(tmp_path / "tools" / "wide.py", "VALUE = 1\n")
    monkeypatch.setattr(
        runner,
        "infer_targeted_tests",
        lambda *_args, **_kwargs: (
            [],
            ["targeted pytest candidate count exceeded limit; using full regression instead"],
        ),
    )

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["tools/wide.py"],
        python_executable="python",
    )

    assert payload["routing"]["derived_level"] == "local_code"
    assert payload["routing"]["effective_level"] == "core_boundary"
    assert "python_full_regression" in _check_names(payload)
    assert "smoke_tests" not in _check_names(payload)


def test_rename_collection_keeps_source_and_destination_for_risk(tmp_path: Path) -> None:
    changed = tmp_path / "changed.txt"
    changed.write_text("R100\tdocs/old.md\t.github/workflows/ci.yml\n", encoding="utf-8")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_file_list=changed,
        python_executable="python",
    )

    assert payload["changed_paths"] == ["docs/old.md", ".github/workflows/ci.yml"]
    assert payload["routing"]["derived_level"] == "core_boundary"


def test_shadow_full_emits_comparable_false_negative_observation(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "guide.md", "# Guide\n")

    def fake_runner(name: str, _command: list[str], _cwd: Path) -> dict[str, object]:
        legacy = name == "legacy_full_regression"
        return {
            "name": name,
            "status": "fail" if legacy else "pass",
            "ok": not legacy,
            "exit_code": 1 if legacy else 0,
            "duration_seconds": 100.0 if legacy else 2.0,
            "stdout_tail": "100 passed" if legacy else "10 passed",
            "stderr_tail": "",
        }

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["docs/guide.md"],
        shadow_full=True,
        pilot_case_id="actual-doc-01",
        execute=True,
        runner=fake_runner,
        python_executable="python",
    )

    observation = payload["pilot_observation"]
    assert observation["case_id"] == "actual-doc-01"
    assert observation["routed"]["ok"] is True
    assert observation["legacy"]["ok"] is False
    assert observation["false_negative"] is True
    assert observation["routed"]["duration_seconds"] == 8.0
    assert observation["legacy"]["duration_seconds"] == 100.0


def test_build_report_plans_surface_specific_checks(tmp_path: Path) -> None:
    _write(tmp_path / "scripts" / "run_changed_surface_checks.py", "print('ok')\n")
    _write(
        tmp_path / "tests" / "test_run_changed_surface_checks.py", "def test_smoke():\n    pass\n"
    )
    _write(
        tmp_path / "tonesoul" / "memory" / "crystallizer.py",
        "class MemoryCrystallizer:\n    pass\n",
    )
    _write(tmp_path / "tests" / "test_memory_crystallizer.py", "def test_smoke():\n    pass\n")
    _write(tmp_path / "docs" / "README.md", "# Docs\n")
    _write(tmp_path / "apps" / "web" / "src" / "lib" / "soulEngine.ts", "export const x = 1;\n")

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=[
            "scripts/run_changed_surface_checks.py",
            "tonesoul/memory/crystallizer.py",
            "docs/README.md",
            "apps/web/src/lib/soulEngine.ts",
        ],
        python_executable="python",
    )

    surface_ids = [surface["id"] for surface in payload["surfaces"]]
    check_names = [check["name"] for check in payload["checks"]]

    assert payload["plan_ok"] is True
    assert payload["checks_ok"] is None
    assert "python_runtime" in surface_ids
    assert "core_runtime" in surface_ids
    assert "docs_governance" in surface_ids
    assert "web_surface" in surface_ids
    assert check_names == [
        "protected_paths",
        "python_lint_changed",
        "layer_boundaries",
        "docs_consistency",
        "doc_links",
        "diff_check",
        "targeted_pytest",
        "web_lint",
        "web_test",
        "python_lint_full",
        "boundary_tests",
        "core_tests",
        "python_full_regression",
        "pii_secret_scan",
    ]
    assert payload["metrics"]["planned_check_count"] == 14
    assert any(
        "tests/test_memory_crystallizer.py" in check["command"]
        for check in payload["checks"]
        if check["name"] == "targeted_pytest"
    )
    boundary = next(check for check in payload["checks"] if check["name"] == "boundary_tests")
    assert "scripts/run_test_tier.py --tier blocking" in boundary["command"]


def test_build_report_executes_checks_with_runner(tmp_path: Path) -> None:
    _write(tmp_path / "scripts" / "verify_protected_paths.py", "print('ok')\n")
    _write(tmp_path / "scripts" / "run_changed_surface_checks.py", "print('ok')\n")
    _write(
        tmp_path / "tests" / "test_run_changed_surface_checks.py", "def test_smoke():\n    pass\n"
    )

    def fake_runner(name: str, command: list[str], cwd: Path) -> dict[str, object]:
        assert cwd == tmp_path
        return {
            "name": name,
            "status": "fail" if name == "targeted_pytest" else "pass",
            "ok": name != "targeted_pytest",
            "exit_code": 1 if name == "targeted_pytest" else 0,
            "duration_seconds": 0.01,
            "stdout_tail": runner._display_command(command),
            "stderr_tail": "",
        }

    payload = runner.build_report(
        repo_root=tmp_path,
        changed_files=["scripts/run_changed_surface_checks.py"],
        execute=True,
        runner=fake_runner,
        python_executable="python",
    )

    assert payload["execution_mode"] == "execute"
    assert payload["checks_ok"] is False
    assert payload["overall_ok"] is False
    assert payload["metrics"]["executed_check_count"] == 10
    assert payload["metrics"]["failed_check_count"] == 1
    assert any(check["status"] == "fail" for check in payload["checks"])


def test_main_writes_json_and_markdown(monkeypatch, tmp_path: Path) -> None:
    out_dir = tmp_path / "status"
    _write(tmp_path / "scripts" / "run_changed_surface_checks.py", "print('ok')\n")
    _write(
        tmp_path / "tests" / "test_run_changed_surface_checks.py", "def test_smoke():\n    pass\n"
    )

    monkeypatch.setattr(
        runner,
        "build_parser",
        lambda: type(
            "Parser",
            (),
            {
                "parse_args": staticmethod(
                    lambda _argv=None: type(
                        "Args",
                        (),
                        {
                            "repo_root": str(tmp_path),
                            "out_dir": str(out_dir.relative_to(tmp_path)),
                            "changed_file": ["scripts/run_changed_surface_checks.py"],
                            "changed_file_list": None,
                            "staged": False,
                            "base_ref": None,
                            "allow_path": [],
                            "execute": False,
                            "strict": False,
                        },
                    )()
                )
            },
        )(),
    )

    exit_code = runner.main([])
    payload = json.loads((out_dir / runner.JSON_FILENAME).read_text(encoding="utf-8"))
    markdown = (out_dir / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["metrics"]["planned_check_count"] == 10
    assert "# Changed Surface Checks Latest" in markdown
    assert "targeted_pytest" in markdown
