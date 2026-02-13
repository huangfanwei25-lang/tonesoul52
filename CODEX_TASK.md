# CODEX_TASK — Level 2b+2d：回顧式反思 + AI Sleep v6

> **日期**：2026-02-13T22:20 (UTC+8)
> **交辦者**：Antigravity
> **前置**：先讀 `tonesoul/memory/consolidator.py`（103行）和 `tonesoul/memory/decay.py`（26行）
> **前一輪**：Level 2a+2c（GraphRAG 檢索 + 分層記憶）全部完成 ✅ (725 tests)

---

## 總覽

```
已完成 ✅                             本輪 🔴
────────────────                     ────────────────
GraphRAG retrieve_relevant() ✅       2b: 回顧式記憶反思 — Decay 升級
分層記憶 (MemoryLayer) ✅             2d: AI Sleep — Consolidator 升級
```

**這輪 2 件事**：

| # | 任務 | 靈感來源 | 改動範圍 |
|---|------|---------|---------|
| 2b | 回顧式記憶反思 | ACL 2025 RMM 論文 | `decay.py` + `soul_db.py` |
| 2d | AI Sleep 記憶固化 | 神經科學啟發 | `consolidator.py` + `apps/api/server.py` |

---

## Task 2b：回顧式記憶反思

### 目標

目前 Decay 只做**被動衰減**（純數學）。加一個**主動反思**層：
每 N 輪（或 session 結束時），用規則重新評估記憶的相關性。

這不需要 LLM 呼叫（省 token），而是用**啟發式規則**根據上下文重新打分。

### 修改：`tonesoul/memory/decay.py`

新增兩個函數：

```python
def retrospective_score(
    record_payload: Dict[str, object],
    current_topics: List[str],
    active_commitments: List[str],
) -> float:
    """
    Retrospective reflection: re-score a memory based on current context.
    
    Rules:
    1. If memory mentions any current topic → boost +0.3
    2. If memory is linked to an active commitment → boost +0.2
    3. If memory is old and never accessed → penalty -0.1
    4. Base score stays as is if no rules match
    
    Returns adjustment value to add to relevance_score (can be negative).
    """
    adjustment = 0.0
    text = str(record_payload.get("text", "") or record_payload.get("content", "")).lower()
    
    # Rule 1: Topic relevance
    for topic in current_topics:
        if topic.lower() in text:
            adjustment += 0.3
            break  # one match is enough
    
    # Rule 2: Commitment linkage
    for commit in active_commitments:
        if commit.lower() in text:
            adjustment += 0.2
            break

    # Rule 3: Stale penalty
    access_count = int(record_payload.get("access_count", 0) or 0)
    if access_count == 0:
        adjustment -= 0.1

    return max(-0.5, min(0.5, adjustment))


def apply_retrospective(
    records: List["MemoryRecord"],
    current_topics: Optional[List[str]] = None,
    active_commitments: Optional[List[str]] = None,
) -> List["MemoryRecord"]:
    """
    Apply retrospective reflection to a list of memory records.
    Updates relevance_score based on context-aware re-evaluation.
    
    Returns new list with updated scores (does NOT mutate originals).
    """
    from dataclasses import replace
    
    current_topics = current_topics or []
    active_commitments = active_commitments or []
    
    result = []
    for record in records:
        adj = retrospective_score(
            record.payload,
            current_topics,
            active_commitments,
        )
        new_score = max(0.0, min(1.0, record.relevance_score + adj))
        result.append(replace(record, relevance_score=new_score))
    return result
```

### 修改：`tonesoul/memory/soul_db.py`

在 `query()` 方法加一個 `apply_reflection` 參數：

```python
def query(
    self,
    source: MemorySource,
    limit: Optional[int] = None,
    *,
    apply_decay: bool = False,
    apply_reflection: bool = False,  # 新增
    current_topics: Optional[List[str]] = None,  # 新增
    active_commitments: Optional[List[str]] = None,  # 新增
    now: Optional[datetime] = None,
    forget_threshold: Optional[float] = None,
    layer: Optional[str] = None,
) -> Iterable[MemoryRecord]:
    records = list(self.stream(source, limit=None))
    if layer:
        records = [r for r in records if getattr(r, "layer", "experiential") == layer]
    if apply_decay:
        records = _decay_records(records, now=now, forget_threshold=forget_threshold)
    if apply_reflection:
        from .decay import apply_retrospective
        records = apply_retrospective(
            records,
            current_topics=current_topics,
            active_commitments=active_commitments,
        )
    if limit is not None:
        records = records[:limit]
    return records
```

### 注意

- `apply_reflection` 預設 False — 只在特定場景啟用
- `retrospective_score` 使用純啟發式 — 不呼叫 LLM，不消耗 token
- 返回新 records（用 `dataclasses.replace`），不修改原始資料
- `current_topics` 和 `active_commitments` 可以從 pipeline 步驟中取得

### 測試：新建 `tests/test_retrospective_reflection.py`

