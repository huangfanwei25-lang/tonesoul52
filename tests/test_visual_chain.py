"""Tests for the Visual Memory Chain module."""

from __future__ import annotations

from tonesoul.memory.visual_chain import (
    FrameType,
    VisualChain,
    VisualFrame,
    render_frame,
)

# ---------------------------------------------------------------------------
# render_frame tests
# ---------------------------------------------------------------------------


class TestRenderFrame:
    def test_session_state_renders_mermaid(self):
        data = {
            "tension": 0.85,
            "verdict": "declare_stance",
            "council_mode": "hybrid",
            "topics": ["ethics", "identity"],
            "commitments_active": 3,
            "ruptures": 1,
            "values_count": 5,
        }
        result = render_frame(FrameType.SESSION_STATE, data)
        assert "graph TD" in result
        assert "HIGH 0.85" in result
        assert "declare_stance" in result
        assert "ethics" in result

    def test_tension_map_renders_mermaid(self):
        data = {"tensions": {"ethics": 0.9, "facts": 0.2, "tone": 0.5}}
        result = render_frame(FrameType.TENSION_MAP, data)
        assert "graph LR" in result
        assert "ethics" in result
        assert "0.90" in result or "0.9" in result

    def test_commitment_tree_renders_mermaid(self):
        data = {
            "commitments": [
                {"text": "Never lie", "status": "active"},
                {"text": "Be transparent", "status": "fulfilled"},
                {"text": "Protect user", "status": "broken"},
            ]
        }
        result = render_frame(FrameType.COMMITMENT_TREE, data)
        assert "Commitments" in result
        assert "Never lie" in result

    def test_council_verdict_renders_mermaid(self):
        data = {
            "verdict": "approve",
            "perspectives": {
                "Philosopher": "agree",
                "Engineer": "neutral",
                "Guardian": "caution",
            },
        }
        result = render_frame(FrameType.COUNCIL_VERDICT, data)
        assert "approve" in result
        assert "Philosopher" in result

    def test_conversation_arc_renders_mermaid(self):
        data = {
            "arc_points": [
                {"turn": 0, "tone": "neutral", "tension": 0.1},
                {"turn": 1, "tone": "curious", "tension": 0.3},
                {"turn": 2, "tone": "tense", "tension": 0.8},
                {"turn": 3, "tone": "resolved", "tension": 0.2},
            ]
        }
        result = render_frame(FrameType.CONVERSATION_ARC, data)
        assert "graph LR" in result
        assert "neutral" in result
        assert "tense" in result

    def test_custom_type_renders_fallback(self):
        result = render_frame(FrameType.CUSTOM, {"key": "value"})
        assert "CUSTOM" in result

    def test_empty_data_renders_gracefully(self):
        result = render_frame(FrameType.TENSION_MAP, {})
        assert "No tension data" in result

    def test_empty_commitments_renders_gracefully(self):
        result = render_frame(FrameType.COMMITMENT_TREE, {})
        assert "No active commitments" in result


# ---------------------------------------------------------------------------
# VisualFrame tests
# ---------------------------------------------------------------------------


class TestVisualFrame:
    def test_round_trip_serialization(self):
        frame = VisualFrame(
            frame_id="vf_0001",
            frame_type=FrameType.SESSION_STATE,
            title="Test Frame",
            mermaid="graph TD\n    A --> B",
            data={"tension": 0.5},
            created_at="2026-02-13T12:00:00Z",
            tags=["test", "tension"],
            branch="main",
            turn_index=1,
        )
        d = frame.to_dict()
        restored = VisualFrame.from_dict(d)
        assert restored.frame_id == "vf_0001"
        assert restored.frame_type == FrameType.SESSION_STATE
        assert restored.title == "Test Frame"
        assert restored.data["tension"] == 0.5
        assert restored.tags == ["test", "tension"]
        assert restored.branch == "main"

    def test_from_dict_handles_unknown_type(self):
        raw = {
            "frame_type": "nonexistent",
            "frame_id": "x",
            "title": "t",
            "mermaid": "",
            "data": {},
            "created_at": "",
        }
        frame = VisualFrame.from_dict(raw)
        assert frame.frame_type == FrameType.CUSTOM


# ---------------------------------------------------------------------------
# VisualChain tests
# ---------------------------------------------------------------------------


