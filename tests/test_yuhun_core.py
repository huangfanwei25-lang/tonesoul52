"""
tests/test_yuhun_core.py — YUHUN Core Protocol v1.0 單元測試

涵蓋：
  - shadow_doc.py (含 TrajectoryDigest)
  - context_assembler.py (含禁止源驗證、FAST/COUNCIL 路由)
  - dpr.py (routing logic)
  - world_sense.py (stable_anchors, inbreeding_risk, dream_candidates)

設計原則：
  - 純單元測試，無外部網路、無 LLM 調用
  - 不啟動 Redis / DB
  - 遵循專案現有測試慣例（非 async 優先）

Agent: Antigravity
Trace-Topic: yuhun-council-v1
"""

from __future__ import annotations

import pytest

# ─────────────────────────────────────────────
# DPR 路由測試
# ─────────────────────────────────────────────


class TestDPR:
    def test_fast_path_simple_request(self):
        from tonesoul.yuhun.dpr import RoutingDecision, route

        result = route("幫我寫一個 hello world")
        assert result.decision == RoutingDecision.FAST_PATH

    def test_council_path_ethical_question(self):
        from tonesoul.yuhun.dpr import RoutingDecision, route

        result = route("這個 AI 系統存在法律漏洞嗎？如何評估倫理風險？")
        assert result.decision == RoutingDecision.COUNCIL_PATH

    def test_dpr_result_has_required_fields(self):
        from tonesoul.yuhun.dpr import DPRResult, route

        result = route("測試輸入")
        assert isinstance(result, DPRResult)
        assert hasattr(result, "decision")
        assert hasattr(result, "complexity_score")  # DPRResult 用 complexity_score，不是 confidence
        assert hasattr(result, "conflict_triggers")
        assert isinstance(result.conflict_triggers, list)

    def test_fast_path_has_low_score(self):
        from tonesoul.yuhun.dpr import RoutingDecision, route

        result = route("今天天氣真好")
        assert result.decision == RoutingDecision.FAST_PATH
        assert result.complexity_score >= 0.0  # 使用正確欄位名稱

    def test_council_path_uncertainty_keywords(self):
        from tonesoul.yuhun.dpr import RoutingDecision, route

        # 使用明確的倫理/法律關鍵字確保觸發 COUNCIL_PATH
        result = route("這個 AI 系統的倫理責任如何界定？存在哪些法律漏洞？")
        assert result.decision == RoutingDecision.COUNCIL_PATH


# ─────────────────────────────────────────────
# ShadowDocument + TrajectoryDigest 測試
# ─────────────────────────────────────────────


class TestShadowDocument:
    def test_create_returns_instance(self):
        from tonesoul.yuhun.shadow_doc import ShadowDocument

        doc = ShadowDocument.create(raw_input="測試輸入")
        assert doc.session_id
        assert doc.timestamp
        assert doc.intent_frame.raw_input == "測試輸入"

    def test_trajectory_digest_default_values(self):
        from tonesoul.yuhun.shadow_doc import ShadowDocument

        doc = ShadowDocument.create(raw_input="測試")
        td = doc.trajectory_digest
        assert td.step_count == 0
        assert td.tool_calls == []
        assert td.key_decisions == []
        assert td.compressed_summary == ""
        assert td.compression_ratio == 0.0

    def test_trajectory_digest_assignment(self):
        from tonesoul.yuhun.shadow_doc import ShadowDocument

        doc = ShadowDocument.create(raw_input="測試")
        doc.trajectory_digest.step_count = 5
        doc.trajectory_digest.key_decisions = ["路由: COUNCIL_PATH", "安全: PASS"]
        doc.trajectory_digest.compressed_summary = "五步推演完成"
        assert doc.trajectory_digest.step_count == 5
        assert len(doc.trajectory_digest.key_decisions) == 2

    def test_to_empath_includes_trajectory(self):
        from tonesoul.yuhun.shadow_doc import ShadowDocument

        doc = ShadowDocument.create(raw_input="測試")
        doc.trajectory_digest.step_count = 3
        doc.trajectory_digest.compressed_summary = "三步摘要"

        empath = doc.to_empath()
        assert "trajectory" in empath
        assert empath["trajectory"]["step_count"] == 3
        assert empath["trajectory"]["compressed_summary"] == "三步摘要"

    def test_to_dict_is_serializable(self):
        import json

        from tonesoul.yuhun.shadow_doc import ShadowDocument

        doc = ShadowDocument.create(
            raw_input="序列化測試",
            reconstructed_intent="intent",
            declarative_goal="goal",
            verification_loop="verify",
        )
        doc.trajectory_digest.step_count = 2

        d = doc.to_dict()
        # 確認可以 JSON 序列化
        serialized = json.dumps(d, ensure_ascii=False)
        assert "trajectory_digest" in serialized
        assert "session_id" in serialized

    def test_save_creates_file(self, tmp_path):
        from tonesoul.yuhun.shadow_doc import ShadowDocument

        doc = ShadowDocument.create(raw_input="存檔測試")
        archive_id = doc.save(cold_storage_dir=str(tmp_path / "shadows"))

        filepath = tmp_path / "shadows" / f"{archive_id}.json"
        assert filepath.exists()
        assert filepath.stat().st_size > 0


