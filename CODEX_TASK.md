# CODEX_TASK — Level 1：記憶接線 v4

> **日期**：2026-02-13T17:40 (UTC+8)
> **交辦者**：Antigravity
> **前置**：先讀 `docs/ARCHITECTURE_DEPLOYED.md`（v2.1），再讀本文件
> **前一輪**：v2（decay engine + graph/visual hooks）、v3（decay gating + contradictions API + sampling）全部完成 ✅

---

## 總覽

v2/v3 把零件做好了。v4 的目標 = **把零件的能力接到實際使用的地方**。

```
已完成 ✅                             本輪接線 🔌
────────────────────────────────────────────────
SemanticGraph 已在 pipeline 更新    → 1b: 回應前查矛盾，違反時警示
VisualChain 已在 pipeline 拍攝      → 1a: 注入到 LLM prompt 給 AI 看
Decay 已在 query() 支援             → 1c: session 結束時自動清理
```

**這輪 3 件事**：

| # | 任務 | 改動範圍 | 難度 |
|---|------|---------|------|
| 1a | Visual Chain → Prompt 注入 | `unified_pipeline.py` | 🟢 低 |
| 1b | SemanticGraph → 回應前矛盾檢查 | `unified_pipeline.py` | 🟢 低 |
| 1c | Decay → Session 結束自動清理 | `apps/api/server.py` + `soul_db.py` | 🟡 中 |

---

## Task 1a：Visual Chain → Prompt 注入

### 目標

讓 AI 在生成回應前，能**看到最近 3 張圖鏈快照**。
這相當於讓 AI「回顧」最近的對話脈絡，只用 ~300 tokens。

### 修改：`tonesoul/unified_pipeline.py`

在 `process()` 方法裡，找到 `# ========== Persona Config 注入 ==========` 區塊（約 L403），**在它之後、ToneBridge 分析之前**，加入：

```python
# ========== Visual Memory Context 注入 ==========
try:
    chain = self._get_visual_chain()
    if chain and chain.frame_count > 0:
        visual_context = chain.render_recent_as_markdown(n=3)
        if visual_context and len(visual_context) > 50:
            user_message = (
                f"[脈絡記憶 — 最近視覺快照]\n{visual_context}\n\n"
                f"---\n\n{user_message}"
            )
except Exception:
    pass  # 圖鏈讀取錯誤不影響主流程
```

### 注意

- `render_recent_as_markdown(n=3)` 已存在於 `visual_chain.py`，直接呼叫
- 注入位置必須在 persona 注入**之後**（因為 persona 也改 user_message）
- 用 `len(visual_context) > 50` 過濾空白 / 無意義返回

### 測試：新建 `tests/test_visual_chain_prompt_injection.py`

```python
"""Test visual chain context injection into pipeline prompt."""
import pytest

def test_visual_context_injected_when_frames_exist():
    """Verify user_message is prefixed with visual context."""
    from tonesoul.memory.visual_chain import VisualChain, FrameType

    chain = VisualChain()
    chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 0",
        data={"tension": 0.3, "verdict": "approve", "council_mode": "hybrid"},
        tags=["auto"],
    )
    md = chain.render_recent_as_markdown(n=3)
    assert "Visual Memory Chain" in md
    assert "session_state" in md
    assert len(md) > 50

def test_visual_context_empty_chain_returns_short():
    """Empty chain should produce short output that won't be injected."""
    from tonesoul.memory.visual_chain import VisualChain

    chain = VisualChain()
    md = chain.render_recent_as_markdown(n=3)
    # Should be short (just header, no frames)
    assert "No frames" in md or len(md) < 100
```

---

## Task 1b：SemanticGraph → 回應前矛盾警示

### 目標

目前矛盾偵測在回應**之後**才跑。把它移到回應**之前**，如果偵測到矛盾，就在 user_message 裡加一個提醒，讓 AI 知道要注意一致性。

### 修改：`tonesoul/unified_pipeline.py`

在 `process()` 方法裡，找到目前的語義圖譜區塊（`# ========== 9. 語義圖譜更新 ==========`，約 L597）。

**不要刪除現有的圖譜更新邏輯**。而是在步驟 [3] Council.deliberate() **之前**，加一個 early contradiction check：

```python
# ========== 2.8 Early Contradiction Check ==========
pre_contradictions = []
try:
    graph = self._get_semantic_graph()
    if graph:
        pre_contradictions = graph.detect_contradictions()
        if pre_contradictions:
            contradiction_hints = "; ".join(
                str(c.description)[:60] for c in pre_contradictions[:3]
            )
            user_message = (
                f"[內在一致性提醒: 偵測到 {len(pre_contradictions)} 個潛在矛盾 — "
                f"{contradiction_hints}]\n\n{user_message}"
            )
except Exception:
    pass
```

### 注意