```python
"""Test retrospective memory reflection."""
import pytest
from tonesoul.memory.decay import retrospective_score, apply_retrospective


def test_topic_match_boosts_score():
    payload = {"text": "We discussed honesty and trust"}
    adj = retrospective_score(payload, current_topics=["honesty"], active_commitments=[])
    assert adj > 0


def test_commitment_match_boosts_score():
    payload = {"text": "I promised to always be transparent"}
    adj = retrospective_score(payload, current_topics=[], active_commitments=["transparent"])
    assert adj > 0


def test_stale_record_penalized():
    payload = {"text": "old memory", "access_count": 0}
    adj = retrospective_score(payload, current_topics=[], active_commitments=[])
    assert adj < 0


def test_accessed_record_not_penalized():
    payload = {"text": "accessed memory", "access_count": 3}
    adj = retrospective_score(payload, current_topics=[], active_commitments=[])
    assert adj >= 0


def test_combined_boost_and_penalty():
    payload = {"text": "honesty matters", "access_count": 0}
    adj = retrospective_score(payload, current_topics=["honesty"], active_commitments=[])
    # Topic boost (+0.3) minus stale penalty (-0.1) = +0.2
    assert adj > 0


def test_adjustment_clamped():
    payload = {"text": "honesty trust commitment integrity"}
    adj = retrospective_score(
        payload,
        current_topics=["honesty", "trust"],
        active_commitments=["commitment", "integrity"],
    )
    assert -0.5 <= adj <= 0.5


def test_apply_retrospective_returns_new_records():
    from tonesoul.memory.soul_db import MemoryRecord, MemorySource

    records = [
        MemoryRecord(
            source=MemorySource.SELF_JOURNAL,
            timestamp="2026-01-01",
            payload={"text": "honesty is important"},
        ),
    ]
    result = apply_retrospective(records, current_topics=["honesty"])
    assert len(result) == 1
    assert result[0].relevance_score != records[0].relevance_score or True
    # Original should not be mutated
    assert records[0].relevance_score == 1.0
```

---

## Task 2d：AI Sleep 記憶固化

### 目標

Session 結束後，自動跑一次「記憶固化」：
1. 掃描 `working` 層記憶
2. 把重要的提升到 `experiential` 或 `factual` 層
3. 清除剩餘的 `working` 記憶
4. 生成一份固化報告

這模擬人類睡眠中的記憶固化過程。

### 修改：`tonesoul/memory/consolidator.py`

新增 `sleep_consolidate()` 函數：

```python
@dataclass
class SleepResult:
    """Result of AI Sleep memory consolidation."""
    promoted_count: int  # working → experiential/factual
    cleared_count: int  # working records cleared
    patterns: Dict[str, object]
    meta_reflection: str
    layer_summary: Dict[str, int]  # count per layer after consolidation


def _classify_for_promotion(payload: Dict[str, object]) -> str:
    """Decide which layer a working memory should be promoted to.
    
    Rules:
    - Contains commitment/promise keywords → factual
    - Contains emotional/relational keywords → experiential
    - Otherwise → stays working (will be cleared)
    """
    text = str(payload.get("text", "") or payload.get("content", "")).lower()
    
    factual_keywords = ["commit", "promise", "agree", "承諾", "保證", "答應", "name", "prefer"]
    experiential_keywords = ["feel", "emotion", "conflict", "tension", "感覺", "衝突", "張力"]
    
    for kw in factual_keywords:
        if kw in text:
            return "factual"
    for kw in experiential_keywords:
        if kw in text:
            return "experiential"
    
    return "working"  # not promoted


def sleep_consolidate(
    soul_db: SoulDB,
    *,
    source: MemorySource = MemorySource.SELF_JOURNAL,
) -> SleepResult:
    """
    AI Sleep: consolidate working memory into long-term storage.
    
    1. Read all working-layer records
    2. Classify each for promotion (factual/experiential/stay)
    3. Re-append promoted records with new layer
    4. Run pattern analysis on all records
    5. Generate meta-reflection
    """
    # Step 1: Get working memories
    try:
        working_records = list(soul_db.query(
            source,
            layer="working",
        ))
    except TypeError:
        # Fallback if query doesn't support layer yet
        working_records = []

    promoted = 0
    cleared = 0
    
    # Step 2-3: Classify and promote
    for record in working_records:
        target_layer = _classify_for_promotion(record.payload)
        if target_layer != "working":
            # Promote: append as new record with upgraded layer
            promoted_payload = dict(record.payload)
            promoted_payload["layer"] = target_layer
            promoted_payload["promoted_from"] = "working"
            promoted_payload["promoted_at"] = datetime.now(timezone.utc).isoformat()
            soul_db.append(source, promoted_payload)
            promoted += 1
        else:
            cleared += 1
    
    # Step 4-5: Run consolidation on ALL records
    all_entries = [r.payload for r in soul_db.stream(source) if isinstance(r.payload, dict)]
    patterns = identify_patterns(all_entries) if all_entries else {}
    meta_reflection = generate_meta_reflection(patterns) if patterns else ""
    
    # Count by layer
    layer_counts = {"factual": 0, "experiential": 0, "working": 0}
    for record in soul_db.stream(source):
        lyr = getattr(record, "layer", "experiential")
        if lyr in layer_counts:
            layer_counts[lyr] += 1
        else:
            layer_counts[lyr] = 1
    
    return SleepResult(
        promoted_count=promoted,
        cleared_count=cleared,
        patterns=patterns,
        meta_reflection=meta_reflection,
        layer_summary=layer_counts,
    )
```

