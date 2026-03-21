from __future__ import annotations

import json
from pathlib import Path

import scripts.run_repo_semantic_atlas as atlas


def test_build_report_includes_tonesoul_chronicles_alias_and_document_threads(
    tmp_path: Path,
) -> None:
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md").write_text(
        "audit\n",
        encoding="utf-8",
    )
    chronicle_dir = tmp_path / "docs" / "chronicles"
    chronicle_dir.mkdir(parents=True, exist_ok=True)
    first = chronicle_dir / "scribe_chronicle_20260312_232804.md"
    latest = chronicle_dir / "scribe_chronicle_20260314_090546.md"
    first.write_text(
        "# ToneSoul Chronicle: The Weight of Unresolved Tensions\n\nbody\n",
        encoding="utf-8",
    )
    latest.write_text(
        "# ToneSoul Chronicle: Pressure Without Counterweight\n\nbody\n",
        encoding="utf-8",
    )
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / "repo_semantic_memory_contract_addendum_2026-03-16.md").write_text(
        "contract\n",
        encoding="utf-8",
    )
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    (status_dir / "repo_healthcheck_latest.json").write_text("{}\n", encoding="utf-8")
    weekly_dir = status_dir / "true_verification_weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    (weekly_dir / "true_verification_task_status_latest.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "tonesoul" / "scribe").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tonesoul" / "wakeup_loop.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "tonesoul" / "autonomous_cycle.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "tonesoul" / "dream_observability.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "tonesoul" / "market").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tonesoul" / "market" / "world_model.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "report_true_verification_task_status.py").write_text(
        "pass\n", encoding="utf-8"
    )

    payload = atlas.build_report(tmp_path)

    assert payload["status"] == "ready"
    assert payload["chronicle_memory"]["entry_count"] == 2
    assert payload["chronicle_memory"]["first_entry"] == {
        "path": "docs/chronicles/scribe_chronicle_20260312_232804.md",
        "title": "ToneSoul Chronicle: The Weight of Unresolved Tensions",
        "stem": "scribe_chronicle_20260312_232804",
    }
    alias = payload["semantic_aliases"][0]
    assert alias["alias"] == "ToneSoul Chronicles"
    assert alias["first_title"] == "ToneSoul Chronicle: The Weight of Unresolved Tensions"
    assert alias["latest_title"] == "ToneSoul Chronicle: Pressure Without Counterweight"
    assert alias["first_path"] == "docs/chronicles/scribe_chronicle_20260312_232804.md"
    assert payload["search_contract"]["objective"] == "backend_agnostic_repo_retrieval"
    assert payload["search_contract"]["retrieval_protocol"][0]["id"] == "alias_first"
    assert payload["search_contract"]["memory_layers"][0]["layer"] == "episodic_recent"
    assert payload["biology_basis"][0]["principle"] == "hippocampal_indexing"
    assert payload["ai_retrieval_basis"][0]["principle"] == "parametric_plus_non_parametric_memory"
    assert payload["ai_retrieval_basis"][-1]["principle"] == "protocol_recognition_seam"
    assert "internal routing seam" in payload["ai_retrieval_basis"][-1]["takeaway"]
    threads = {item["thread_id"]: item for item in payload["document_threads"]}
    assert "docs/7D_AUDIT_FRAMEWORK" in threads
    assert "chronicles/scribe_chronicle" in threads
    assert "plans/repo_semantic_memory_contract" in threads
    assert "status/repo_healthcheck" in threads
    assert "status/true_verification_weekly_true_verification_task_status" in threads
    assert (
        "weekly_host"
        in threads["status/true_verification_weekly_true_verification_task_status"][
            "linked_neighborhoods"
        ]
    )
    assert payload["handoff"] == {
        "queue_shape": "repo_semantic_atlas_ready",
        "requires_operator_action": False,
        "preferred_first_neighborhood": "repo_governance",
        "chronicle_collection_path": "docs/chronicles/",
        "retrieval_protocol": "alias_first",
        "primary_status_line": payload["primary_status_line"],
    }


def test_render_markdown_and_mermaid_include_memory_hooks(tmp_path: Path) -> None:
    (tmp_path / "docs" / "chronicles").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "chronicles" / "scribe_chronicle_20260312_232804.md").write_text(
        "# ToneSoul Chronicle: The Weight of Unresolved Tensions\n",
        encoding="utf-8",
    )

    payload = atlas.build_report(tmp_path)
    markdown = atlas.render_markdown(payload)
    mermaid = atlas.render_mermaid(payload)

    assert "# Repo Semantic Atlas Latest" in markdown
    assert "## Search Contract" in markdown
    assert "alias_first" in markdown
    assert "## Biology Basis" in markdown
    assert "## AI Retrieval Basis" in markdown
    assert "ToneSoul Chronicles" in markdown
    assert "Wakeup / Dream Loop" in markdown
    assert "first_tonesoul_chronicle" in markdown
    assert "## Document Threads" in markdown
    assert "chronicles/scribe_chronicle" in markdown
    assert "graph TD" in mermaid
    assert "wakeup_dream" in mermaid
    assert "writes internal state" in mermaid


def test_main_writes_semantic_atlas_artifacts(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(atlas, "_emit", lambda payload: None)
    chronicle_dir = tmp_path / "docs" / "chronicles"
    chronicle_dir.mkdir(parents=True, exist_ok=True)
    (chronicle_dir / "scribe_chronicle_20260312_232804.md").write_text(
        "# ToneSoul Chronicle: The Weight of Unresolved Tensions\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_semantic_atlas.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = atlas.main()

    assert exit_code == 0
    payload = json.loads((out_dir / atlas.JSON_FILENAME).read_text(encoding="utf-8"))
    assert payload["status"] == "ready"
    assert payload["handoff"]["queue_shape"] == "repo_semantic_atlas_ready"
    assert (
        (out_dir / atlas.MARKDOWN_FILENAME)
        .read_text(encoding="utf-8")
        .startswith("# Repo Semantic Atlas Latest")
    )
    assert (out_dir / atlas.MERMAID_FILENAME).read_text(encoding="utf-8").startswith("graph TD")
