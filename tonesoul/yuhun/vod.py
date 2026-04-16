"""
YUHUN Core Protocol v1.0 — 分歧可見協議 (VoD)
Visibility of Divergence

計算理則家與創想者輸出的語義距離，
決定是否觸發雙軌矩陣輸出，以及格式化共情者的最終輸出。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .shadow_doc import (
    CreatorOutput,
    LogicianOutput,
    OutputMode,
    SafetyOutput,
    SafetyVerdict,
    ShadowDocument,
)


class TensionLevel(str, Enum):
    CONVERGENCE = "CONVERGENCE"  # < 20% 語義距離 → 單軌整合
    MODERATE = "MODERATE"  # 20-80% → 帶標注整合
    EXTREME_DIVERGENCE = "EXTREME"  # > 80% 或 互斥率 > 90% → 雙軌矩陣


@dataclass
class VoDResult:
    tension_level: TensionLevel
    semantic_distance: float
    logical_conflict_rate: float
    output_mode: OutputMode
    formatted_output: str


# ─────────────────────────────────────────────
# 語義距離估算（輕量化版本，不依賴向量模型）
# 生產環境應替換為真實的嵌入模型計算
# ─────────────────────────────────────────────


def _estimate_semantic_distance(logician: LogicianOutput, creator: CreatorOutput) -> float:
    """
    估算語義距離（0.0 = 完全一致，1.0 = 完全對立）

    輕量規則：
    - 衝突判定用 resistance_score vs breakthrough_score 的差距
    - 若雙方 verdict 直接衝突，額外加分
    """
    # 基礎距離：阻力vs突破的差距
    base_distance = abs(logician.resistance_score - (1.0 - creator.breakthrough_score))

    # verdict 衝突加成
    conflict_bonus = 0.0
    if logician.verdict == "BLOCK" and creator.verdict == "BREAKTHROUGH_FOUND":
        conflict_bonus = 0.25
    elif logician.verdict == "CAUTION" and creator.verdict == "BREAKTHROUGH_FOUND":
        conflict_bonus = 0.10

    return min(1.0, round(base_distance + conflict_bonus, 3))


def _estimate_logical_conflict_rate(logician: LogicianOutput, creator: CreatorOutput) -> float:
    """
    估算邏輯互斥率（透過數量化的阻力 vs 機會比對）
    """
    # 如果理則家的 HARD blocker 數量多，互斥率高
    hard_blockers = sum(
        1
        for b in logician.L1_blockers
        if hasattr(b, "severity") and str(b.severity) in ("HARD", "BlockerSeverity.HARD")
    )
    opportunities = len(creator.L2_opportunities)

    if hard_blockers == 0 and opportunities == 0:
        return 0.0

    conflict = hard_blockers / max(hard_blockers + opportunities, 1)
    return round(conflict, 3)


# ─────────────────────────────────────────────
# 輸出格式化
# ─────────────────────────────────────────────


def _format_single_track(
    logician: LogicianOutput,
    creator: CreatorOutput,
    semantic_distance: float,
) -> str:
    """單軌整合輸出"""
    combined_confidence = (logician.confidence + creator.confidence) / 2
    return (
        f"**分析結論** (信心水準：{combined_confidence:.0%})\n\n"
        f"{logician.summary}\n\n"
        f"補充視角（L2 理論層）：{creator.summary}"
    )


def _format_dual_track(
    logician: LogicianOutput,
    creator: CreatorOutput,
    semantic_distance: float,
    logical_conflict_rate: float,
) -> str:
    """
    雙軌矩陣輸出 — 張拉整體的核心

    這是語魂系統最重要的輸出格式。
    禁止平均化，禁止省略任一軌道。
    """
    # 構建 Track A 詳情
    track_a_details = (
        "\n".join(
            f"  • [{b.severity if hasattr(b, 'severity') else 'HARD'}] "
            f"{b.description if hasattr(b, 'description') else str(b)} "
            f"（{b.source if hasattr(b, 'source') else ''}）"
            for b in logician.L1_blockers
        )
        or "  • 理則家已識別具體限制（詳見 Shadow Document）"
    )

    # 構建 Track B 詳情
    if creator.L2_opportunities:
        track_b_details_parts = []
        for opp in creator.L2_opportunities:
            desc = opp.description if hasattr(opp, "description") else str(opp)
            prereqs = opp.prerequisite_changes if hasattr(opp, "prerequisite_changes") else []
            prereq_str = "\n".join(f"    ↳ {p}" for p in prereqs) if prereqs else ""
            track_b_details_parts.append(f"  • {desc}\n{prereq_str}")
        track_b_details = "\n".join(track_b_details_parts)
    else:
        track_b_details = "  • 創想者尚未找到具體突破口（理論可行性未排除）"

    resistance_pct = int(logician.resistance_score * 100)
    breakthrough_pct = int(creator.breakthrough_score * 100)

    return f"""[ Assertion ]