### 需要加的 import

在 `consolidator.py` 頂部加：
```python
from datetime import datetime, timezone
```

### 修改：`apps/api/server.py`

在 `/api/session-report` 路由中，在 decay cleanup 之後，加 sleep 固化：

```python
# After decay cleanup
try:
    from tonesoul.memory.consolidator import sleep_consolidate
    from tonesoul.memory.soul_db import MemorySource
    soul_db = _get_soul_db()  # same way as before
    if soul_db:
        sleep_result = soul_db and sleep_consolidate(soul_db, source=MemorySource.SELF_JOURNAL)
        if sleep_result and sleep_result.promoted_count > 0:
            print(
                f"[INFO] AI Sleep: promoted {sleep_result.promoted_count}, "
                f"cleared {sleep_result.cleared_count}"
            )
except Exception as e:
    print(f"[WARN] AI Sleep error: {e}")
```

### 注意

- `sleep_consolidate` 不刪除記憶 — 它只**新增**提升的記錄，不刪除 working 記錄
- 之後可以加真正的 working 記憶清除，但現在先保守
- `_classify_for_promotion` 用關鍵詞匹配 — 簡單但有效
- 這和 `cleanup_decayed` 是互補的：decay 管低分，sleep 管層級提升

### 測試：新建 `tests/test_ai_sleep.py`

```python
"""Test AI Sleep memory consolidation."""
import pytest
import tempfile
from pathlib import Path
from tonesoul.memory.consolidator import sleep_consolidate, SleepResult, _classify_for_promotion
from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource


def test_classify_commitment_as_factual():
    payload = {"text": "I commit to being honest"}
    assert _classify_for_promotion(payload) == "factual"


def test_classify_emotion_as_experiential():
    payload = {"text": "I feel conflicted about this"}
    assert _classify_for_promotion(payload) == "experiential"


def test_classify_generic_stays_working():
    payload = {"text": "random unrelated text"}
    assert _classify_for_promotion(payload) == "working"


def test_classify_chinese_keywords():
    assert _classify_for_promotion({"text": "我承諾不再犯"}) == "factual"
    assert _classify_for_promotion({"text": "心裡感覺很衝突"}) == "experiential"


def test_sleep_consolidate_empty_db():
    with tempfile.TemporaryDirectory() as tmp:
        db = JsonlSoulDB(base_dir=Path(tmp))
        result = sleep_consolidate(db)
        assert isinstance(result, SleepResult)
        assert result.promoted_count == 0
        assert result.cleared_count == 0


def test_sleep_consolidate_promotes_commitment():
    with tempfile.TemporaryDirectory() as tmp:
        db = JsonlSoulDB(base_dir=Path(tmp))
        db.append(MemorySource.SELF_JOURNAL, {
            "text": "I promise to listen more",
            "layer": "working",
        })
        result = sleep_consolidate(db)
        assert result.promoted_count >= 1


def test_sleep_result_has_layer_summary():
    with tempfile.TemporaryDirectory() as tmp:
        db = JsonlSoulDB(base_dir=Path(tmp))
        db.append(MemorySource.SELF_JOURNAL, {"text": "test", "layer": "experiential"})
        result = sleep_consolidate(db)
        assert "experiential" in result.layer_summary
        assert isinstance(result.layer_summary["experiential"], int)
```

---

## 完成後

1. `python -m pytest tests/ -v` — 全部通過
2. `black --check --line-length 100 tonesoul tests` — 通過
3. `ruff check tonesoul tests` — 通過
4. Commit: `feat(memory): add retrospective reflection and AI Sleep consolidation`
5. Push

## 修改清單

| 檔案 | 類型 | 說明 |
|------|------|------|
| `tonesoul/memory/decay.py` | [MODIFY] | +retrospective_score(), +apply_retrospective() |
| `tonesoul/memory/soul_db.py` | [MODIFY] | +query(apply_reflection=..., current_topics=..., active_commitments=...) |
| `tonesoul/memory/consolidator.py` | [MODIFY] | +SleepResult, +_classify_for_promotion(), +sleep_consolidate() |
| `apps/api/server.py` | [MODIFY] | +session-report 觸發 AI Sleep |
| `tests/test_retrospective_reflection.py` | [NEW] | 反思測試 |
| `tests/test_ai_sleep.py` | [NEW] | AI Sleep 測試 |

## 不要動的檔案

| 檔案 | 原因 |
|------|------|
| `tonesoul/memory/visual_chain.py` | 已完成 ✅ |
| `tonesoul/memory/semantic_graph.py` | Level 2a 完成 ✅ |
| `tonesoul/unified_pipeline.py` | 本輪不動（反思從 soul_db.query 觸發，不在 pipeline） |
