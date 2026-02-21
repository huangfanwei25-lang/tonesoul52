from pathlib import Path

import scripts.verify_dual_track_boundary as boundary


def test_match_block_rule_supports_exact_file_and_prefix() -> None:
    blocked_prefixes = ["memory/handoff/", "tonesoul_evolution/"]
    blocked_files = ["memory/agent_discussion.jsonl"]

    assert boundary._match_block_rule(
        "memory/agent_discussion.jsonl",
        blocked_prefixes=blocked_prefixes,
        blocked_files=blocked_files,
    ) == {"rule_type": "file", "rule": "memory/agent_discussion.jsonl"}

    assert boundary._match_block_rule(
        "tonesoul_evolution/adversarial/prompts.py",
        blocked_prefixes=blocked_prefixes,
        blocked_files=blocked_files,
    ) == {"rule_type": "prefix", "rule": "tonesoul_evolution/"}

    assert (
        boundary._match_block_rule(
            "tonesoul/council/runtime.py",
            blocked_prefixes=blocked_prefixes,
            blocked_files=blocked_files,
        )
        is None
    )


def test_collect_changed_paths_accepts_explicit_list() -> None:
    payload = boundary._collect_changed_paths(
        repo_root=Path("."),
        staged=False,
        base_ref=None,
        changed_file_list=None,
        changed_files=["memory/handoff/a.md", "tonesoul/council/runtime.py"],
    )

    assert payload["ok"] is True
    assert payload["mode"] == "explicit"
    assert payload["paths"] == ["memory/handoff/a.md", "tonesoul/council/runtime.py"]


def test_collect_changed_paths_supports_file_list(tmp_path: Path) -> None:
    changed_file_list = tmp_path / "changed.txt"
    changed_file_list.write_text(
        "memory/handoff/a.md\n\n tonesoul/council/runtime.py \n", encoding="utf-8"
    )

    payload = boundary._collect_changed_paths(
        repo_root=tmp_path,
        staged=False,
        base_ref=None,
        changed_file_list=changed_file_list,
        changed_files=[],
    )

    assert payload["ok"] is True
    assert payload["mode"] == "file_list"
    assert payload["paths"] == ["memory/handoff/a.md", "tonesoul/council/runtime.py"]


def test_build_report_passes_when_no_blocked_paths() -> None:
    collection = {
        "ok": True,
        "mode": "explicit",
        "paths": ["tonesoul/council/runtime.py", "tests/test_council.py"],
    }
    report = boundary.build_report(
        repo_root=Path("."),
        collection=collection,
        blocked_prefixes=["memory/handoff/"],
        blocked_files=["memory/agent_discussion.jsonl"],
        allow_private_paths=False,
    )

    assert report["overall_ok"] is True
    assert report["metrics"]["violation_count"] == 0
    assert report["issues"] == []


def test_build_report_fails_when_blocked_paths_detected() -> None:
    collection = {
        "ok": True,
        "mode": "explicit",
        "paths": ["memory/handoff/codex_prompt.md", "tonesoul/council/runtime.py"],
    }
    report = boundary.build_report(
        repo_root=Path("."),
        collection=collection,
        blocked_prefixes=["memory/handoff/"],
        blocked_files=["memory/agent_discussion.jsonl"],
        allow_private_paths=False,
    )

    assert report["overall_ok"] is False
    assert report["metrics"]["violation_count"] == 1
    assert report["violations"][0]["path"] == "memory/handoff/codex_prompt.md"
    assert any("violate dual-track boundary policy" in issue for issue in report["issues"])


def test_build_report_allows_break_glass_but_emits_warning() -> None:
    collection = {
        "ok": True,
        "mode": "explicit",
        "paths": ["memory/agent_discussion.jsonl"],
    }
    report = boundary.build_report(
        repo_root=Path("."),
        collection=collection,
        blocked_prefixes=["memory/handoff/"],
        blocked_files=["memory/agent_discussion.jsonl"],
        allow_private_paths=True,
    )

    assert report["overall_ok"] is True
    assert report["metrics"]["violation_count"] == 1
    assert report["issues"] == []
    assert any("break-glass mode" in warning for warning in report["warnings"])