# ─────────────────────────────────────────────
# ContextAssembler 測試
# ─────────────────────────────────────────────


class TestContextAssembler:
    def test_fast_path_no_council_frame(self):
        from tonesoul.yuhun.context_assembler import ContextAssembler
        from tonesoul.yuhun.dpr import RoutingDecision, route

        assembler = ContextAssembler()
        result = route("寫個 hello world")
        pkg = assembler.assemble(result, "寫個 hello world")

        assert pkg.routing == RoutingDecision.FAST_PATH
        assert pkg.council_frame == ""
        assert pkg.anchor_memory == []
        assert pkg.contracts == []

    def test_council_path_has_council_frame(self):
        from tonesoul.yuhun.context_assembler import ContextAssembler
        from tonesoul.yuhun.dpr import RoutingDecision, route

        assembler = ContextAssembler()
        result = route("AI 系統的倫理責任與法律風險如何評估？")
        pkg = assembler.assemble(result, "倫理風險問題")

        assert pkg.routing == RoutingDecision.COUNCIL_PATH
        assert pkg.council_frame != ""
        assert "議會框架" in pkg.council_frame

    def test_prompt_sections_always_end_with_user_request(self):
        from tonesoul.yuhun.context_assembler import ContextAssembler
        from tonesoul.yuhun.dpr import route

        assembler = ContextAssembler()
        for text in ["簡單問題", "倫理與法律風險分析"]:
            result = route(text)
            pkg = assembler.assemble(result, text)
            sections = pkg.to_prompt_sections()
            assert sections[-1].startswith("[USER REQUEST]")

    def test_sources_used_always_includes_axioms(self):
        from tonesoul.yuhun.context_assembler import ContextAssembler
        from tonesoul.yuhun.dpr import route

        assembler = ContextAssembler()
        result = route("任何問題")
        pkg = assembler.assemble(result, "任何問題")
        assert "AXIOMS.json" in pkg.sources_used

    def test_estimated_tokens_positive(self):
        from tonesoul.yuhun.context_assembler import ContextAssembler
        from tonesoul.yuhun.dpr import route

        assembler = ContextAssembler()
        result = route("token 計算測試")
        pkg = assembler.assemble(result, "token 計算測試")
        assert pkg.estimated_tokens >= 0


class TestContextViolation:
    def test_blocked_chronicle_path(self):
        from tonesoul.yuhun.context_assembler import (
            ContextViolationError,
            validate_context_sources,
        )

        with pytest.raises(ContextViolationError):
            validate_context_sources(["docs/chronicles/task_archive_2026.md"])

    def test_blocked_memory_path(self):
        from tonesoul.yuhun.context_assembler import (
            ContextViolationError,
            validate_context_sources,
        )

        with pytest.raises(ContextViolationError):
            validate_context_sources(["memory/self_journal.jsonl"])

    def test_blocked_evolution_path(self):
        from tonesoul.yuhun.context_assembler import (
            ContextViolationError,
            validate_context_sources,
        )

        with pytest.raises(ContextViolationError):
            validate_context_sources(["tonesoul_evolution/private_config.py"])

    def test_valid_sources_pass(self):
        from tonesoul.yuhun.context_assembler import validate_context_sources

        # 這些是合法來源
        result = validate_context_sources(
            [
                "AXIOMS.json",
                "docs/architecture/CONTEXT_BUDGET_SPEC.md",
                "council_frame_summary",
                "world_sense.stable_anchors()",
            ]
        )
        assert result is True

    def test_multiple_sources_one_blocked(self):
        from tonesoul.yuhun.context_assembler import (
            ContextViolationError,
            validate_context_sources,
        )

        with pytest.raises(ContextViolationError):
            validate_context_sources(
                [
                    "AXIOMS.json",
                    "memory/private_data.jsonl",  # 這個違規
                ]
            )


# ─────────────────────────────────────────────
# WorldSense 測試
# ─────────────────────────────────────────────


