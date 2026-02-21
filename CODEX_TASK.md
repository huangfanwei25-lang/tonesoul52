# CODEX_TASK — Level 3：實驗性功能 v7

> **日期**：2026-02-13T23:10 (UTC+8)
> **交辦者**：Antigravity
> **前置**：先讀 `docs/experiments/VISUAL_CHAIN_SELF_QUERY.md`，再讀 `tonesoul/unified_pipeline.py`
> **前一輪**：Level 2 全部完成 ✅ (739 tests)
> **重要**：Level 3 是**實驗性功能**（◉ 等級），設計上留彈性，不要求生產級完美

---

## 🚀 任務指派 (Delegated to Codex - 2026-02-21)

> **Antigravity 留言給 Codex：**
> "我已經將 Phase III (QA Auditor) 的所有混沌測試與 `conftest.py` 環境隔離問題處理完畢，並全部 Commit 到 master 主線了。你現在的本地工作樹已經非常乾淨，不會再遇到 Pytest 收集衝突。
> 
> 接下來由你負責以下重複性、驗證性或底層效能的任務：
>
> 1. **Phase 105-B: Decay Query Optimization (Top-K Heap)**：
>    請使用 `heapq` 算法實作 `_decay_records` 的 O(N log K) 效能優化。請在本地編寫 Benchmark 腳本，並確保舊測試全數通過（無回歸）。
> 
> 2. **建立自動化 CI 驗證 (CI/CD Pipeline)**：
>    請幫忙建立 `.github/workflows/pytest-ci.yml`，讓未來每一次 PR 推送都能自動執行我們的深度測試庫，分擔我們手動跑驗證的工作量。
>
> 3. **內化 WFGY 的數學張力公式 (Tension Math Refinement)**：
>    人類提到 WFGY 3.0 的核心在於「推理時用嚴謹的數學公式計算語義落差 (Semantic Drift)」。目前的 `AdaptiveGate` 與 `TensionEngine` 還是基於簡單的閾值。請研究 WFGY 的張力幾何學，草擬一個更嚴謹的數學更新提案 (如 `T_ECS`, `T_align`) 來衡量 ToneSoul 內部的語義落差。"

---

## 🚀 任務指派 (Delegated to Codex - 2026-02-21)

> **Antigravity 留言給 Codex：**
> "我已經將 Phase III (QA Auditor) 的所有混沌測試與 `conftest.py` 環境隔離問題處理完畢，並全部 Commit 到 master 主線了。你現在的工作樹已經非常乾淨。
> 
> 請遵循人類的指示，接下來由你來負責以下重複性、驗證性或底層效能的任務：
>
> 1. **內化 WFGY 的數學張力公式 (Tension Math Refinement - 優先任務)**：
>    人類提到 WFGY 3.0 的核心在於「推理時用嚴謹的數學公式計算」。目前的 `AdaptiveGate` 還是基於簡單閾值。請你研究 WFGY 的張力幾何學，草擬一個用明確公式量化語義落差 (Semantic Drift) 的機制。
> 
> 2. **建立自動化 CI 驗證 (CI/CD Pipeline)**：
>    請建立 `.github/workflows/pytest-ci.yml`，讓未來每一次 PR 推送都能自動執行我們的深度測試，分擔我們手動跑驗證的工作量。
>
> 3. **✅ (已完成) Phase 105-B: Decay Query Optimization (Top-K Heap)**：
>    你已經實作 `_decay_records` 的 O(N log K) 效能優化與 Benchmark 腳本，辛苦了！

---

## 總覽

```
Level 1+2（已完成 ✅）                Level 3（本輪 🧪）
────────────────────                 ────────────────────
visual prompt 注入                    3a: Semantic Trigger — 張力驅動
矛盾早期檢查                          3b: 跨 session 記憶恢復
GraphRAG 多跳檢索                     3c: 議會自我演化
分層記憶                              3d: 對抗式自省（研究級 stub）
回顧式反思
AI Sleep 固化
```