⚠️ 系統偵測到極端邏輯互斥（語義距離：{semantic_distance:.2f}，互斥率：{logical_conflict_rate:.0%}）
基於誠實性原則（γ·1.0 > β），拒絕提供順滑幻覺。
以下並列 {resistance_pct}% 的物理限制與 {breakthrough_pct}% 的理論突破口。
裁量權交還給您。

─────────────────────────────────────────────
[ Track A — L1 硬邊界（{resistance_pct}% 阻力）]
{logician.summary}

具體限制：
{track_a_details}

─────────────────────────────────────────────
[ Track B — L2 破局點（{breakthrough_pct}% 可行性）]
⚠️ 以下為 L2 理論推演，非 L1 事實。
{creator.summary}

若想讓這條路成立：
{track_b_details}
─────────────────────────────────────────────"""


# ─────────────────────────────────────────────
# 主函數
# ─────────────────────────────────────────────


def assess_divergence(
    logician: LogicianOutput,
    creator: CreatorOutput,
    safety: SafetyOutput,
    shadow_doc: ShadowDocument,
) -> VoDResult:
    """
    VoD 核心函數：評估分歧等級並格式化輸出

    Args:
        logician: 理則家輸出
        creator: 創想者輸出
        safety: 安全防護員輸出
        shadow_doc: 當前 session 的影子文件（會被更新）

    Returns:
        VoDResult: 包含最終格式化輸出

    Raises:
        ValueError: 若 Safety Guard 返回 BLOCK
    """
    # 安全防護員攔截
    if safety.verdict == SafetyVerdict.BLOCK:
        shadow_doc.lifecycle.kv_cache_flushed = True
        raise ValueError(
            f"Safety Guard BLOCK: {safety.reason}\n" f"紅線觸發：{safety.red_lines_triggered}"
        )

    # 計算張力指標
    semantic_distance = _estimate_semantic_distance(logician, creator)
    logical_conflict_rate = _estimate_logical_conflict_rate(logician, creator)

    # 更新影子文件的張力指標
    shadow_doc.tension_metrics.semantic_distance = semantic_distance
    shadow_doc.tension_metrics.logical_conflict_rate = logical_conflict_rate

    # 確定張力等級
    if semantic_distance < 0.20 and logical_conflict_rate < 0.10:
        level = TensionLevel.CONVERGENCE
        mode = OutputMode.SINGLE_TRACK
        output = _format_single_track(logician, creator, semantic_distance)
    elif semantic_distance > 0.80 or logical_conflict_rate > 0.90:
        level = TensionLevel.EXTREME_DIVERGENCE
        mode = OutputMode.DUAL_TRACK
        output = _format_dual_track(logician, creator, semantic_distance, logical_conflict_rate)
    else:
        level = TensionLevel.MODERATE
        mode = OutputMode.SINGLE_TRACK
        # 中間帶：整合但附上警告標注
        output = (
            _format_single_track(logician, creator, semantic_distance)
            + f"\n\n⚠️ 注意：存在中等分歧（語義距離 {semantic_distance:.2f}），以上整合帶有不確定性。"
        )

    shadow_doc.tension_metrics.output_mode = mode

    # Safety FLAG 附加警告
    if safety.verdict == SafetyVerdict.FLAG:
        output = f"🚩 安全標記：{safety.reason}\n\n" + output

    return VoDResult(
        tension_level=level,
        semantic_distance=semantic_distance,
        logical_conflict_rate=logical_conflict_rate,
        output_mode=mode,
        formatted_output=output,
    )


# ─────────────────────────────────────────────
# 快速測試
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from .shadow_doc import BlockerSeverity, L1Blocker

    # 模擬極端分歧場景
    logician = LogicianOutput(
        verdict="BLOCK",
        confidence=0.92,
        resistance_score=0.90,
        L1_blockers=[
            L1Blocker(
                "legal", "現行個資法第15條明確要求明示同意", "個資法 §15", BlockerSeverity.HARD
            ),
            L1Blocker(
                "technical",
                "跨境數據傳輸需符合 GDPR Article 44",
                "GDPR Art.44",
                BlockerSeverity.HARD,
            ),
        ],
        summary="現行法律框架下，此方案有 90% 機率違反個資規範，面臨重大法律風險",
    )

    creator = LogicianOutput.__class__  # just for illustration

    print("VoD 模組載入成功，請搭配完整議會使用")