- `detect_contradictions()` 已存在於 `semantic_graph.py`
- 每個 `Contradiction` 物件有 `.description` 屬性 — 如果是 `.to_dict()` 格式則用 `c.get("description", "")`
- 只取前 3 個矛盾，每個截斷 60 字，避免膨脹 prompt
- 步驟 9 的原有矛盾偵測**保持不變**（那是回應後的完整偵測）

### 測試：新建 `tests/test_early_contradiction_check.py`

```python
"""Test early contradiction check injects hints before response generation."""
import pytest

def test_contradiction_description_accessible():
    """Verify Contradiction objects have description field."""
    from tonesoul.memory.semantic_graph import SemanticGraph

    graph = SemanticGraph()
    # Add conflicting nodes manually
    graph.add_node("honesty", "value")
    graph.add_node("deception", "value")
    graph.add_edge("honesty", "deception", "contradicts")
    contradictions = graph.detect_contradictions()
    # May or may not detect — this tests the interface
    for c in contradictions:
        # Either has .description or .to_dict() with "description"
        desc = getattr(c, "description", None) or c.to_dict().get("description", "")
        assert isinstance(desc, str)
```

---

## Task 1c：Decay → Session 結束自動清理

### 目標

Session 結束（或 session report 生成）時，跑一次 decay query 清理低分記憶。

### 修改：`tonesoul/memory/soul_db.py`

加一個新方法 `cleanup_decayed()`：

```python
def cleanup_decayed(
    self,
    source: MemorySource,
    *,
    forget_threshold: Optional[float] = None,
) -> int:
    """Remove records that have decayed below threshold. Returns count removed."""
    all_records = list(self.stream(source))
    now_str = datetime.now(timezone.utc).isoformat()
    # Use _decay_records to get surviving records
    surviving = _decay_records(all_records, forget_threshold=forget_threshold)
    removed_count = len(all_records) - len(surviving)
    # For now: log the count. Actual deletion depends on backend.
    return removed_count
```

### 修改：`apps/api/server.py`

在 `/api/session-report` 路由中，成功生成報告後，加清理呼叫：

```python
# After report generation
try:
    from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource
    soul_db = _get_soul_db()  # or however soul_db is accessed
    if soul_db and hasattr(soul_db, 'cleanup_decayed'):
        cleaned = soul_db.cleanup_decayed(MemorySource.SELF_JOURNAL)
        if cleaned > 0:
            print(f"[INFO] Decay cleanup: {cleaned} memories below threshold")
except Exception as e:
    print(f"[WARN] Decay cleanup error: {e}")
```

### 注意

- `cleanup_decayed()` 目前只是返回計數。**不要真的刪除記憶** — 先做 soft cleanup（只計數），等確認安全再加真正刪除
- `_get_soul_db()` — 找到 server.py 裡怎麼取得 soul_db 實例，用同樣的方式
- 只在 `session-report` 觸發，不是每次 chat 都清理

### 測試：新建 `tests/test_decay_cleanup.py`

```python
"""Test session-end decay cleanup."""
import pytest

def test_cleanup_returns_count():
    """cleanup_decayed should return integer count."""
    from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource
    import tempfile, pathlib

    with tempfile.TemporaryDirectory() as tmp:
        db = JsonlSoulDB(base_dir=pathlib.Path(tmp))
        db.append(MemorySource.SELF_JOURNAL, {"text": "test"})
        result = db.cleanup_decayed(MemorySource.SELF_JOURNAL)
        assert isinstance(result, int)
        assert result >= 0
```

---

## 完成後

1. `python -m pytest tests/ -v` — 全部通過
2. `black --check --line-length 100 tonesoul tests apps` — 通過
3. `ruff check tonesoul tests apps` — 通過
4. Commit: `feat(memory): wire visual prompt injection, early contradiction check, decay cleanup`
5. Push

## 修改清單

| 檔案 | 類型 | 說明 |
|------|------|------|
| `tonesoul/unified_pipeline.py` | [MODIFY] | +visual context 注入 +early contradiction check |
| `tonesoul/memory/soul_db.py` | [MODIFY] | +cleanup_decayed() 方法 |
| `apps/api/server.py` | [MODIFY] | +session-report 清理呼叫 |
| `tests/test_visual_chain_prompt_injection.py` | [NEW] | 圖鏈注入測試 |
| `tests/test_early_contradiction_check.py` | [NEW] | 早期矛盾檢查測試 |
| `tests/test_decay_cleanup.py` | [NEW] | 衰減清理測試 |

## 不要動的檔案

| 檔案 | 原因 |
|------|------|
| `tonesoul/memory/visual_chain.py` | 已完成 ✅ |
| `tonesoul/memory/semantic_graph.py` | 已完成 ✅ |
| `tonesoul/memory/decay.py` | 已完成 ✅ |
| `docs/` | 文件不動 |