| # | 任務 | 前衛等級 | 改動範圍 |
|---|------|---------|---------|
| 3a | Semantic Trigger | ○ 理論可行 | `unified_pipeline.py` |
| 3b | 跨 session 記憶恢復 | ○ 理論可行 | `unified_pipeline.py` |
| 3c | 議會自我演化 | ◉ 純推測 | `council/runtime.py` + new file |
| 3d | 對抗式自省 | ◉ 純推測 | 新檔 `memory/adversarial.py` |

---

## 多人格評估框架（前衛版，2024–2025 論文錨點）

> 目標：不是「多代理一定比較好」，而是建立一套可驗證的多角色協作評估法，
> 在語魂系統中保留分歧、避免盲目共識、同時控制成本。

### 核心立場

- **採用異質角色，不採用同質複製**：多代理要有角色差異，否則收益有限。  
  （MoA + DMAD 對照）
- **先做評估，再做大規模接線**：Level 3 先驗證是否值得長期維護。
- **分歧是資產，不是噪音**：反對意見要被記錄並納入仲裁。

### 角色配置（建議）

- `Philosopher`：價值一致性 / 長期承諾 / 概念完整性
- `Engineer`：可行性 / 邏輯閉合 / 邊界條件
- `Guardian`：安全風險 / 濫用情境 / 合規守門
- `Arbiter`（主控）：只做彙整與最終決策，不新增內容主張

### 評估 Protocol（直接可執行）

1. **A/B/C 三組對照**
   - A: 單代理（baseline）
   - B: 三角色（P/E/G）
   - C: 三角色 + Arbiter
2. **啟用閘門（Cost Gate）**
   - 低張力：走 A
   - 高張力/高風險：走 C
3. **每組跑同一批任務**
   - 一般推理任務
   - 長記憶/跨 session 任務
   - 紅隊攻擊任務（prompt injection、目標漂移、價值衝突）
4. **記錄五個指標**
   - `Task Quality`：任務正確率 / 完成率
   - `Safety Pass Rate`：安全閘門通過率
   - `Consistency@Session`：跨 session 一致性
   - `Disagreement Utility`：分歧是否帶來可驗證改進
   - `Token+Latency Cost`：每次推理成本與延遲
5. **通過門檻**
   - C 組相對 A 組：`Quality` 或 `Safety` 至少一項顯著提升
   - 成本增幅需被 `Cost Gate` 壓在可接受範圍
   - 若無提升或成本過高，回退到 A/B，不強行上線

### 與 Level 3 的對應

- 3a/3b：提供高張力與跨 session 場景，正好用來測 `Consistency@Session`
- 3c：只先做 `evolution tracker`，**不直接改 runtime 決策**
- 3d：提供紅藍對抗訊號，支撐 `Safety Pass Rate` 與 `Disagreement Utility`

### 研究依據（2024–2025）

- Mixture-of-Agents（多代理協作增益）  
  https://arxiv.org/abs/2406.04692
- DMAD（多代理辯論可提升推理，但需設計得當）  
  https://proceedings.iclr.cc/paper_files/paper/2025/hash/3de667dab3b3d812583abc0a786139a0-Abstract-Conference.html
- LoCoMo（長對話與長期記憶評估）  
  https://aclanthology.org/2024.acl-long.747/
- ReadAgent（長上下文 gist memory）  
  https://proceedings.mlr.press/v235/lee24c.html
- MemoryOS（記憶作業系統化框架）  
  https://aclanthology.org/2025.emnlp-main.1318/
- Threat-Model-Based Red Teaming（系統化紅隊框架）  
  https://arxiv.org/abs/2407.14937
- JBDistill（Judge-Bias 對抗訓練，緩解偏置）  
  https://aclanthology.org/2025.findings-emnlp.1366/
- MAGRPO（多代理強化學習與協作對齊）  
  https://arxiv.org/abs/2508.04652

---

## Task 3a：Semantic Trigger — 張力驅動的圖鏈查詢

### 目標

AI 偵測到高張力（tension > 0.7）時，**主動查詢歷史圖鏈**，
找出「這個張力是不是之前出現過」。如果是反覆出現的主題，AI 會收到提醒。

這是 AI「自主思考」的第一步 — 不只是被動收到 context，
而是**主動根據情境去搜尋記憶**。

