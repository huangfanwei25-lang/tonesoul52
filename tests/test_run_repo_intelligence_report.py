from __future__ import annotations

import json
from pathlib import Path

import scripts.run_repo_intelligence_report as repo_intelligence


def test_build_report_surfaces_entrypoints_and_policy(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("tracked", encoding="utf-8")
    (tmp_path / "HANDOFF.md").write_text("tracked", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("tracked", encoding="utf-8")
    (tmp_path / "skills").mkdir()
    (tmp_path / ".agent").mkdir()
    (tmp_path / "docs" / "status").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "status" / "repo_healthcheck_latest.json").write_text(
        "{}\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "status" / "repo_semantic_atlas_latest.json").write_text(
        json.dumps(
            {
                "primary_status_line": (
                    "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 "
                    "chronicles=19 doc_threads=431 rules=8 graph_edges=7"
                ),
                "runtime_status_line": (
                    "entrypoints | atlas=repo_semantic_atlas_latest.json "
                    "repo=repo_healthcheck_latest.json "
                    "dream=dream_observability_latest.json "
                    "weekly=true_verification_task_status_latest.json "
                    "scribe=scribe_status_latest.json protocol=alias_first"
                ),
                "artifact_policy_status_line": (
                    "semantic_map=domain_level | aliases=source_declared "
                    "graph=passive_no_reparse protocol=backend_agnostic"
                ),
                "search_contract": {
                    "retrieval_protocol": [
                        {"id": "alias_first"},
                        {"id": "neighborhood_before_file"},
                        {"id": "status_surface_before_source"},
                    ]
                },
                "handoff": {
                    "queue_shape": "repo_semantic_atlas_ready",
                    "requires_operator_action": False,
                    "preferred_first_neighborhood": "repo_governance",
                    "chronicle_collection_path": "docs/chronicles/",
                    "retrieval_protocol": "alias_first",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "status" / "runtime_source_change_groups_latest.json").write_text(
        "{}\n", encoding="utf-8"
    )
    weekly_path = (
        tmp_path
        / "docs"
        / "status"
        / "true_verification_weekly"
        / "true_verification_task_status_latest.json"
    )
    weekly_path.parent.mkdir(parents=True, exist_ok=True)
    weekly_path.write_text("{}\n", encoding="utf-8")
    (tmp_path / "docs" / "status" / "agent_integrity_latest.json").write_text(
        "{}\n", encoding="utf-8"
    )

    payload = repo_intelligence.build_report(tmp_path)

    assert payload["status"] == "ready"
    assert payload["summary"] == {
        "protected_file_count": 5,
        "watched_directory_count": 3,
        "recommended_surface_count": 7,
        "available_surface_count": 5,
        "missing_surface_count": 2,
        "semantic_memory_connected": True,
    }
    assert payload["external_tool_policy"] == {
        "adoption_mode": "sidecar_only",
        "main_repo_install_allowed": False,
        "mirror_clone_required": True,
        "hook_registration_allowed": False,
        "protected_file_mutation_allowed": False,
    }
    assert payload["handoff"] == {
        "queue_shape": "repo_intelligence_ready",
        "requires_operator_action": False,
        "preferred_first_surface": "docs/status/repo_healthcheck_latest.json",
        "main_repo_install_allowed": False,
        "mirror_clone_required": True,
        "semantic_retrieval_protocol": "alias_first",
        "semantic_preferred_neighborhood": "repo_governance",
        "primary_status_line": payload["primary_status_line"],
    }
    assert payload["semantic_memory_handoff"] == {
        "path": "docs/status/repo_semantic_atlas_latest.json",
        "retrieval_protocol": "alias_first",
        "preferred_first_neighborhood": "repo_governance",
        "chronicle_collection_path": "docs/chronicles/",
        "retrieval_rule_ids": [
            "alias_first",
            "neighborhood_before_file",
            "status_surface_before_source",
        ],
        "primary_status_line": (
            "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 "
            "chronicles=19 doc_threads=431 rules=8 graph_edges=7"
        ),
        "runtime_status_line": (
            "entrypoints | atlas=repo_semantic_atlas_latest.json "
            "repo=repo_healthcheck_latest.json "
            "dream=dream_observability_latest.json "
            "weekly=true_verification_task_status_latest.json "
            "scribe=scribe_status_latest.json protocol=alias_first"
        ),
        "artifact_policy_status_line": (
            "semantic_map=domain_level | aliases=source_declared "
            "graph=passive_no_reparse protocol=backend_agnostic"
        ),
    }
    assert payload["recommended_surfaces"][0]["name"] == "repo_healthcheck"
    assert payload["recommended_surfaces"][0]["available"] is True
    assert payload["recommended_surfaces"][1]["name"] == "repo_semantic_atlas"
    assert payload["recommended_surfaces"][1]["available"] is True
    assert payload["recommended_surfaces"][2]["name"] == "agent_integrity"
    assert payload["recommended_surfaces"][2]["available"] is True
    assert payload["recommended_surfaces"][-1]["name"] == "scribe_status"
    assert payload["recommended_surfaces"][-1]["available"] is False
    markdown = repo_intelligence.render_markdown(payload)
    assert "# Repo Intelligence Latest" in markdown
    assert "sidecar_only" in markdown
    assert "repo_healthcheck_latest.json" in markdown
    assert "repo_semantic_atlas_latest.json" in markdown
    assert "agent_integrity_latest.json" in markdown
    assert "## Semantic Retrieval Protocol" in markdown
    assert "alias_first" in markdown
    assert "repo_governance" in markdown


def test_main_writes_repo_intelligence_artifacts(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(repo_intelligence, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_intelligence_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = repo_intelligence.main()

    assert exit_code == 0
    payload = json.loads((out_dir / repo_intelligence.JSON_FILENAME).read_text(encoding="utf-8"))
    assert payload["status"] == "ready"
    assert payload["handoff"]["queue_shape"] == "repo_intelligence_ready"
    markdown = (out_dir / repo_intelligence.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "Repo Intelligence Latest" in markdown
