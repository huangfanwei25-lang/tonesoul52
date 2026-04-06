from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_dashboard_workspace_keeps_operator_shell_markers() -> None:
    workspace_page = _read("apps/dashboard/frontend/pages/workspace.py")

    for marker in (
        "Tiered Operator Shell",
        "Tier 0 · Instant Gate",
        "Tier 1 · Orientation Shell",
        "Tier 2 · Deep Governance",
        "Open Tier 2 drawer",
    ):
        assert marker in workspace_page

    for tier_call in (
        "run_session_start_bundle(agent_id=WORKSPACE_AGENT_ID, tier=0",
        "run_session_start_bundle(agent_id=WORKSPACE_AGENT_ID, tier=1",
        "run_session_start_bundle(agent_id=WORKSPACE_AGENT_ID, tier=2",
    ):
        assert tier_call in workspace_page


def test_dashboard_workspace_keeps_tier2_bounded() -> None:
    workspace_page = _read("apps/dashboard/frontend/pages/workspace.py")

    assert "build_tier2_deep_governance_drawer" in workspace_page
    assert "import_posture" not in workspace_page
    assert "claim_view" not in workspace_page


def test_public_surfaces_stay_demo_first() -> None:
    home_page = _read("apps/web/src/app/page.tsx")
    docs_page = _read("apps/web/src/app/docs/page.tsx")
    tier_cue = _read("apps/web/src/components/TierModelPublicCue.tsx")

    assert 'TierModelPublicCue variant="compact"' in home_page
    assert 'TierModelPublicCue variant="full"' in docs_page
    assert "not the canonical operator console" in tier_cue
    assert "dashboard workspace" in tier_cue
    assert "CLI entry" in tier_cue

    for forbidden in (
        "run_session_start_bundle",
        "mutation_preflight",
        "publish_push_preflight",
        "task_board_preflight",
        "Open Tier 2 drawer",
    ):
        assert forbidden not in home_page
        assert forbidden not in docs_page
