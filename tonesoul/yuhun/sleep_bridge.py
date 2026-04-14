"""
YUHUN Core Protocol v1.0 — WorldSense → DreamEngine 橋接器
Sleep Period Bridge

功能：把 WorldSense.dream_candidates() 的感知資料
轉化為 DreamEngine 可消化的 environment_stimuli 格式，
讓清醒期累積的「高漂移 + 高張力時刻」成為睡眠期的做夢輸入。

位置：L6 Memory & Continuity 層（連接 L2 感知層和 L6 夢境循環）

設計原則：
  - 不修改 DreamEngine（開閉原則）
  - WorldSense 的輸出是 advisory，轉換後加上 yuhun 標籤以示來源
  - 每個 DreamCandidate 對應一條 environment_stimulus 記錄
  - priority_score > 0.5 才注入（防止雜訊）
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tonesoul.dream_engine import DreamEngine
    from tonesoul.yuhun.world_sense import DreamCandidate, WorldSense


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ─────────────────────────────────────────────
# 轉換：DreamCandidate → environment_stimulus payload
# ─────────────────────────────────────────────


def candidate_to_stimulus(candidate: "DreamCandidate", *, session_id: str = "") -> dict[str, Any]:
    """
    把 WorldSense.DreamCandidate 轉化為 DreamEngine 的 stimulus payload 格式

    DreamEngine 期待的 payload 欄位（來自 _build_collision / _priority_score）：
      - topic          (str)   — 主題，用於 query_terms
      - summary        (str)   — 摘要，用於 LLM reflection
      - relevance_score (float) — 0.0-1.0
      - novelty_score   (float) — 0.0-1.0
      - tags           (list)  — 標籤，影響 priority_score
      - source_url     (str)   — 追溯來源

    WorldSense.DreamCandidate 的欄位：
      - step, reason, drift_at_moment, tension_at_moment
      - jump_signal, priority, type
    """
    # 從候選類型推導 topic
    type_label = {
        "high_drift": "語義漂移事件 — 系統偏離本體中心",
        "lockdown_event": "奇點鎖定事件 — 推論收斂/鏈斷裂",
        "high_tension": "高張力分歧事件 — 議會極端分歧",
    }.get(candidate.type, "YUHUN 感知事件")

    topic = f"[Step {candidate.step}] {type_label}: {candidate.reason}"

    # 從張力值和漂移值推導 relevance / novelty
    # relevance = 漂移值（越偏離家，越值得重新思考）
    # novelty   = 張力值（越緊張，越有新知識空間）
    relevance = round(min(1.0, candidate.drift_at_moment), 4)
    novelty = round(min(1.0, candidate.tension_at_moment), 4)

    # 標籤集
    tags = ["yuhun", "world_sense", candidate.type, f"step_{candidate.step}"]
    if candidate.jump_signal.get("triggered"):
        tags.append("seabed_lockdown")
    if candidate.jump_signal.get("self_reference", 0) > 0.6:
        tags.append("inbreeding_risk")

    summary = (
        f"YUHUN WorldSense 捕捉到的高優先級事件（priority={candidate.priority:.3f}）。\n"
        f"類型：{candidate.type} | 漂移：{candidate.drift_at_moment:.3f} | "
        f"張力：{candidate.tension_at_moment:.3f}\n"
        f"觸發原因：{candidate.reason}\n"
        f"JumpMonitor 狀態：觸發={candidate.jump_signal.get('triggered')} | "
        f"自我引用率={candidate.jump_signal.get('self_reference', 0):.3f} | "
        f"鏈完整度={candidate.jump_signal.get('chain_integrity', 1.0):.3f}\n"
        f"做夢任務：在無時間壓力的環境中重新推演此時刻，尋找清醒期沒有時間找的第三條路。"
    )

    return {
        "type": "yuhun_world_sense_stimulus",
        "timestamp": _utcnow_iso(),
        "topic": topic,
        "summary": summary,
        "source_url": f"yuhun://world_sense/step/{candidate.step}",
        "relevance_score": relevance,
        "novelty_score": novelty,
        "tags": tags,
        "priority_score": round(candidate.priority, 4),
        "yuhun_metadata": {
            "step": candidate.step,
            "candidate_type": candidate.type,
            "drift_at_moment": candidate.drift_at_moment,
            "tension_at_moment": candidate.tension_at_moment,
            "jump_signal": candidate.jump_signal,
            "session_id": session_id,
        },
        "provenance": {
            "kind": "yuhun_world_sense",
            "session_id": session_id,
            "generated_at": _utcnow_iso(),
        },
        "decay_policy": {"policy": "adaptive"},
        "promotion_gate": {"status": "candidate", "source": "yuhun_world_sense"},
    }


# ─────────────────────────────────────────────
# 橋接函數
# ─────────────────────────────────────────────


@dataclass
class SleepBridgeResult:
    """睡眠期橋接結果"""

    injected_count: int  # 成功注入的刺激數
    skipped_count: int  # 優先級不足而跳過的候選數
    stimuli_ids: list[str]  # 注入成功的記錄 ID
    inbreeding_risk: str  # 近親繁殖風險等級
    stable_anchor_score: float  # 喚醒驗證錨點穩定分數
    advisory: str  # 給下游（DreamEngine）的建議


def inject_world_sense_to_dream(
    world_sense: "WorldSense",
    dream_engine: "DreamEngine",
    *,
    top_n: int = 5,
    min_priority: float = 0.5,
    session_id: str = "",
) -> SleepBridgeResult:
    """
    睡眠期橋接主函數

    步驟：
    1. 從 WorldSense 提取 dream_candidates（高漂移 + 高張力時刻）
    2. 過濾 priority < min_priority 的雜訊
    3. 轉換為 environment_stimulus 格式
    4. 寫入 DreamEngine 的 SoulDB（透過 write_gateway）
    5. 評估近親繁殖風險和穩定錨點
    6. 觸發 DreamEngine.run_cycle() 消化這些輸入

    Args:
        world_sense:  清醒期累積的感知實例
        dream_engine: DreamEngine 實例（需要 write_gateway 和 soul_db）
        top_n:        取前 N 個候選（預設 5）
        min_priority: 最低優先級閾值（預設 0.5）
        session_id:   當前 session 識別符，用於追溯

    Returns:
        SleepBridgeResult: 橋接結果摘要

    Raises:
        RuntimeError: 若 DreamEngine 沒有 write_gateway（非預期狀態）
    """
    if not hasattr(dream_engine, "write_gateway"):
        raise RuntimeError(
            "DreamEngine 缺少 write_gateway，無法注入 WorldSense 刺激。"
            "請確認 DreamEngine 已正確初始化。"
        )

    # 1. 提取候選
    all_candidates = world_sense.dream_candidates(top_n=top_n)

    # 2. 過濾
    valid_candidates = [c for c in all_candidates if c.priority >= min_priority]
    skipped = len(all_candidates) - len(valid_candidates)

    injected_ids: list[str] = []

    # 3. 轉換並注入
    for candidate in valid_candidates:
        payload = candidate_to_stimulus(candidate, session_id=session_id)
        try:
            from tonesoul.memory.soul_db import MemorySource

            record_id = dream_engine.write_gateway.write_payload(MemorySource.CUSTOM, payload)
            injected_ids.append(record_id)
        except Exception as e:
            # 注入單一失敗不阻斷整體流程（graceful degradation）
            print(f"[SleepBridge] Warning: 注入 step {candidate.step} 失敗：{e}")

    # 4. 評估感知狀態
    risk = world_sense.inbreeding_risk()
    anchors = world_sense.stable_anchors()

    # 5. 組建建議
    advisory_parts = []
    if risk.requires_external_anchor:
        advisory_parts.append(
            f"⚠️ 近親繁殖風險={risk.risk_level}：DreamEngine 反射前必須引入外部 L1 事實對照"
        )
    if anchors.stability_score < 0.5:
        advisory_parts.append(f"穩定性偏低（{anchors.stability_score:.0%}）：喚醒驗證標準應提高")
    if not advisory_parts:
        advisory_parts.append("系統狀態正常，可安全執行 DreamEngine.run_cycle()")

    return SleepBridgeResult(
        injected_count=len(injected_ids),
        skipped_count=skipped,
        stimuli_ids=injected_ids,
        inbreeding_risk=risk.risk_level,
        stable_anchor_score=anchors.stability_score,
        advisory=" | ".join(advisory_parts),
    )


# ─────────────────────────────────────────────
# 快速測試（不依賴真實 DreamEngine）
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent.parent))

    from tonesoul.yuhun.world_sense import DreamCandidate, WorldSense

    # 模擬一個有 3 個高漂移事件的 WorldSense session
    ws = WorldSense(home_vector={"deltaT": 0.5, "deltaS": 0.6, "deltaR": 0.4})

    scenarios = [
        ({"deltaT": 0.5, "deltaS": 0.6, "deltaR": 0.4}, 0.1, True),
        ({"deltaT": 0.9, "deltaS": 0.1, "deltaR": 0.9}, 0.92, False),  # 危機
        ({"deltaT": 0.8, "deltaS": 0.2, "deltaR": 0.8}, 0.85, True),  # 高張力
        ({"deltaT": 0.5, "deltaS": 0.6, "deltaR": 0.4}, 0.2, True),
    ]
    for vec, tension, trace in scenarios:
        ws.observe(semantic_vector=vec, tension_total=tension, has_echo_trace=trace)

    candidates = ws.dream_candidates(top_n=5)
    print("=== 做夢候選 → Stimulus 轉換 ===\n")
    for c in candidates:
        payload = candidate_to_stimulus(c, session_id="test-session-001")
        print(f"Step {c.step} [{c.type}] priority={c.priority:.3f}")
        print(f"  topic: {payload['topic'][:80]}...")
        print(
            f"  relevance={payload['relevance_score']:.3f} novelty={payload['novelty_score']:.3f}"
        )
        print(f"  tags: {payload['tags']}")
        print()

    print("=== SleepBridge (Mock — without real DreamEngine) ===")
    print(f"近親繁殖風險：{ws.inbreeding_risk().risk_level}")
    print(f"穩定錨點分數：{ws.stable_anchors().stability_score:.0%}")
    print(f"可注入候選：{len([c for c in candidates if c.priority >= 0.5])} / {len(candidates)}")