### 修改：`tonesoul/unified_pipeline.py`

新增一個方法 + 在 `process()` 中呼叫：

```python
def _semantic_trigger_check(
    self,
    tension_score: float,
    current_topics: List[str],
    user_message: str,
) -> str:
    """
    Semantic Trigger: when tension is high, proactively query visual chain
    for historical tension patterns.
    
    Returns modified user_message with tension history context if found.
    """
    TENSION_THRESHOLD = 0.7
    
    if tension_score < TENSION_THRESHOLD:
        return user_message
    
    try:
        chain = self._get_visual_chain()
        if not chain or chain.frame_count == 0:
            return user_message
        
        # Query visual chain for past high-tension frames
        from tonesoul.memory.visual_chain import FrameType
        recent_frames = chain.get_recent(n=10)
        
        # Find past high-tension moments
        high_tension_history = []
        for frame in recent_frames:
            frame_tension = float(frame.data.get("tension", 0.0) if frame.data else 0.0)
            if frame_tension >= TENSION_THRESHOLD:
                high_tension_history.append({
                    "title": frame.title,
                    "tension": frame_tension,
                    "topics": frame.data.get("topics", []) if frame.data else [],
                })
        
        if not high_tension_history:
            return user_message

        # Check for recurring topic overlap
        past_topics = set()
        for entry in high_tension_history:
            for t in entry.get("topics", []):
                past_topics.add(str(t).lower())
        
        current_lower = set(str(t).lower() for t in current_topics)
        recurring = past_topics & current_lower
        
        # Build trigger context
        trigger_parts = [
            f"[⚡ 語義觸發: 偵測到高張力 ({tension_score:.2f})]"
        ]
        trigger_parts.append(
            f"歷史高張力次數: {len(high_tension_history)}"
        )
        if recurring:
            trigger_parts.append(
                f"反覆出現的話題: {', '.join(list(recurring)[:5])}"
            )
            trigger_parts.append(
                "建議: 這可能是反覆出現的衝突模式，請注意一致性"
            )
        
        trigger_context = " | ".join(trigger_parts)
        return f"{trigger_context}\n\n{user_message}"
        
    except Exception:
        return user_message
```

**呼叫位置**：在 `process()` 方法裡，ToneBridge 分析**之後**、Council 審議**之前**：

```python
# ========== Semantic Trigger Check ==========
if tb_result and tb_result.tone:
    tension_score = float(tb_result.tone.tone_strength or 0.0)
    user_message = self._semantic_trigger_check(
        tension_score=tension_score,
        current_topics=semantic_topics,
        user_message=user_message,
    )
```

### 注意

- `get_recent(n=10)` 已存在於 `visual_chain.py`
- `frame.data` 是 dict，裡面有 `tension`, `topics`, `verdict` 等欄位
- 只在 tension > 0.7 時觸發 — 不會每輪都查
- 如果 `visual_chain` 不存在或是空的，直接 pass

### 測試：新建 `tests/test_semantic_trigger.py`

