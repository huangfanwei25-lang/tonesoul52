"""Tests for visual-chain and persona attachment context injection."""

from __future__ import annotations

from pathlib import Path

from tonesoul.memory.visual_chain import FrameType, VisualChain
from tonesoul.unified_pipeline import UnifiedPipeline


def _build_chain_with_frame() -> VisualChain:
    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 0",
        data={"tension": 0.3, "verdict": "approve", "council_mode": "hybrid"},
        tags=["auto"],
    )
    return chain


def test_visual_context_markdown_contains_recent_frame() -> None:
    chain = _build_chain_with_frame()
    markdown = chain.render_recent_as_markdown(n=3)
    assert "Visual Memory Chain" in markdown
    assert "session_state" in markdown
    assert len(markdown) > 50


def test_pipeline_injects_visual_context_when_frames_exist() -> None:
    pipeline = UnifiedPipeline()
    pipeline._visual_chain = _build_chain_with_frame()

    original = "user asks for next action"
    updated = pipeline._inject_visual_context(original)

    assert "[脈絡記憶 — 最近視覺快照]" in updated
    assert "Visual Memory Chain" in updated
    assert original in updated


def test_pipeline_skips_visual_context_when_chain_is_empty() -> None:
    pipeline = UnifiedPipeline()
    pipeline._visual_chain = VisualChain()

    original = "empty chain input"
    updated = pipeline._inject_visual_context(original)

    assert updated == original


def test_build_injection_context_splits_persona_and_context_views() -> None:
    pipeline = UnifiedPipeline()
    pipeline._visual_chain = _build_chain_with_frame()
    persona_config = {
        "style": "concise",
        "weights": {"meaning": 60, "practical": 30, "safety": 10},
        "response_length": "short",
        "custom_roles": [
            {
                "name": "risk_auditor",
                "description": "check failure paths first",
                "prompt_hint": "prefer fail-closed behavior",
                "attachments": [{"label": "policy", "path": "docs/policy.md", "note": "baseline"}],
            }
        ],
    }

    original = "planning request"
    updated = pipeline.build_injection_context(original, persona_config=persona_config)

    assert updated.count("[脈絡記憶 — 最近視覺快照]") == 1
    assert updated.count("[用戶偏好:") == 1
    assert "risk_auditor" in updated
    assert "docs/policy.md" in updated
    assert updated.endswith(original)


def test_persona_attachment_excerpt_included_when_path_allowed(tmp_path: Path) -> None:
    pipeline = UnifiedPipeline()
    policy_dir = tmp_path / "docs"
    policy_dir.mkdir(parents=True, exist_ok=True)
    policy_path = policy_dir / "policy.md"
    policy_path.write_text("Attachment line one.\nAttachment line two.", encoding="utf-8")

    pipeline._repo_root = tmp_path
    pipeline._persona_attachment_allow_prefixes = ("docs/",)
    pipeline._persona_attachment_max_files = 2
    pipeline._persona_attachment_max_chars = 120
    pipeline._persona_attachment_cache.clear()

    updated = pipeline._inject_persona_memory(
        "hello",
        {
            "custom_roles": [
                {
                    "name": "risk_auditor",
                    "attachments": [
                        {"label": "policy", "path": "docs/policy.md", "note": "baseline"}
                    ],
                }
            ]
        },
    )

    assert "附件摘要=" in updated
    assert "Attachment line one." in updated


def test_persona_attachment_excerpt_blocks_disallowed_path(tmp_path: Path) -> None:
    pipeline = UnifiedPipeline()
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("SECRET_TOKEN_123", encoding="utf-8")

    pipeline._repo_root = tmp_path
    pipeline._persona_attachment_allow_prefixes = ("docs/",)
    pipeline._persona_attachment_cache.clear()

    updated = pipeline._inject_persona_memory(
        "hello",
        {
            "custom_roles": [
                {
                    "name": "risk_auditor",
                    "attachments": [
                        {"label": "secret", "path": "secret.txt", "note": "should block"}
                    ],
                }
            ]
        },
    )

    assert "secret.txt" in updated
    assert "SECRET_TOKEN_123" not in updated