class TestVisualChain:
    def test_capture_and_get_recent(self):
        chain = VisualChain()
        chain.capture(
            frame_type=FrameType.SESSION_STATE,
            title="Turn 1",
            data={"tension": 0.3},
            tags=["low"],
        )
        chain.capture(
            frame_type=FrameType.SESSION_STATE,
            title="Turn 2",
            data={"tension": 0.8},
            tags=["high"],
        )
        recent = chain.get_recent(n=1)
        assert len(recent) == 1
        assert recent[0].title == "Turn 2"

    def test_query_by_tags(self):
        chain = VisualChain()
        chain.capture(FrameType.SESSION_STATE, "A", {"tension": 0.1}, tags=["calm"])
        chain.capture(FrameType.TENSION_MAP, "B", {"tensions": {"x": 0.9}}, tags=["crisis"])
        chain.capture(FrameType.SESSION_STATE, "C", {"tension": 0.2}, tags=["calm"])

        results = chain.query(tags=["calm"])
        assert len(results) == 2
        assert all("calm" in f.tags for f in results)

    def test_query_by_frame_type(self):
        chain = VisualChain()
        chain.capture(FrameType.SESSION_STATE, "A", {})
        chain.capture(FrameType.TENSION_MAP, "B", {})
        chain.capture(FrameType.SESSION_STATE, "C", {})

        results = chain.query(frame_type=FrameType.TENSION_MAP)
        assert len(results) == 1
        assert results[0].title == "B"

    def test_branching(self):
        chain = VisualChain()
        f1 = chain.capture(FrameType.SESSION_STATE, "Main 1", {}, branch="main")
        chain.fork_branch("experiment", f1.frame_id)
        chain.capture(FrameType.SESSION_STATE, "Exp 1", {}, branch="experiment")
        chain.capture(FrameType.SESSION_STATE, "Main 2", {}, branch="main")

        main_frames = chain.get_branch("main")
        exp_frames = chain.get_branch("experiment")
        assert len(main_frames) == 2
        assert len(exp_frames) == 1
        assert chain.list_branches() == ["main", "experiment"]

    def test_list_tags(self):
        chain = VisualChain()
        chain.capture(FrameType.SESSION_STATE, "A", {}, tags=["ethics", "tension"])
        chain.capture(FrameType.SESSION_STATE, "B", {}, tags=["ethics"])

        tags = chain.list_tags()
        assert tags["ethics"] == 2
        assert tags["tension"] == 1

    def test_chain_summary(self):
        chain = VisualChain()
        chain.capture(FrameType.SESSION_STATE, "A", {"tension": 0.5})
        chain.capture(FrameType.TENSION_MAP, "B", {"tensions": {}})

        summary = chain.get_chain_summary()
        assert summary["total_frames"] == 2
        assert "main" in summary["branches"]
        assert summary["latest_turn"] == 2

    def test_render_recent_as_markdown(self):
        chain = VisualChain()
        chain.capture(FrameType.SESSION_STATE, "Turn 1", {"tension": 0.5})
        md = chain.render_recent_as_markdown(n=1)
        assert "Visual Memory Chain" in md
        assert "Turn 1" in md
        assert "```mermaid" in md

    def test_persistence_round_trip(self, tmp_path):
        path = tmp_path / "chain.json"
        chain = VisualChain(storage_path=path)
        chain.capture(FrameType.SESSION_STATE, "Persisted", {"tension": 0.6}, tags=["test"])

        assert path.exists()

        chain2 = VisualChain(storage_path=path)
        assert chain2.frame_count == 1
        assert chain2.get_recent(1)[0].title == "Persisted"
        assert chain2.list_tags() == {"test": 1}

    def test_empty_chain_renders_gracefully(self):
        chain = VisualChain()
        md = chain.render_recent_as_markdown()
        assert "No frames captured" in md

    def test_merge_context(self):
        chain = VisualChain()
        chain.capture(FrameType.SESSION_STATE, "Main", {"tension": 0.3}, branch="main")
        chain.capture(FrameType.TENSION_MAP, "Alt", {"tensions": {"x": 0.9}}, branch="alt")

        merged = chain.merge_context(["main", "alt"])
        assert "main" in merged
        assert "alt" in merged
        assert "```mermaid" in merged