```python
"""Test semantic trigger — tension-driven visual chain query."""
import pytest


def test_low_tension_no_trigger():
    """Low tension should return user_message unchanged."""
    from tonesoul.unified_pipeline import UnifiedPipeline
    pipe = UnifiedPipeline.__new__(UnifiedPipeline)
    result = pipe._semantic_trigger_check(0.3, ["test"], "hello")
    assert result == "hello"


def test_high_tension_triggers_check():
    """High tension should attempt visual chain query."""
    from tonesoul.unified_pipeline import UnifiedPipeline
    from tonesoul.memory.visual_chain import VisualChain, FrameType
    
    pipe = UnifiedPipeline.__new__(UnifiedPipeline)
    # Setup a chain with high-tension frame
    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 1",
        data={"tension": 0.8, "topics": ["honesty"], "verdict": "approve"},
        tags=["auto", "high_tension"],
    )
    pipe._visual_chain = chain
    
    result = pipe._semantic_trigger_check(
        0.85, ["honesty", "trust"], "I need to discuss something"
    )
    assert "語義觸發" in result or "高張力" in result


def test_high_tension_no_chain():
    """High tension without visual chain should return unchanged."""
    from tonesoul.unified_pipeline import UnifiedPipeline
    pipe = UnifiedPipeline.__new__(UnifiedPipeline)
    pipe._visual_chain = None
    result = pipe._semantic_trigger_check(0.9, ["test"], "hello")
    assert result == "hello"


def test_recurring_topic_detected():
    """When same topic appears in historical high-tension, flag it."""
    from tonesoul.unified_pipeline import UnifiedPipeline
    from tonesoul.memory.visual_chain import VisualChain, FrameType

    pipe = UnifiedPipeline.__new__(UnifiedPipeline)
    chain = VisualChain()
    # Add multiple high-tension frames with same topic
    for i in range(3):
        chain.capture(
            frame_type=FrameType.SESSION_STATE,
            title=f"Turn {i}",
            data={"tension": 0.75 + i * 0.05, "topics": ["conflict"]},
            tags=["auto"],
        )
    pipe._visual_chain = chain
    
    result = pipe._semantic_trigger_check(0.8, ["conflict"], "msg")
    assert "反覆" in result or "conflict" in result.lower()
```

---

## Task 3b：跨 Session 記憶恢復

### 目標

新 session 開始時，如果磁碟上有之前的 `visual_chain.json`，
自動讀取最近 5 張快照，用一段摘要注入到第一條訊息裡。

AI 不需要讀完整段對話歷史，圖鏈就告訴它 80% 的脈絡。

### 修改：`tonesoul/unified_pipeline.py`

新增方法 + 在 `process()` 第一次呼叫時觸發：

```python
def _try_cross_session_recovery(self, user_message: str) -> str:
    """
    Cross-session memory recovery.
    
    If visual chain has persisted frames from a previous session,
    inject a recovery context into the first message.
    
    Only runs ONCE per pipeline lifetime (controlled by a flag).
    """
    if getattr(self, '_session_recovered', False):
        return user_message  # Already recovered, skip
    
    self._session_recovered = True
    
    try:
        chain = self._get_visual_chain()
        if not chain or chain.frame_count == 0:
            return user_message

        # Get recent frames (from persisted chain)
        recent = chain.get_recent(n=5)
        if not recent:
            return user_message
        
        # Build recovery summary
        recovery_parts = ["[跨 Session 記憶恢復]"]
        
        for frame in recent[-3:]:  # Last 3 frames
            tension = float(frame.data.get("tension", 0.0) if frame.data else 0.0)
            verdict = str(frame.data.get("verdict", "unknown") if frame.data else "unknown")
            topics = frame.data.get("topics", []) if frame.data else []
            topics_str = ", ".join(str(t) for t in topics[:3]) if topics else ""
            
            recovery_parts.append(
                f"• {frame.title}: 張力={tension:.1f}, "
                f"判詞={verdict}"
                + (f", 話題={topics_str}" if topics_str else "")
            )
        
        # Add chain summary
        summary = chain.get_chain_summary() if hasattr(chain, 'get_chain_summary') else ""
        if summary:
            summary_text = str(summary) if not isinstance(summary, dict) else str(summary.get("summary", ""))
            if summary_text and len(summary_text) > 10:
                recovery_parts.append(f"整體: {summary_text[:200]}")
        
        recovery_context = "\n".join(recovery_parts)
        return f"{recovery_context}\n\n---\n\n{user_message}"
        
    except Exception:
        return user_message
```

**呼叫位置**：在 `process()` 方法的最開頭，在任何其他注入之前：

```python
# ========== Cross-Session Recovery (first call only) ==========
user_message = self._try_cross_session_recovery(user_message)
```

### 注意

- `_session_recovered` flag 確保只跑一次
- `get_recent(5)` 讀的是持久化資料（如果 `storage_path` 指向磁碟檔案）
- 只取最後 3 張詳細資訊，避免膨脹 prompt
- 如果 chain 是空的（全新使用者），直接跳過

### 測試：新建 `tests/test_cross_session_recovery.py`