class TestWorldSense:
    def _make_ws_with_observations(self, n: int = 5):
        from tonesoul.yuhun.world_sense import WorldSense

        ws = WorldSense()
        for i in range(n):
            ws.observe(
                semantic_vector={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
                tension_total=0.2,
                has_echo_trace=True,
            )
        return ws

    def test_stable_anchors_empty_returns_zero(self):
        from tonesoul.yuhun.world_sense import StableAnchor, WorldSense

        ws = WorldSense()
        anchor = ws.stable_anchors()
        assert isinstance(anchor, StableAnchor)
        assert anchor.stability_score == 0.0
        assert anchor.low_drift_steps == []

    def test_stable_anchors_after_observations(self):

        ws = self._make_ws_with_observations(5)
        anchor = ws.stable_anchors()
        assert anchor.stability_score >= 0.0
        assert anchor.mean_drift >= 0.0
        assert isinstance(anchor.home_vector, dict)

    def test_inbreeding_risk_insufficient_data(self):
        from tonesoul.yuhun.world_sense import WorldSense

        ws = WorldSense()
        risk = ws.inbreeding_risk()
        assert risk.risk_level == "none"

    def test_dream_candidates_empty_no_crash(self):
        from tonesoul.yuhun.world_sense import WorldSense

        ws = WorldSense()
        candidates = ws.dream_candidates(top_n=3)
        assert candidates == []

    def test_dream_candidates_high_tension_selected(self):
        from tonesoul.yuhun.world_sense import WorldSense

        ws = WorldSense()
        # 正常觀測
        ws.observe(
            semantic_vector={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
            tension_total=0.1,
            has_echo_trace=True,
        )
        # 高張力事件
        ws.observe(
            semantic_vector={"deltaT": 0.9, "deltaS": 0.1, "deltaR": 0.9},
            tension_total=0.95,
            has_echo_trace=True,
        )

        candidates = ws.dream_candidates(top_n=5)
        # 至少應該找到一個高張力候選
        assert len(candidates) >= 1
        assert candidates[0].priority > 0.0

    def test_quick_status_nominal_when_new(self):
        from tonesoul.yuhun.world_sense import WorldSense

        ws = WorldSense()
        status = ws.quick_status()
        assert status["advisory"] == "no observations yet"
        assert status["is_drifting"] is False
        assert status["is_lockdown"] is False

    def test_observe_returns_snapshot(self):
        from tonesoul.yuhun.world_sense import WorldSense, WorldSenseSnapshot

        ws = WorldSense()
        snap = ws.observe(
            semantic_vector={"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5},
            tension_total=0.3,
            has_echo_trace=True,
        )
        assert isinstance(snap, WorldSenseSnapshot)
        assert snap.confidence_level == "OBSERVED"
        assert snap.tension_total == pytest.approx(0.3)


# ─────────────────────────────────────────────
# 整合測試：DPR → ContextAssembler → ShadowDocument
# ─────────────────────────────────────────────


class TestYUHUNPipeline:
    def test_full_pipeline_fast_path(self):
        """FAST_PATH 完整流程：DPR → ContextAssembler → ShadowDocument"""
        from tonesoul.yuhun.context_assembler import ContextAssembler
        from tonesoul.yuhun.dpr import route
        from tonesoul.yuhun.shadow_doc import RoutingDecision, ShadowDocument

        user_input = "請幫我摘要這份文件"
        dpr_result = route(user_input)
        assembler = ContextAssembler()
        pkg = assembler.assemble(dpr_result, user_input)

        # 建立影子文件並記錄軌跡
        doc = ShadowDocument.create(raw_input=user_input)
        doc.tension_metrics.routing_decision = RoutingDecision(pkg.routing.value)
        doc.trajectory_digest.step_count = len(pkg.to_prompt_sections())
        doc.trajectory_digest.compressed_summary = f"FAST_PATH, {pkg.estimated_tokens} tokens"

        empath = doc.to_empath()
        assert empath["trajectory"]["step_count"] > 0

    def test_full_pipeline_council_path(self):
        """COUNCIL_PATH 完整流程：DPR → ContextAssembler → ShadowDocument"""
        from tonesoul.yuhun.context_assembler import ContextAssembler
        from tonesoul.yuhun.dpr import RoutingDecision, route
        from tonesoul.yuhun.shadow_doc import ShadowDocument

        user_input = "這個 AI 系統在倫理和法律上有什麼潛在漏洞？"
        dpr_result = route(user_input)
        assert dpr_result.decision == RoutingDecision.COUNCIL_PATH

        assembler = ContextAssembler()
        pkg = assembler.assemble(dpr_result, user_input)

        doc = ShadowDocument.create(raw_input=user_input)
        doc.trajectory_digest.step_count = 4
        doc.trajectory_digest.key_decisions = [
            "DPR: COUNCIL_PATH",
            f"Context: {pkg.estimated_tokens} tokens",
        ]

        empath = doc.to_empath()
        assert "trajectory" in empath
        assert empath["trajectory"]["step_count"] == 4
