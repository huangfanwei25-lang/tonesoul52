from __future__ import annotations

from pathlib import Path

import yaml

from tonesoul.frame_router import (
    _role_alignment,
    _score_frame,
    build_frame_plan,
    route_frames,
)


def _make_context(
    *,
    domain: str = "finance",
    decision_mode: str = "review",
    task: str = "assess portfolio risk",
    objective: str = "hedge downside exposure",
) -> dict[str, object]:
    return {
        "context": {
            "domain": domain,
            "task": task,
            "objective": objective,
        },
        "time_island": {
            "kairos": {
                "decision_mode": decision_mode,
            }
        },
    }


def _make_frame(
    frame_id: str,
    *,
    domains: list[str] | None = None,
    decision_modes: list[str] | None = None,
    keywords: list[str] | None = None,
    roles: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": frame_id,
        "description": f"{frame_id} frame",
        "signals": {
            "domains": domains or [],
            "decision_modes": decision_modes or [],
            "keywords": keywords or [],
        },
        "roles": roles or [],
    }


def _write_role_catalog(path: Path) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "version": "2026.03",
                "operational_roles": {
                    "Risk": {"aligns_to": "guardian"},
                    "Recorder": {"aligns_to": "scribe"},
                },
                "governance_roles": {
                    "guardian": {"level": 3},
                    "scribe": {"level": 1},
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def test_score_frame_keyword_match() -> None:
    score = _score_frame(
        _make_frame(
            "risk",
            domains=["finance"],
            decision_modes=["review"],
            keywords=["risk", "hedge"],
        ),
        _make_context(),
    )

    assert score == 5


def test_score_frame_no_match() -> None:
    score = _score_frame(
        _make_frame(
            "analysis",
            domains=["governance"],
            decision_modes=["lockdown"],
            keywords=["poetry"],
        ),
        _make_context(),
    )

    assert score == 0


def test_route_frames_returns_top_n() -> None:
    registry = [
        _make_frame("analysis", domains=["finance"], keywords=["assess"]),
        _make_frame(
            "risk",
            domains=["finance"],
            decision_modes=["review"],
            keywords=["risk", "hedge"],
        ),
        _make_frame(
            "execution",
            domains=["finance"],
            decision_modes=["review"],
            keywords=["portfolio"],
        ),
    ]

    selected = route_frames(_make_context(), registry, limit=2)

    assert [frame["id"] for frame, _score in selected] == ["risk", "execution"]


def test_route_frames_empty_registry() -> None:
    assert route_frames(_make_context(), [], limit=2) == []


def test_build_frame_plan_structure(tmp_path: Path) -> None:
    plan = build_frame_plan(
        _make_context(),
        [
            _make_frame(
                "risk",
                domains=["finance"],
                decision_modes=["review"],
                keywords=["risk"],
                roles=["Risk"],
            )
        ],
        role_catalog_path=str(tmp_path / "missing_role_catalog.yaml"),
    )

    assert "generated_at" in plan
    assert "selected_frames" in plan
    assert "role_summary" in plan
    assert "council_summary" in plan
    assert plan["selected_frames"][0]["id"] == "risk"
    assert plan["role_summary"]["operational_roles"] == ["Risk"]


def test_build_frame_plan_with_role_catalog(tmp_path: Path) -> None:
    role_catalog_path = _write_role_catalog(tmp_path / "role_catalog.yaml")
    plan = build_frame_plan(
        _make_context(),
        [
            _make_frame(
                "risk",
                domains=["finance"],
                decision_modes=["review"],
                keywords=["risk"],
                roles=["Risk", "Recorder"],
            )
        ],
        role_catalog_path=str(role_catalog_path),
    )

    selected = plan["selected_frames"][0]
    role_summary = plan["role_summary"]
    assert plan["role_catalog_version"] == "2026.03"
    assert selected["governance_roles"] == ["guardian", "scribe"]
    assert role_summary["operational_roles"] == ["Recorder", "Risk"]
    assert role_summary["governance_roles"] == ["guardian", "scribe"]
    assert role_summary["max_governance_level"] == 3


def test_role_alignment_known_unmatched() -> None:
    roles, governance_roles, role_map = _role_alignment(
        ["Risk", "Mystery"],
        {
            "operational_roles": {
                "Risk": {"aligns_to": "guardian"},
            },
            "governance_roles": {
                "guardian": {"level": 2},
            },
        },
    )

    assert roles == ["Risk", "Mystery"]
    assert governance_roles == ["guardian"]
    assert role_map == [
        {
            "role": "Risk",
            "governance_role": "guardian",
            "governance_level": 2,
        },
        {
            "role": "Mystery",
            "governance_role": "unknown",
            "governance_level": None,
        },
    ]