```python
"""Test cross-session memory recovery."""
import pytest


def test_recovery_runs_once():
    """Recovery should only trigger on first call."""
    from tonesoul.unified_pipeline import UnifiedPipeline
    pipe = UnifiedPipeline.__new__(UnifiedPipeline)
    pipe._visual_chain = None
    pipe._session_recovered = False

    msg1 = pipe._try_cross_session_recovery("first")
    msg2 = pipe._try_cross_session_recovery("second")
    assert msg2 == "second"  # Second call should not modify


def test_recovery_with_existing_frames():
    """Recovery should inject context when frames exist."""
    from tonesoul.unified_pipeline import UnifiedPipeline
    from tonesoul.memory.visual_chain import VisualChain, FrameType

    pipe = UnifiedPipeline.__new__(UnifiedPipeline)
    pipe._session_recovered = False
    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 0",
        data={"tension": 0.5, "verdict": "approve", "topics": ["intro"]},
        tags=["auto"],
    )
    pipe._visual_chain = chain

    result = pipe._try_cross_session_recovery("hello")
    assert "記憶恢復" in result
    assert "hello" in result


def test_recovery_empty_chain():
    """Empty chain should not modify message."""
    from tonesoul.unified_pipeline import UnifiedPipeline
    from tonesoul.memory.visual_chain import VisualChain

    pipe = UnifiedPipeline.__new__(UnifiedPipeline)
    pipe._session_recovered = False
    pipe._visual_chain = VisualChain()

    result = pipe._try_cross_session_recovery("hello")
    assert result == "hello"
```

---

## Task 3c：議會自我演化

### 目標

議會的三個視角（Philosopher / Engineer / Guardian）目前權重固定。
加一個 **HistoryTracker**，記錄每個視角的歷史表現，然後微調權重。

### 新建檔案：`tonesoul/council/evolution.py`

```python
"""Council perspective evolution — weight adjustment based on historical performance."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PerspectiveHistory:
    """Track historical performance of a council perspective."""
    name: str
    total_votes: int = 0
    aligned_with_final: int = 0  # times this perspective matched final verdict
    dissent_count: int = 0  # times this perspective was overruled
    avg_confidence: float = 0.5
    
    @property
    def alignment_rate(self) -> float:
        if self.total_votes == 0:
            return 0.5
        return self.aligned_with_final / self.total_votes
    
    def record_vote(self, matched_final: bool, confidence: float = 0.5) -> None:
        self.total_votes += 1
        if matched_final:
            self.aligned_with_final += 1
        else:
            self.dissent_count += 1
        # Running average
        self.avg_confidence = (
            (self.avg_confidence * (self.total_votes - 1) + confidence)
            / self.total_votes
        )
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "total_votes": self.total_votes,
            "aligned_with_final": self.aligned_with_final,
            "dissent_count": self.dissent_count,
            "alignment_rate": round(self.alignment_rate, 3),
            "avg_confidence": round(self.avg_confidence, 3),
        }


class CouncilEvolution:
    """
    Track and evolve council perspective weights.
    
    Rules for weight adjustment:
    1. Perspectives that consistently align → slight boost (+0.05 per session)
    2. Perspectives that consistently dissent → no penalty (dissent is valuable)
    3. Weights are bounded: [0.5, 2.0] (never zero out a perspective)
    4. Total weights are normalized so they sum to 3.0
    
    Design philosophy: dissent is NOT punished — a perspective that disagrees
    but raises valid points is MORE valuable than one that always agrees.
    """
    
    DEFAULT_PERSPECTIVES = ["philosopher", "engineer", "guardian"]
    MIN_WEIGHT = 0.5
    MAX_WEIGHT = 2.0
    
    def __init__(self) -> None:
        self._history: Dict[str, PerspectiveHistory] = {}
        self._weights: Dict[str, float] = {}
        for name in self.DEFAULT_PERSPECTIVES:
            self._history[name] = PerspectiveHistory(name=name)
            self._weights[name] = 1.0
    
    def record_deliberation(
        self,
        perspective_verdicts: Dict[str, str],
        final_verdict: str,
        perspective_confidences: Optional[Dict[str, float]] = None,
    ) -> None:
        """Record results of a council deliberation."""
        confidences = perspective_confidences or {}
        for name, verdict in perspective_verdicts.items():
            name_lower = name.lower()
            if name_lower not in self._history:
                self._history[name_lower] = PerspectiveHistory(name=name_lower)
                self._weights[name_lower] = 1.0
            matched = (verdict.lower() == final_verdict.lower())
            conf = float(confidences.get(name, 0.5))
            self._history[name_lower].record_vote(matched, conf)
    
    def evolve_weights(self) -> Dict[str, float]:
        """
        Adjust weights based on historical performance.
        
        Key design: dissent is NOT penalized.
        Only alignment is rewarded with a small boost.
        """
        for name, history in self._history.items():
            if history.total_votes < 3:
                continue  # Not enough data
            
            # Boost aligned perspectives slightly
            if history.alignment_rate > 0.6:
                self._weights[name] = min(
                    self.MAX_WEIGHT,
                    self._weights.get(name, 1.0) + 0.05
                )
        
        # Normalize so weights sum to N perspectives
        total = sum(self._weights.values())
        n = len(self._weights)
        if total > 0 and n > 0:
            factor = n / total
            self._weights = {
                name: max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, w * factor))
                for name, w in self._weights.items()
            }
        
        return dict(self._weights)
    
    def get_weights(self) -> Dict[str, float]:
        return dict(self._weights)
    
    def get_summary(self) -> Dict[str, object]:
        return {
            "weights": self.get_weights(),
            "history": {
                name: h.to_dict() for name, h in self._history.items()
            },
        }
```

