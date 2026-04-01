import json
import subprocess

import scripts.verify_incremental_commit_attribution as incremental


def test_verify_revision_keeps_json_payload_on_strict_failure(monkeypatch) -> None:
    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args[0],
            1,
            stdout=json.dumps(
                {
                    "ok": False,
                    "summary": "fix(ci): missing trailers",
                    "has_agent": False,
                    "has_topic": False,
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(incremental.subprocess, "run", fake_run)

    payload = incremental._verify_revision("abc123")

    assert payload["ok"] is False
    assert payload["summary"] == "fix(ci): missing trailers"
    assert payload["rev"] == "abc123"
    assert payload["exit_code"] == 1


def test_resolve_revision_plan_for_push_uses_before_range(monkeypatch) -> None:
    monkeypatch.setattr(incremental, "_sha_exists", lambda revision: revision == "before123")
    monkeypatch.setattr(incremental, "_rev_list", lambda spec: ["commit-a", "commit-b"])

    plan = incremental.resolve_revision_plan(
        event_name="push",
        head_sha="head456",
        before_sha="before123",
        pr_base_sha=None,
        pr_head_sha=None,
        local_base_candidates=["origin/master"],
    )

    assert plan["mode"] == "push_incremental"
    assert plan["range_spec"] == "before123..head456"
    assert plan["base_ref"] == "before123"
    assert plan["checked_revisions"] == ["commit-a", "commit-b"]


def test_resolve_revision_plan_for_local_uses_merge_base(monkeypatch) -> None:
    monkeypatch.setattr(incremental, "_first_existing_base_ref", lambda refs: "origin/main")
    monkeypatch.setattr(incremental, "_merge_base", lambda base, head: "merge-base-1")
    monkeypatch.setattr(incremental, "_rev_list", lambda spec: ["commit-local"])

    plan = incremental.resolve_revision_plan(
        event_name="",
        head_sha="HEAD",
        before_sha=None,
        pr_base_sha=None,
        pr_head_sha=None,
        local_base_candidates=["origin/main", "main"],
    )

    assert plan["mode"] == "local_incremental"
    assert plan["range_spec"] == "merge-base-1..HEAD"
    assert plan["base_ref"] == "origin/main"
    assert plan["checked_revisions"] == ["commit-local"]


def test_resolve_revision_plan_prefers_enforcement_anchor_when_available(monkeypatch) -> None:
    monkeypatch.setattr(
        incremental, "_sha_exists", lambda revision: revision in {"anchor-1", "HEAD"}
    )
    monkeypatch.setattr(
        incremental, "_is_ancestor", lambda ancestor, head: (ancestor, head) == ("anchor-1", "HEAD")
    )
    monkeypatch.setattr(incremental, "_rev_list", lambda spec: ["anchored-a", "anchored-b"])

    plan = incremental.resolve_revision_plan(
        event_name="pull_request",
        head_sha="HEAD",
        before_sha=None,
        pr_base_sha="base-sha",
        pr_head_sha="head-sha",
        local_base_candidates=["origin/master"],
        enforcement_anchor="anchor-1",
    )

    assert plan["mode"] == "anchored_incremental"
    assert plan["range_spec"] == "anchor-1..HEAD"
    assert plan["base_ref"] == "anchor-1"
    assert plan["checked_revisions"] == ["anchored-a", "anchored-b"]
    assert plan["anchor_override_used"] is True


def test_build_report_collects_missing_context(monkeypatch) -> None:
    monkeypatch.setattr(
        incremental,
        "resolve_revision_plan",
        lambda **kwargs: {
            "event_name": "push",
            "mode": "push_incremental",
            "range_spec": "before..head",
            "base_ref": "before",
            "checked_revisions": ["ok-1", "bad-2"],
        },
    )

    def fake_verify(revision: str) -> dict[str, object]:
        if revision == "bad-2":
            return {
                "rev": revision,
                "ok": False,
                "summary": "missing Agent trailer",
                "has_agent": False,
                "has_topic": True,
            }
        return {
            "rev": revision,
            "ok": True,
            "summary": "feat: valid trailers",
            "has_agent": True,
            "has_topic": True,
        }

    monkeypatch.setattr(incremental, "_verify_revision", fake_verify)

    report = incremental.build_report(
        event_name="push",
        head_sha="head",
        before_sha="before",
        pr_base_sha=None,
        pr_head_sha=None,
        local_base_candidates=["origin/master"],
    )

    assert report["ok"] is False
    assert report["missing_count"] == 1
    assert report["missing"] == [
        {
            "rev": "bad-2",
            "summary": "missing Agent trailer",
            "error": "",
        }
    ]


def test_build_report_keeps_unexpected_revision_error_in_context(monkeypatch) -> None:
    monkeypatch.setattr(
        incremental,
        "resolve_revision_plan",
        lambda **kwargs: {
            "event_name": "local",
            "mode": "local_incremental",
            "range_spec": None,
            "base_ref": "origin/master",
            "checked_revisions": ["broken-1"],
        },
    )
    monkeypatch.setattr(
        incremental,
        "_verify_revision",
        lambda revision: (_ for _ in ()).throw(RuntimeError("git log failed")),
    )

    report = incremental.build_report(
        event_name="",
        head_sha="HEAD",
        before_sha=None,
        pr_base_sha=None,
        pr_head_sha=None,
        local_base_candidates=["origin/master"],
    )

    assert report["ok"] is False
    assert report["missing_count"] == 1
    assert report["results"][0]["error"] == "git log failed"
    assert report["missing"][0]["error"] == "git log failed"


def test_build_report_exempts_synthetic_merge_commit(monkeypatch) -> None:
    monkeypatch.setattr(
        incremental,
        "resolve_revision_plan",
        lambda **kwargs: {
            "event_name": "pull_request",
            "mode": "anchored_incremental",
            "range_spec": "anchor..HEAD",
            "base_ref": "anchor",
            "checked_revisions": ["merge-1"],
        },
    )
    monkeypatch.setattr(
        incremental,
        "_verify_revision",
        lambda revision: {
            "rev": revision,
            "ok": False,
            "summary": "Merge feature-head into base-head",
            "has_agent": False,
            "has_topic": False,
            "changed_files": [],
            "exempted": False,
            "exemption_reason": None,
        },
    )

    report = incremental.build_report(
        event_name="pull_request",
        head_sha="HEAD",
        before_sha=None,
        pr_base_sha="base",
        pr_head_sha="head",
        local_base_candidates=["origin/master"],
    )

    assert report["ok"] is True
    assert report["missing_count"] == 0
    assert report["results"][0]["ok"] is True
    assert report["results"][0]["exempted"] is True
    assert report["results"][0]["exemption_reason"] == "synthetic_merge_commit"


def test_build_report_can_include_tree_equivalence(monkeypatch) -> None:
    monkeypatch.setattr(
        incremental,
        "resolve_revision_plan",
        lambda **kwargs: {
            "event_name": "local",
            "mode": "local_incremental",
            "range_spec": None,
            "base_ref": "origin/master",
            "checked_revisions": ["good-1"],
        },
    )
    monkeypatch.setattr(
        incremental,
        "_verify_revision",
        lambda revision: {
            "rev": revision,
            "ok": True,
            "summary": "feat: valid trailers",
            "has_agent": True,
            "has_topic": True,
        },
    )
    monkeypatch.setattr(
        incremental,
        "_tree_hash",
        lambda revision: {
            "feature-head": "tree-123",
            "backfill-head": "tree-123",
        }.get(revision),
    )

    report = incremental.build_report(
        event_name="",
        head_sha="feature-head",
        before_sha=None,
        pr_base_sha=None,
        pr_head_sha=None,
        local_base_candidates=["origin/master"],
        equivalent_ref="backfill-head",
    )

    assert report["ok"] is True
    assert report["equivalence"] == {
        "head_revision": "feature-head",
        "compare_revision": "backfill-head",
        "head_tree": "tree-123",
        "compare_tree": "tree-123",
        "tree_equal": True,
    }


def test_build_report_marks_tree_equivalence_false_when_compare_ref_differs(monkeypatch) -> None:
    monkeypatch.setattr(
        incremental,
        "resolve_revision_plan",
        lambda **kwargs: {
            "event_name": "local",
            "mode": "local_incremental",
            "range_spec": None,
            "base_ref": "origin/master",
            "checked_revisions": ["good-1"],
        },
    )
    monkeypatch.setattr(
        incremental,
        "_verify_revision",
        lambda revision: {
            "rev": revision,
            "ok": True,
            "summary": "feat: valid trailers",
            "has_agent": True,
            "has_topic": True,
        },
    )
    monkeypatch.setattr(
        incremental,
        "_tree_hash",
        lambda revision: {
            "feature-head": "tree-123",
            "backfill-head": "tree-999",
        }.get(revision),
    )

    report = incremental.build_report(
        event_name="",
        head_sha="feature-head",
        before_sha=None,
        pr_base_sha=None,
        pr_head_sha=None,
        local_base_candidates=["origin/master"],
        equivalent_ref="backfill-head",
    )

    assert report["ok"] is True
    assert report["equivalence"]["tree_equal"] is False
    assert report["equivalence"]["head_tree"] == "tree-123"
    assert report["equivalence"]["compare_tree"] == "tree-999"


def test_tree_equivalence_satisfied_only_when_tree_equal_true() -> None:
    assert incremental._tree_equivalence_satisfied({"equivalence": {"tree_equal": True}}) is True
    assert incremental._tree_equivalence_satisfied({"equivalence": {"tree_equal": False}}) is False
    assert incremental._tree_equivalence_satisfied({}) is False
