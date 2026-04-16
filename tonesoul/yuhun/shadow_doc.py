"""
YUHUN Core Protocol v1.0 — JSON Shadow Document
影子文件格式定義與生成工具

每次議會推演必須生成此文件。
在前端隱藏，但永久封存於後端冷儲存。
如同飛機黑盒子：乘客看不見，但事故調查時可調閱。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

# ─────────────────────────────────────────────
# 枚舉類型
# ─────────────────────────────────────────────


class SafetyVerdict(str, Enum):
    PASS = "PASS"
    FLAG = "FLAG"
    BLOCK = "BLOCK"


class OutputMode(str, Enum):
    SINGLE_TRACK = "SINGLE_TRACK"
    DUAL_TRACK = "DUAL_TRACK"
    TOOL_CALL = "TOOL_CALL"  # 法規空白 → 觸發外部工具


class RoutingDecision(str, Enum):
    FAST_PATH = "FAST_PATH"
    COUNCIL_PATH = "COUNCIL_PATH"


class BlockerSeverity(str, Enum):
    HARD = "HARD"  # 物理/法律上不可逾越
    SOFT = "SOFT"  # 技術難度高但理論可克服


# ─────────────────────────────────────────────
# 子結構
# ─────────────────────────────────────────────


@dataclass
class IntentFrame:
    raw_input: str
    reconstructed_intent: str  # 補幀後 20 詞組以上
    declarative_goal: str  # 轉化後的宣告式目標
    verification_loop: str  # 如何驗證目標達成


@dataclass
class L1Blocker:
    type: str  # physical | legal | data | technical
    description: str
    source: str
    severity: BlockerSeverity


@dataclass
class L2Opportunity:
    type: str  # framework_shift | prerequisite_change | analogy | historical_precedent
    description: str
    confidence_level: str = "L2_THEORETICAL"
    prerequisite_changes: list[str] = field(default_factory=list)
    analogy: Optional[str] = None


@dataclass
class LogicianOutput:
    verdict: str  # BLOCK | CAUTION | PASS | INSUFFICIENT_DATA
    confidence: float  # 0.0 - 1.0
    resistance_score: float  # 0.0 - 1.0，通常 0.9 代表 90% 阻力
    L1_blockers: list[L1Blocker]
    summary: str


@dataclass
class CreatorOutput:
    verdict: str  # BREAKTHROUGH_FOUND | MARGINAL | NONE
    confidence: float
    breakthrough_score: float  # 0.0 - 1.0，通常 0.1 代表 10% 可能
    L2_opportunities: list[L2Opportunity]
    summary: str


@dataclass
class SafetyOutput:
    verdict: SafetyVerdict
    red_lines_triggered: list[str]
    smoothness_hallucination_detected: bool
    L3_masquerade_detected: bool
    empath_bias_detected: bool
    intervention: Optional[str]
    reason: str


@dataclass
class TensionMetrics:
    semantic_distance: float  # 0.0 - 1.0
    logical_conflict_rate: float  # 0.0 - 1.0
    routing_decision: RoutingDecision
    output_mode: OutputMode


@dataclass
class TrajectoryDigest:
    """
    軌跡摘要 — 壓縮版的推演過程記錄

    靈感來源：Hermes Agent trajectory_compressor.py
    目的：讓 DreamEngine 的做夢材料不只是數值快照，也含「過程」
    規格：docs/architecture/CONTEXT_BUDGET_SPEC.md（Layer 2 來源）
    """

    step_count: int = 0  # 推演步驟數
    tool_calls: list[str] = field(default_factory=list)  # 工具調用序列（壓縮名稱）
    key_decisions: list[str] = field(default_factory=list)  # 關鍵決策節點
    compressed_summary: str = ""  # 最終壓縮摘要（< 200 tokens）
    compression_ratio: float = 0.0  # 原始長度 / 壓縮後長度


@dataclass
class LegalProfile:
    applicable_laws: list[str]
    gap_detected: bool
    social_value_matrix_triggered: bool
    judicial_precedents: list[str]


@dataclass
class Lifecycle:
    kv_cache_flushed: bool = True
    cold_storage_archived: bool = True
    archive_id: str = field(default_factory=lambda: f"COLD-{uuid.uuid4().hex[:8].upper()}")
    retrievable_for_audit: bool = True


# ─────────────────────────────────────────────
# 主文件
# ─────────────────────────────────────────────


@dataclass
class ShadowDocument:
    """
    JSON 影子文件 — 議會推演的完整記錄

    使用方式：
        doc = ShadowDocument.create(
            raw_input="使用者的原始輸入",
            ...
        )
        doc.save()  # 寫入冷儲存
        payload = doc.to_empath()  # 給共情者的讀取格式
    """

    session_id: str
    timestamp: str
    intent_frame: IntentFrame
    council_outputs: dict[str, LogicianOutput | CreatorOutput | SafetyOutput]
    tension_metrics: TensionMetrics
    legal_profile: LegalProfile
    lifecycle: Lifecycle
    trajectory_digest: TrajectoryDigest = field(default_factory=TrajectoryDigest)

    @classmethod
    def create(
        cls,
        raw_input: str,
        reconstructed_intent: str = "",
        declarative_goal: str = "",
        verification_loop: str = "",
    ) -> "ShadowDocument":
        """建立新的影子文件（初始化空白狀態）"""
        return cls(
            session_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            intent_frame=IntentFrame(
                raw_input=raw_input,
                reconstructed_intent=reconstructed_intent,
                declarative_goal=declarative_goal,
                verification_loop=verification_loop,
            ),
            council_outputs={},
            tension_metrics=TensionMetrics(
                semantic_distance=0.0,
                logical_conflict_rate=0.0,
                routing_decision=RoutingDecision.FAST_PATH,
                output_mode=OutputMode.SINGLE_TRACK,
            ),
            legal_profile=LegalProfile(
                applicable_laws=[],
                gap_detected=False,
                social_value_matrix_triggered=False,
                judicial_precedents=[],
            ),
            lifecycle=Lifecycle(),
            trajectory_digest=TrajectoryDigest(),
        )

    def to_dict(self) -> dict:
        """序列化為 JSON 可存格式（Python 原生 dict）"""
        import dataclasses

        def _convert(obj):
            if dataclasses.is_dataclass(obj):
                return {k: _convert(v) for k, v in dataclasses.asdict(obj).items()}
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, list):
                return [_convert(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items()}
            return obj

        return _convert(self)

    def to_empath(self) -> dict:
        """
        給共情者的摘要格式（不含 lifecycle 細節）
        共情者讀取此格式進行最終整合
        """
        return {
            "session_id": self.session_id,
            "intent_frame": {
                "declarative_goal": self.intent_frame.declarative_goal,
                "verification_loop": self.intent_frame.verification_loop,
            },
            "tension": {
                "semantic_distance": self.tension_metrics.semantic_distance,
                "logical_conflict_rate": self.tension_metrics.logical_conflict_rate,
                "output_mode": self.tension_metrics.output_mode.value,
            },
            "logician_summary": (
                self.council_outputs.get("logician", {}).summary
                if hasattr(self.council_outputs.get("logician", None), "summary")
                else None
            ),
            "creator_summary": (
                self.council_outputs.get("creator", {}).summary
                if hasattr(self.council_outputs.get("creator", None), "summary")
                else None
            ),
            "safety_verdict": (
                self.council_outputs.get("safety", None).verdict.value
                if self.council_outputs.get("safety")
                else None
            ),
            "legal_gap": self.legal_profile.gap_detected,
            "trajectory": {
                "step_count": self.trajectory_digest.step_count,
                "key_decisions": self.trajectory_digest.key_decisions,
                "compressed_summary": self.trajectory_digest.compressed_summary,
            },
        }

    def save(self, cold_storage_dir: str = "memory/yuhun_shadows") -> str:
        """
        寫入冷儲存
        Returns: archive_id
        """
        import json
        from pathlib import Path

        path = Path(cold_storage_dir)
        path.mkdir(parents=True, exist_ok=True)

        filename = path / f"{self.lifecycle.archive_id}.json"
        filename.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.lifecycle.cold_storage_archived = True
        return self.lifecycle.archive_id


# ─────────────────────────────────────────────
# 快速測試
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json

    doc = ShadowDocument.create(
        raw_input="這個 AI 架構是否存在法律漏洞？",
        reconstructed_intent="使用者想了解在現行法律框架下，AI 多代理人系統可能面臨的法律責任疏漏與合規風險",
        declarative_goal="提供可操作的法律風險評估，識別具體漏洞，並說明應對策略",
        verification_loop="若輸出能讓法學背景的人立即識別出主要合規風險點，則視為成功",
    )

    # 模擬填入議會數據
    doc.tension_metrics.semantic_distance = 0.82
    doc.tension_metrics.logical_conflict_rate = 0.91
    doc.tension_metrics.routing_decision = RoutingDecision.COUNCIL_PATH
    doc.tension_metrics.output_mode = OutputMode.DUAL_TRACK
    doc.legal_profile.gap_detected = True

    print("=== Shadow Document ===")
    print(json.dumps(doc.to_dict(), ensure_ascii=False, indent=2)[:800], "...")
    print("\n=== Empath Summary ===")
    print(json.dumps(doc.to_empath(), ensure_ascii=False, indent=2))