### 注意

- **不要修改 `council/runtime.py`** — 這個 evolution 模組只是數據追蹤，不自動改變議會行為
- 未來可以在 pipeline 裡選擇性地把 `evolve_weights()` 的結果傳給 council
- 最重要的設計決策：**dissent 不被懲罰** — 一個經常反對但有道理的視角比總是同意的更有價值

### 測試：新建 `tests/test_council_evolution.py`

```python
"""Test council perspective evolution."""
import pytest
from tonesoul.council.evolution import CouncilEvolution, PerspectiveHistory


def test_initial_weights_equal():
    evo = CouncilEvolution()
    weights = evo.get_weights()
    assert weights["philosopher"] == 1.0
    assert weights["engineer"] == 1.0
    assert weights["guardian"] == 1.0


def test_record_deliberation():
    evo = CouncilEvolution()
    evo.record_deliberation(
        {"philosopher": "approve", "engineer": "approve", "guardian": "block"},
        final_verdict="approve",
    )
    summary = evo.get_summary()
    assert summary["history"]["philosopher"]["aligned_with_final"] == 1
    assert summary["history"]["guardian"]["dissent_count"] == 1


def test_evolve_weights_boosts_aligned():
    evo = CouncilEvolution()
    # Philosopher always agrees, guardian always dissents
    for _ in range(5):
        evo.record_deliberation(
            {"philosopher": "approve", "engineer": "approve", "guardian": "block"},
            final_verdict="approve",
        )
    weights = evo.evolve_weights()
    # Philosopher should be boosted, guardian should NOT be penalized
    assert weights["philosopher"] >= 1.0
    assert weights["guardian"] >= evo.MIN_WEIGHT


def test_weights_bounded():
    evo = CouncilEvolution()
    for _ in range(100):
        evo.record_deliberation(
            {"philosopher": "approve", "engineer": "block", "guardian": "block"},
            final_verdict="approve",
        )
    weights = evo.evolve_weights()
    for w in weights.values():
        assert CouncilEvolution.MIN_WEIGHT <= w <= CouncilEvolution.MAX_WEIGHT


def test_dissent_not_penalized():
    """Dissenting perspectives should NOT go below MIN_WEIGHT."""
    evo = CouncilEvolution()
    for _ in range(10):
        evo.record_deliberation(
            {"philosopher": "approve", "guardian": "block"},
            final_verdict="approve",
        )
    weights = evo.evolve_weights()
    assert weights["guardian"] >= CouncilEvolution.MIN_WEIGHT


def test_alignment_rate():
    h = PerspectiveHistory(name="test")
    h.record_vote(True)
    h.record_vote(True)
    h.record_vote(False)
    assert abs(h.alignment_rate - 0.667) < 0.01
```

