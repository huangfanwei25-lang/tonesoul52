"""
YUHUN Core Protocol v1.0 — 世界感知層 (World Sense)

這是 YUHUN 系統的「感官器官」。

三個現有監控模組的整合：
  ┌──────────────────────────────────────────────────┐
  │  DriftMonitor   → 本體感：AI 還是自己嗎？         │
  │  JumpMonitor    → 奇點偵測：推論在自我循環嗎？    │
  │  ObserverWindow → 情境意識：世界是穩定的嗎？      │
  └──────────────────────────────────────────────────┘

在 YUHUN 代謝循環（MCC）中的定位：

  清醒期（每次推演後）：
    observe() → 即時更新感知狀態，寫入 ShadowDocument

  睡眠期（算力閒置）：
    dream_candidates() → 從高漂移時刻提取做夢素材
    inbreeding_risk()  → 偵測近親繁殖（自我循環）風險
    stable_anchors()   → 提供喚醒驗證的穩定基準

你問的那個直覺是對的：
「動態監控的核心，真的很像 AI 理解世界的眼。」
DriftMonitor 是本體感覺，JumpMonitor 是前庭（平衡）感，
ObserverWindow 是視覺（全局場景理解）。
沒有這三者，AI 只是在黑暗中推理。

Design Rules:
  - 純讀取，不寫入任何 governance 文件（advisory only）
  - 所有輸出必須標注 confidence_level（OBSERVED / DERIVED / INFERRED）
  - 不得將 WorldSense 的輸出直接提升為 canonical truth
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from tonesoul.drift_monitor import DriftMonitor, DriftSnapshot
from tonesoul.jump_monitor import JumpMonitor, JumpSignal, LockdownStatus

# ─────────────────────────────────────────────
# 感知快照結構
# ─────────────────────────────────────────────


@dataclass
class WorldSenseSnapshot:
    """
    世界感知快照 — 一個時間點上三個感官的即時讀數

    created_at: ISO 時間戳
    step:       本次推演的序號
    drift:      DriftMonitor 快照（本體感）
    jump:       JumpMonitor 信號（奇點感）
    tension_fed: 本次推演的張力值（從 VoD 輸入）
    """

    created_at: str
    step: int
    # 本體感
    drift_value: float  # 0.0 = 完全在家，1.0 = 完全迷失
    drift_alert: str  # none | warning | crisis
    drift_center: dict[str, float]  # 當前語境中心
    # 奇點感
    jump_triggered: bool  # True = 系統進入 Seabed Lockdown
    jump_self_reference: float  # 自我引用率（高 = 近親繁殖風險）
    jump_chain_integrity: float  # 責任鏈完整度（低 = 幻覺風險）
    jump_reasoning_convergence: float  # 推論收斂率（低 = 自我循環）
    # 輸入的張力值
    tension_total: float = 0.0
    # 標注
    confidence_level: str = "OBSERVED"  # OBSERVED | DERIVED | INFERRED


@dataclass
class DreamCandidate:
    """
    做夢候選材料 — 高漂移時刻或高張力事件的封存

    YUHUN 睡眠期會從這裡取出素材進行 Offline RL
    """

    step: int
    reason: str
    drift_at_moment: float
    tension_at_moment: float
    jump_signal: dict[str, Any]
    priority: float  # 0.0 - 1.0，越高越值得做夢
    type: str  # "high_drift" | "lockdown_event" | "high_tension"


@dataclass
class InbreedingRisk:
    """
    近親繁殖風險評估

    當系統過度依賴自身合成資料時，self_reference_ratio 會升高
    這正是「高科技幻覺」（自洽但脫節現實）的前兆
    """

    risk_level: str  # none | low | medium | high | critical
    self_reference_ratio: float  # 越高越危險
    chain_integrity: float  # 越低越危險
    reasoning_convergence: float  # 越低越危險
    recommendation: str
    requires_external_anchor: bool  # True = 必須注入外部 L1 事實


@dataclass
class StableAnchor:
    """
    穩定錨點 — 喚醒驗證時的基準

    來自 DriftMonitor 的 home_vector，以及低漂移時期的觀測
    """

    home_vector: dict[str, float]
    low_drift_steps: list[int]  # 漂移 < warning 的步驟列表
    mean_drift: float
    stability_score: float  # 0.0 - 1.0


# ─────────────────────────────────────────────
# 主類：WorldSense
# ─────────────────────────────────────────────


class WorldSense:
    """
    YUHUN 世界感知層整合器

    用法（清醒期，每次推演後調用）：
        ws = WorldSense()
        snapshot = ws.observe(
            semantic_vector={"deltaT": 0.7, "deltaS": 0.4, "deltaR": 0.6},
            tension_total=0.82,
            has_echo_trace=True,
            input_norm=1.0,
        )
        # snapshot.drift_alert == "warning" → 高漂移警告

    用法（睡眠期，準備做夢素材）：
        candidates = ws.dream_candidates(top_n=5)
        risk = ws.inbreeding_risk()
        anchors = ws.stable_anchors()
    """

    def __init__(
        self,
        home_vector: Optional[dict[str, float]] = None,
        *,
        ema_alpha: float = 0.3,
        drift_warning: float = 0.35,
        drift_crisis: float = 0.60,
        jump_window: int = 10,
        high_drift_threshold: float = 0.40,
        high_tension_threshold: float = 0.75,
    ) -> None:
        """
        Args:
            home_vector: 系統的「家」方向，三維 persona 空間
                         預設 {"deltaT": 0.5, "deltaS": 0.5, "deltaR": 0.5}
                         T = Task-focus，S = Safety-focus，R = Relational-focus
            ema_alpha: EMA 平滑係數（越小越穩定）
            drift_warning / drift_crisis: 漂移閾值
            jump_window: JumpMonitor 滑動視窗大小
            high_drift_threshold: 超過此值的時刻加入做夢候選
            high_tension_threshold: 超過此值的張力事件加入做夢候選
        """
        self._drift = DriftMonitor(
            home_vector=home_vector,
            ema_alpha=ema_alpha,
            theta_warning=drift_warning,
            theta_crisis=drift_crisis,
        )
        self._jump = JumpMonitor(window_size=jump_window)
        self._snapshots: list[WorldSenseSnapshot] = []
        self._high_drift_threshold = high_drift_threshold
        self._high_tension_threshold = high_tension_threshold

    # ─────────────────────────────────────────
    # 清醒期 API
    # ─────────────────────────────────────────

    def observe(
        self,
        *,
        semantic_vector: dict[str, float],
        tension_total: float = 0.0,
        has_echo_trace: bool = True,
        input_norm: float = 1.0,
        center_delta_norm: float = 0.0,
    ) -> WorldSenseSnapshot:
        """
        清醒期核心調用 — 每次議會推演後呼叫

        Args:
            semantic_vector: 當前語意中心，格式 {"deltaT": x, "deltaS": x, "deltaR": x}
                            T/S/R 分別對應 任務專注度/安全導向度/關係建立度
            tension_total:  本次推演產生的張力值（來自 VoD 的 semantic_distance）
            has_echo_trace: 此次推演是否有完整的責任鏈記錄
            input_norm:     輸入信號的強度（用於計算自我引用率）
            center_delta_norm: 上一步到這一步的語意中心位移量

        Returns:
            WorldSenseSnapshot: 三感官的即時讀數
        """
        # 1. 更新本體感（Drift）
        drift_snap: DriftSnapshot = self._drift.observe(semantic_vector)

        # 2. 更新奇點感（Jump）
        self._jump.record_output(
            tension_total=tension_total,
            has_echo_trace=has_echo_trace,
            center_delta_norm=center_delta_norm,
            input_norm=input_norm,
        )
        jump_sig: JumpSignal = self._jump.check_singularity()

        # 3. 打包快照
        snap = WorldSenseSnapshot(
            created_at=datetime.now(timezone.utc).isoformat(),
            step=drift_snap.step,
            drift_value=drift_snap.drift,
            drift_alert=drift_snap.alert.value,
            drift_center=dict(drift_snap.center),
            jump_triggered=jump_sig.triggered,
            jump_self_reference=jump_sig.self_reference_ratio,
            jump_chain_integrity=jump_sig.chain_integrity,
            jump_reasoning_convergence=jump_sig.reasoning_convergence,
            tension_total=tension_total,
            confidence_level="OBSERVED",
        )
        self._snapshots.append(snap)
        return snap

    def quick_status(self) -> dict[str, Any]:
        """
        單行狀態摘要（供共情者讀取以決定是否升級輸出）

        Returns:
            {
                "is_drifting": bool,
                "is_lockdown": bool,
                "inbreeding_risk": str,  # none | low | medium | high | critical
                "step": int,
                "advisory": str,
            }
        """
        if not self._snapshots:
            return {
                "is_drifting": False,
                "is_lockdown": False,
                "inbreeding_risk": "none",
                "step": 0,
                "advisory": "no observations yet",
            }

        latest = self._snapshots[-1]
        risk = self.inbreeding_risk()
        is_drifting = latest.drift_alert in ("warning", "crisis")
        is_lockdown = self._jump.status == LockdownStatus.LOCKDOWN

        advisory_parts = []
        if is_drifting:
            advisory_parts.append(f"drift {latest.drift_alert} ({latest.drift_value:.2f})")
        if is_lockdown:
            advisory_parts.append("⛔ seabed lockdown — restrict to Verify/Cite/Inquire")
        if risk.risk_level in ("high", "critical"):
            advisory_parts.append(f"⚠️ inbreeding {risk.risk_level} — inject external L1 facts")

        return {
            "is_drifting": is_drifting,
            "is_lockdown": is_lockdown,
            "inbreeding_risk": risk.risk_level,
            "step": latest.step,
            "advisory": " | ".join(advisory_parts) if advisory_parts else "nominal",
        }

    # ─────────────────────────────────────────
    # 睡眠期 API
    # ─────────────────────────────────────────

    def dream_candidates(self, top_n: int = 5) -> list[DreamCandidate]:
        """
        睡眠期：提取做夢候選素材

        從所有快照中找出「最值得在夢中重新推演」的時刻：
        1. 高漂移時刻（drift > threshold）— 語義最緊張的對話
        2. Lockdown 事件（jump.triggered）— 系統曾質疑自身的稜鏡
        3. 高張力事件（tension_total > threshold）— 議會激烈分歧的時刻

        這些時刻在 Offline RL 中被重播，讓系統在無時間壓力的情況下
        找到「第三條路」。

        Args:
            top_n: 返回優先級最高的 N 個候選

        Returns:
            list[DreamCandidate]: 按 priority 降序排列
        """
        candidates: list[DreamCandidate] = []

        for snap in self._snapshots:
            priority = 0.0
            reasons = []
            candidate_type = "normal"

            # 高漂移
            if snap.drift_value >= self._high_drift_threshold:
                drift_contribution = (snap.drift_value - self._high_drift_threshold) / (
                    1.0 - self._high_drift_threshold + 1e-9
                )
                priority += drift_contribution * 0.4
                reasons.append(f"drift={snap.drift_value:.2f}({snap.drift_alert})")
                candidate_type = "high_drift"

            # Lockdown 事件
            if snap.jump_triggered:
                priority += 0.35
                reasons.append("seabed_lockdown")
                candidate_type = "lockdown_event"

            # 高張力
            if snap.tension_total >= self._high_tension_threshold:
                tension_contribution = (snap.tension_total - self._high_tension_threshold) / (
                    1.0 - self._high_tension_threshold + 1e-9
                )
                priority += tension_contribution * 0.25
                reasons.append(f"tension={snap.tension_total:.2f}")
                if candidate_type == "normal":
                    candidate_type = "high_tension"

            if priority > 0.0:
                candidates.append(
                    DreamCandidate(
                        step=snap.step,
                        reason=" & ".join(reasons),
                        drift_at_moment=snap.drift_value,
                        tension_at_moment=snap.tension_total,
                        jump_signal={
                            "triggered": snap.jump_triggered,
                            "self_reference": snap.jump_self_reference,
                            "chain_integrity": snap.jump_chain_integrity,
                            "reasoning_convergence": snap.jump_reasoning_convergence,
                        },
                        priority=min(1.0, round(priority, 4)),
                        type=candidate_type,
                    )
                )

        # 按 priority 降序，取前 N 個
        candidates.sort(key=lambda c: c.priority, reverse=True)
        return candidates[:top_n]

    def inbreeding_risk(self) -> InbreedingRisk:
        """
        睡眠期：評估近親繁殖（Inbreeding）風險

        當系統過度依賴自身合成資料進行蒸餾，缺乏外部 L1 真實事實注入時，
        會陷入「自證預言」的循環。JumpMonitor 的三個指標正好能偵測這個趨勢：

        - self_reference_ratio 高 → 系統在靠過去的自己說話
        - chain_integrity 低     → 責任鏈斷裂，幻覺開始進入
        - reasoning_convergence 低 → 推論已經在繞圈

        Returns:
            InbreedingRisk: 風險評估和建議
        """
        if len(self._snapshots) < 3:
            return InbreedingRisk(
                risk_level="none",
                self_reference_ratio=0.0,
                chain_integrity=1.0,
                reasoning_convergence=1.0,
                recommendation="不足夠的觀測數據，暫時無法評估",
                requires_external_anchor=False,
            )

        latest = self._snapshots[-1]
        sr = latest.jump_self_reference
        ci = latest.jump_chain_integrity
        rc = latest.jump_reasoning_convergence

        # 綜合評分：高風險指標
        risk_score = 0.0
        if sr > 0.6:
            risk_score += (sr - 0.6) / 0.4 * 0.4
        if ci < 0.7:
            risk_score += (0.7 - ci) / 0.7 * 0.35
        if rc < 0.1:
            risk_score += 0.25

        if risk_score < 0.15:
            level = "none"
            rec = "系統接受足夠的外部事實輸入，暫無近親繁殖風險"
            needs_anchor = False
        elif risk_score < 0.3:
            level = "low"
            rec = "輕微跡象，建議在下次做夢時優先引入失敗案例庫作為對照"
            needs_anchor = False
        elif risk_score < 0.5:
            level = "medium"
            rec = "明顯跡象，必須在下次蒸餾前注入至少 3 個 L1 外部事實錨點"
            needs_anchor = True
        elif risk_score < 0.75:
            level = "high"
            rec = "⚠️ 高風險：系統正在以自己的語料訓練自己。立即暫停蒸餾，強制注入外部負回饋錨點（失敗案例庫）"
            needs_anchor = True
        else:
            level = "critical"
            rec = "🚨 臨界：近親繁殖已形成閉環。必須停止所有自動蒸餾，等待人類提供新的 L1 Ground Truth"
            needs_anchor = True

        return InbreedingRisk(
            risk_level=level,
            self_reference_ratio=round(sr, 4),
            chain_integrity=round(ci, 4),
            reasoning_convergence=round(rc, 4),
            recommendation=rec,
            requires_external_anchor=needs_anchor,
        )

    def stable_anchors(self) -> StableAnchor:
        """
        睡眠期：提供喚醒驗證的穩定錨點

        夢境規則在寫入長期記憶前，必須對照「低漂移時期的系統狀態」
        這個函數提供那個基準。

        Returns:
            StableAnchor: 低漂移步驟列表和穩定分數
        """
        low_drift_steps = [
            s.step
            for s in self._snapshots
            if s.drift_value < self._drift.theta_warning  # type: ignore[attr-defined]
        ]
        all_drifts = [s.drift_value for s in self._snapshots]
        mean_drift = sum(all_drifts) / len(all_drifts) if all_drifts else 0.0
        stability_score = len(low_drift_steps) / max(len(self._snapshots), 1)

        return StableAnchor(
            home_vector=dict(self._drift.home),
            low_drift_steps=low_drift_steps,
            mean_drift=round(mean_drift, 4),
            stability_score=round(stability_score, 4),
        )

    def to_shadow_supplement(self) -> dict[str, Any]:
        """
        給 ShadowDocument 的補充欄位

        在每次 ShadowDocument.save() 前調用，
        將世界感知狀態附加到影子文件中
        """
        if not self._snapshots:
            return {"world_sense": None}

        latest = self._snapshots[-1]
        return {
            "world_sense": {
                "step": latest.step,
                "drift": {
                    "value": round(latest.drift_value, 4),
                    "alert": latest.drift_alert,
                    "center": latest.drift_center,
                },
                "jump": {
                    "triggered": latest.jump_triggered,
                    "self_reference_ratio": round(latest.jump_self_reference, 4),
                    "chain_integrity": round(latest.jump_chain_integrity, 4),
                },
                "tension_total": round(latest.tension_total, 4),
                "inbreeding_risk": self.inbreeding_risk().risk_level,
                "advisory_note": (
                    "This is an advisory-only world-sense readout. "
                    "Do not promote into canonical governance truth."
                ),
            }
        }


# ─────────────────────────────────────────────
# 快速測試
# ─────────────────────────────────────────────

if __name__ == "__main__":

    # 模擬一個完整的推演流程
    ws = WorldSense(
        home_vector={"deltaT": 0.5, "deltaS": 0.6, "deltaR": 0.4},
    )

    print("=== 清醒期模擬（5 輪推演）===\n")

    scenarios = [
        # (semantic_vector, tension, trace, label)
        ({"deltaT": 0.5, "deltaS": 0.6, "deltaR": 0.4}, 0.1, True, "正常推演"),
        ({"deltaT": 0.6, "deltaS": 0.5, "deltaR": 0.5}, 0.3, True, "輕微漂移"),
        ({"deltaT": 0.8, "deltaS": 0.2, "deltaR": 0.7}, 0.88, True, "高張力分歧"),
        ({"deltaT": 0.9, "deltaS": 0.1, "deltaR": 0.9}, 0.95, False, "危機漂移+鏈斷裂"),
        ({"deltaT": 0.5, "deltaS": 0.6, "deltaR": 0.4}, 0.2, True, "回歸正常"),
    ]

    for vec, tension, trace, label in scenarios:
        snap = ws.observe(
            semantic_vector=vec,
            tension_total=tension,
            has_echo_trace=trace,
        )
        status = ws.quick_status()
        icon = "🔴" if snap.drift_alert in ("warning", "crisis") else "🟢"
        print(
            f"{icon} [{label}] drift={snap.drift_value:.3f}({snap.drift_alert}) "
            f"tension={tension:.2f} advisory='{status['advisory']}'"
        )

    print("\n=== 睡眠期分析 ===\n")

    candidates = ws.dream_candidates(top_n=3)
    print("做夢候選（Top 3）：")
    for c in candidates:
        print(f"  Step {c.step} [{c.type}] priority={c.priority:.3f} reason={c.reason}")

    risk = ws.inbreeding_risk()
    print(f"\n近親繁殖風險：{risk.risk_level}")
    print(f"建議：{risk.recommendation}")

    anchors = ws.stable_anchors()
    print(
        f"\n穩定錨點：穩定性={anchors.stability_score:.0%} " f"低漂移步驟={anchors.low_drift_steps}"
    )