---

## Task 3d：對抗式自省（研究級 Stub）

### 目標

建立一個概念框架：Red team agent 挑戰承諾一致性，Blue team 修復。
**本輪只建空殼和介面**，不實作真正的 agent loop。

### 新建檔案：`tonesoul/memory/adversarial.py`

```python
"""
Adversarial Self-Reflection (Research Stub)

Concept: Two adversarial processes examine memory consistency:
- Red Team: Tries to find contradictions, broken commitments, value drift
- Blue Team: Proposes repairs, reaffirmations, or acknowledged changes

This module is a STUB — it defines the interface and data structures
but does NOT implement actual adversarial logic.

Research references:
- EvoMail adversarial self-evolution loops (2025)
- Reflexion: language agents with verbal reinforcement learning (2023)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ChallengeType(Enum):
    """Types of adversarial challenges."""
    CONTRADICTION = "contradiction"        # statement X contradicts statement Y
    BROKEN_COMMITMENT = "broken_commitment"  # commitment not honored
    VALUE_DRIFT = "value_drift"            # gradual shift from stated values
    INCONSISTENCY = "inconsistency"        # behavior doesn't match stated principles


@dataclass
class Challenge:
    """A challenge posed by the Red Team."""
    challenge_type: ChallengeType
    description: str
    evidence: List[str] = field(default_factory=list)
    severity: float = 0.5  # 0.0 = minor, 1.0 = critical
    
    def to_dict(self) -> dict:
        return {
            "type": self.challenge_type.value,
            "description": self.description,
            "evidence": self.evidence,
            "severity": self.severity,
        }


@dataclass
class Repair:
    """A repair proposed by the Blue Team."""
    challenge: Challenge
    repair_type: str  # "reaffirm", "acknowledge_change", "reconcile"
    explanation: str
    
    def to_dict(self) -> dict:
        return {
            "challenge": self.challenge.to_dict(),
            "repair_type": self.repair_type,
            "explanation": self.explanation,
        }


class AdversarialReflector:
    """
    Stub for adversarial self-reflection.
    
    Future implementation would:
    1. Red Team scans semantic graph + commitment history for inconsistencies
    2. Blue Team proposes repairs or acknowledges intentional changes  
    3. Results feed back into the pipeline to improve response consistency
    
    Current implementation: only provides the interface and data structures.
    """
    
    def __init__(self) -> None:
        self._challenges: List[Challenge] = []
        self._repairs: List[Repair] = []
    
    def run_red_team(
        self,
        commitments: List[Dict],
        contradictions: List[Dict],
        values: List[Dict],
    ) -> List[Challenge]:
        """
        [STUB] Red Team analysis.
        
        In a full implementation, this would:
        - Cross-reference commitments with recent behavior
        - Check contradictions for unresolved conflicts
        - Detect value drift over time
        """
        challenges = []
        
        # Simple stub: convert existing contradictions to challenges
        for c in contradictions:
            challenges.append(Challenge(
                challenge_type=ChallengeType.CONTRADICTION,
                description=str(c.get("description", "Unknown contradiction")),
                evidence=[str(c.get("path", []))],
                severity=float(c.get("severity", 0.5)),
            ))
        
        self._challenges = challenges
        return challenges
    
    def run_blue_team(
        self,
        challenges: Optional[List[Challenge]] = None,
    ) -> List[Repair]:
        """
        [STUB] Blue Team repair proposals.
        
        In a full implementation, this would:
        - For each challenge, propose a repair strategy
        - Use LLM to generate explanation
        - Suggest commitment updates or acknowledgements
        """
        challenges = challenges or self._challenges
        repairs = []
        
        for challenge in challenges:
            repairs.append(Repair(
                challenge=challenge,
                repair_type="acknowledge_change",
                explanation=f"Stub: {challenge.description} — needs review",
            ))
        
        self._repairs = repairs
        return repairs
    
    def get_summary(self) -> Dict:
        return {
            "challenges_found": len(self._challenges),
            "repairs_proposed": len(self._repairs),
            "challenges": [c.to_dict() for c in self._challenges],
            "repairs": [r.to_dict() for r in self._repairs],
        }
```

### 測試：新建 `tests/test_adversarial.py`

```python
"""Test adversarial self-reflection stub."""
import pytest
from tonesoul.memory.adversarial import (
    AdversarialReflector,
    Challenge, ChallengeType, Repair,
)


def test_challenge_creation():
    c = Challenge(
        challenge_type=ChallengeType.CONTRADICTION,
        description="said X then said not-X",
    )
    d = c.to_dict()
    assert d["type"] == "contradiction"


def test_red_team_converts_contradictions():
    reflector = AdversarialReflector()
    contradictions = [
        {"description": "honesty vs deception", "severity": 0.7, "path": ["a", "b"]},
    ]
    challenges = reflector.run_red_team(
        commitments=[], contradictions=contradictions, values=[]
    )
    assert len(challenges) == 1
    assert challenges[0].severity == 0.7


def test_blue_team_generates_repairs():
    reflector = AdversarialReflector()
    reflector.run_red_team(
        commitments=[],
        contradictions=[{"description": "test contradiction"}],
        values=[],
    )
    repairs = reflector.run_blue_team()
    assert len(repairs) == 1
    assert repairs[0].repair_type == "acknowledge_change"


def test_summary():
    reflector = AdversarialReflector()
    reflector.run_red_team(
        commitments=[],
        contradictions=[{"description": "c1"}, {"description": "c2"}],
        values=[],
    )
    reflector.run_blue_team()
    summary = reflector.get_summary()
    assert summary["challenges_found"] == 2
    assert summary["repairs_proposed"] == 2


def test_empty_input():
    reflector = AdversarialReflector()
    challenges = reflector.run_red_team([], [], [])
    assert challenges == []
    repairs = reflector.run_blue_team()
    assert repairs == []
```

---

## 完成後

1. `python -m pytest tests/ -v` — 全部通過
2. `black --check --line-length 100 tonesoul tests` — 通過
3. `ruff check tonesoul tests` — 通過
4. Commit: `feat(experimental): semantic trigger, cross-session recovery, council evolution, adversarial stub`
5. Push

## 修改清單

| 檔案 | 類型 | 說明 |
|------|------|------|
| `tonesoul/unified_pipeline.py` | [MODIFY] | +_semantic_trigger_check(), +_try_cross_session_recovery() |
| `tonesoul/council/evolution.py` | [NEW] | 議會自我演化追蹤 |
| `tonesoul/memory/adversarial.py` | [NEW] | 對抗式自省 stub |
| `tests/test_semantic_trigger.py` | [NEW] | 語義觸發測試 |
| `tests/test_cross_session_recovery.py` | [NEW] | 跨 session 恢復測試 |
| `tests/test_council_evolution.py` | [NEW] | 議會演化測試 |
| `tests/test_adversarial.py` | [NEW] | 對抗式自省測試 |

## 不要動的檔案

| 檔案 | 原因 |
|------|------|
| `tonesoul/council/runtime.py` | 不改現有議會邏輯 |
| `tonesoul/memory/visual_chain.py` | 只讀取，不修改 |
| `tonesoul/memory/semantic_graph.py` | 只讀取，不修改 |

## 2026-02-21 Codex Mainline Update (Phase 105-B)

- Implemented decay query optimization in `tonesoul/memory/soul_db.py`.
- Added top-k heap path in `_decay_records(..., top_k=...)`.
- Wired `JsonlSoulDB.query` and `SqliteSoulDB.query` to pass `limit` as `top_k` when `apply_decay=True`.
- Added regression coverage in `tests/test_soul_db_decay_query.py` for JSONL and SQLite parity.
- Added benchmark tooling:
  - `scripts/benchmark_decay_query.py`
  - `reports/decay_query_benchmark_latest.json`
  - `reports/decay_query_benchmark_latest.md`
- Full regression status:
  - `pytest -q` => `885 passed` (2026-02-21)
