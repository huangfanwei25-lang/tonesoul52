# CODEX_TASK — Level 2：GraphRAG 檢索 + 分層記憶 v5

> **日期**：2026-02-13T19:00 (UTC+8)
> **交辦者**：Antigravity
> **前置**：先讀 `docs/ARCHITECTURE_DEPLOYED.md`（v2.1），再讀 `tonesoul/memory/semantic_graph.py`
> **前一輪**：Level 1 接線（visual prompt 注入 / 矛盾早期檢查 / decay 清理）全部完成 ✅ (713 tests)

---

## 總覽

Level 1 把零件接上線了。Level 2 **升級核心能力**：

```
Level 1 (已完成):                Level 2 (本輪):
────────────────                 ────────────────
圖鏈 → prompt 注入 ✅            SemanticGraph → GraphRAG 多跳檢索 🔴
矛盾 → 早期檢查 ✅               soul_db → 分層記憶 (factual/experiential) 🔴
decay → soft cleanup ✅
```

**這輪 2 件事**：

| # | 任務 | 靈感來源 | 改動範圍 |
|---|------|---------|---------|
| 2a | GraphRAG 多跳檢索 | Microsoft GraphRAG (2024) | `semantic_graph.py` + `unified_pipeline.py` |
| 2c | 分層記憶 | Amazon Bedrock AgentCore | `soul_db.py` |

---

## Task 2a：GraphRAG 多跳檢索

### 目標

給定 user message，從 SemanticGraph 裡找到相關的承諾/概念/話題，然後沿著 edges 做 2-hop BFS，回傳一個結構化的「相關脈絡」。

目前 SemanticGraph 只存不查。加了這個方法後，AI 能在回應前「沿著知識圖譜走」，找到「我之前說過什麼相關的話」。

### 修改：`tonesoul/memory/semantic_graph.py`

新增一個方法 `retrieve_relevant()`：

```python
def retrieve_relevant(
    self,
    query_terms: List[str],
    max_hops: int = 2,
    max_results: int = 10,
) -> Dict[str, Any]:
    """
    GraphRAG-style multi-hop retrieval.
    
    Given query terms (from user message), find matching nodes,
    then walk edges up to max_hops to discover related context.
    
    Returns:
        {
            "matched_nodes": [...],      # 直接匹配的節點
            "related_nodes": [...],      # 多跳發現的節點
            "paths": [...],             # 連接路徑
            "commitments_in_scope": [...], # 範圍內的承諾
            "context_summary": "..."     # 人類可讀的摘要
        }
    """
    if not query_terms or not self._nodes:
        return {
            "matched_nodes": [],
            "related_nodes": [],
            "paths": [],
            "commitments_in_scope": [],
            "context_summary": "",
        }

    # Step 1: 找到匹配的起始節點（label 包含任一 query term）
    matched = []
    query_lower = [t.lower().strip() for t in query_terms if t.strip()]
    for node in self._nodes.values():
        label_lower = node.label.lower()
        for term in query_lower:
            if term in label_lower or label_lower in term:
                matched.append(node)
                break

    if not matched:
        return {
            "matched_nodes": [],
            "related_nodes": [],
            "paths": [],
            "commitments_in_scope": [],
            "context_summary": "No matching concepts found in semantic graph.",
        }

    # Step 2: BFS 多跳展開
    visited = set(n.id for n in matched)
    frontier = [n.id for n in matched]
    related = []
    paths = []

    for hop in range(max_hops):
        next_frontier = []
        for nid in frontier:
            neighbors = self.get_neighbors(nid)
            for neighbor in neighbors:
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    next_frontier.append(neighbor.id)
                    related.append(neighbor)
                    # 記錄路徑
                    edges = self.get_edges_between(nid, neighbor.id)
                    for edge in edges:
                        paths.append({
                            "from": self._nodes[nid].label if nid in self._nodes else nid,
                            "to": neighbor.label,
                            "relation": edge.edge_type.value,
                            "hop": hop + 1,
                        })
        frontier = next_frontier
        if not frontier:
            break

    # Step 3: 找出範圍內的承諾
    all_in_scope = set(n.id for n in matched) | set(n.id for n in related)
    commitments = [
        self._nodes[nid]
        for nid in all_in_scope
        if nid in self._nodes and self._nodes[nid].node_type == NodeType.COMMITMENT
    ]

    # Step 4: 生成摘要
    summary_parts = []
    if matched:
        labels = ", ".join(n.label for n in matched[:5])
        summary_parts.append(f"直接相關: {labels}")
    if commitments:
        labels = ", ".join(n.label for n in commitments[:3])
        summary_parts.append(f"相關承諾: {labels}")
    if paths:
        summary_parts.append(f"發現 {len(paths)} 條關聯路徑 ({max_hops}-hop)")

    return {
        "matched_nodes": [n.to_dict() for n in matched[:max_results]],
        "related_nodes": [n.to_dict() for n in related[:max_results]],
        "paths": paths[:20],
        "commitments_in_scope": [n.to_dict() for n in commitments],
        "context_summary": " | ".join(summary_parts) if summary_parts else "",
    }
```

### 修改：`tonesoul/unified_pipeline.py`

在 `process()` 方法裡，**ToneBridge 分析之後、Council 之前**（大約在步驟 2.8 矛盾檢查之後），加入 GraphRAG 檢索：

```python
# ========== 2.9 GraphRAG Context Retrieval ==========
graph_context = {}
try:
    graph = self._get_semantic_graph()
    if graph:
        # 用 user message 的關鍵詞做檢索
        query_terms = []
        if tb_result and tb_result.tone and tb_result.tone.trigger_keywords:
            query_terms.extend(tb_result.tone.trigger_keywords)
        if tb_result and tb_result.motive and tb_result.motive.likely_motive:
            query_terms.append(tb_result.motive.likely_motive)
        # 加上 user message 的前幾個詞作為 fallback
        words = [w.strip() for w in user_message.split()[:10] if len(w.strip()) > 2]
        query_terms.extend(words[:5])

        if query_terms:
            graph_context = graph.retrieve_relevant(
                query_terms=query_terms,
                max_hops=2,
                max_results=10,
            )
            # 如果有相關脈絡，注入到 user_message
            context_summary = graph_context.get("context_summary", "")
            if context_summary:
                user_message = (
                    f"[語義脈絡: {context_summary}]\n\n{user_message}"
                )
except Exception:
    pass
```

### 測試：新建 `tests/test_graph_rag_retrieval.py`

```python
"""Test GraphRAG multi-hop retrieval."""
import pytest
from tonesoul.memory.semantic_graph import (
    SemanticGraph, NodeType, EdgeType,
)


def test_retrieve_empty_graph():
    g = SemanticGraph()
    result = g.retrieve_relevant(["test"])
    assert result["matched_nodes"] == []
    assert "No matching" in result["context_summary"]


def test_retrieve_direct_match():
    g = SemanticGraph()
    g.add_node("honesty", NodeType.CONCEPT)
    result = g.retrieve_relevant(["honesty"])
    assert len(result["matched_nodes"]) == 1
    assert result["matched_nodes"][0]["label"] == "honesty"


def test_retrieve_multi_hop():
    g = SemanticGraph()
    n1 = g.add_node("honesty", NodeType.CONCEPT)
    n2 = g.add_node("transparency", NodeType.CONCEPT)
    n3 = g.add_node("trust", NodeType.CONCEPT)
    g.add_edge(n1, n2, EdgeType.SUPPORTS)
    g.add_edge(n2, n3, EdgeType.IMPLIES)
    result = g.retrieve_relevant(["honesty"], max_hops=2)
    all_labels = [n["label"] for n in result["matched_nodes"] + result["related_nodes"]]
    assert "honesty" in all_labels
    assert "transparency" in all_labels
    assert "trust" in all_labels


def test_retrieve_commitment_in_scope():
    g = SemanticGraph()
    n1 = g.add_node("always be truthful", NodeType.COMMITMENT)
    n2 = g.add_node("honesty", NodeType.CONCEPT)
    g.add_edge(n1, n2, EdgeType.RELATED_TO)
    result = g.retrieve_relevant(["honesty"])
    assert len(result["commitments_in_scope"]) >= 1


def test_retrieve_respects_max_hops():
    g = SemanticGraph()
    n1 = g.add_node("A", NodeType.CONCEPT)
    n2 = g.add_node("B", NodeType.CONCEPT)
    n3 = g.add_node("C", NodeType.CONCEPT)
    n4 = g.add_node("D", NodeType.CONCEPT)
    g.add_edge(n1, n2, EdgeType.RELATED_TO)
    g.add_edge(n2, n3, EdgeType.RELATED_TO)
    g.add_edge(n3, n4, EdgeType.RELATED_TO)
    result = g.retrieve_relevant(["A"], max_hops=1)
    labels = [n["label"] for n in result["related_nodes"]]
    assert "B" in labels
    assert "C" not in labels  # 2 hops away, but max_hops=1


def test_retrieve_empty_terms():
    g = SemanticGraph()
    g.add_node("test", NodeType.CONCEPT)
    result = g.retrieve_relevant([])
    assert result["matched_nodes"] == []


def test_retrieve_paths_recorded():
    g = SemanticGraph()
    n1 = g.add_node("ethics", NodeType.CONCEPT)
    n2 = g.add_node("fairness", NodeType.CONCEPT)
    g.add_edge(n1, n2, EdgeType.SUPPORTS)
    result = g.retrieve_relevant(["ethics"])
    assert len(result["paths"]) >= 1
    assert result["paths"][0]["relation"] == "supports"
```

---

## Task 2c：分層記憶

### 目標

目前 `MemorySource` 有 6 種來源（self_journal, summary_balls, 等），但沒有區分**功能層**。

分成 3 層：
- **factual** — 事實性記憶（承諾、名字、日期、偏好）
- **experiential** — 體驗性記憶（對話摘要、情緒模式、衝突解決經驗）
- **working** — 工作記憶（當前 session 的即時脈絡，session 結束後清除）

### 修改：`tonesoul/memory/soul_db.py`

1. 新增 `MemoryLayer` enum：

```python
class MemoryLayer(Enum):
    """Functional memory layers (inspired by Amazon Bedrock AgentCore)."""
    FACTUAL = "factual"        # Facts: commitments, names, preferences
    EXPERIENTIAL = "experiential"  # Experiences: conversation summaries, patterns
    WORKING = "working"        # Working memory: current session, cleared on end
```

2. 在 `MemoryRecord` 加一個欄位：

```python
@dataclass
class MemoryRecord:
    source: MemorySource
    timestamp: str
    payload: Dict[str, object]
    tags: List[str] = field(default_factory=list)
    record_id: Optional[str] = None
    relevance_score: float = 1.0
    access_count: int = 0
    last_accessed: Optional[str] = None
    layer: str = "experiential"  # 預設層：用 str 而非 enum 以保向後相容
```

3. 在 `query()` 方法加 `layer` 過濾：

```python
def query(
    self,
    source: MemorySource,
    limit: Optional[int] = None,
    *,
    apply_decay: bool = False,
    now: Optional[datetime] = None,
    forget_threshold: Optional[float] = None,
    layer: Optional[str] = None,  # 新增：按層篩選
) -> Iterable[MemoryRecord]:
    records = list(self.stream(source, limit=None))
    if layer:
        records = [r for r in records if getattr(r, "layer", "experiential") == layer]
    if apply_decay:
        records = _decay_records(records, now=now, forget_threshold=forget_threshold)
    if limit is not None:
        records = records[:limit]
    return records
```

4. 在 `stream()` 解析時加入 `layer` 欄位：

```python
# 在 JsonlSoulDB.stream() 和 SqliteSoulDB.stream() 的 MemoryRecord 建構裡加：
layer=str(record_payload.get("layer", "experiential")),
```

### 測試：新建 `tests/test_layered_memory.py`

```python
"""Test layered memory functionality."""
import pytest
import tempfile
from pathlib import Path
from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, MemoryRecord


def test_memory_record_has_layer():
    r = MemoryRecord(
        source=MemorySource.SELF_JOURNAL,
        timestamp="2026-01-01",
        payload={"text": "test"},
        layer="factual",
    )
    assert r.layer == "factual"


def test_default_layer_is_experiential():
    r = MemoryRecord(
        source=MemorySource.SELF_JOURNAL,
        timestamp="2026-01-01",
        payload={"text": "test"},
    )
    assert r.layer == "experiential"


def test_query_filter_by_layer():
    with tempfile.TemporaryDirectory() as tmp:
        db = JsonlSoulDB(base_dir=Path(tmp))
        db.append(MemorySource.SELF_JOURNAL, {"text": "fact1", "layer": "factual"})
        db.append(MemorySource.SELF_JOURNAL, {"text": "exp1", "layer": "experiential"})
        db.append(MemorySource.SELF_JOURNAL, {"text": "work1", "layer": "working"})

        factual = list(db.query(MemorySource.SELF_JOURNAL, layer="factual"))
        exp = list(db.query(MemorySource.SELF_JOURNAL, layer="experiential"))
        working = list(db.query(MemorySource.SELF_JOURNAL, layer="working"))
        all_records = list(db.query(MemorySource.SELF_JOURNAL))

        assert len(all_records) == 3
        assert len(factual) >= 1
        assert len(exp) >= 1
        assert len(working) >= 1


def test_layer_backward_compatible():
    """Records without layer field should default to experiential."""
    with tempfile.TemporaryDirectory() as tmp:
        db = JsonlSoulDB(base_dir=Path(tmp))
        db.append(MemorySource.SELF_JOURNAL, {"text": "old record"})
        records = list(db.query(MemorySource.SELF_JOURNAL, layer="experiential"))
        assert len(records) >= 1
```

---

## 完成後

1. `python -m pytest tests/ -v` — 全部通過
2. `black --check --line-length 100 tonesoul tests` — 通過
3. `ruff check tonesoul tests` — 通過
4. Commit: `feat(memory): add GraphRAG retrieval and layered memory`
5. Push

## 修改清單

| 檔案 | 類型 | 說明 |
|------|------|------|
| `tonesoul/memory/semantic_graph.py` | [MODIFY] | +retrieve_relevant() 多跳檢索 |
| `tonesoul/unified_pipeline.py` | [MODIFY] | +GraphRAG context 注入 |
| `tonesoul/memory/soul_db.py` | [MODIFY] | +MemoryLayer enum, +layer 欄位, +layer 過濾 |
| `tests/test_graph_rag_retrieval.py` | [NEW] | GraphRAG 檢索測試 |
| `tests/test_layered_memory.py` | [NEW] | 分層記憶測試 |

## 不要動的檔案

| 檔案 | 原因 |
|------|------|
| `tonesoul/memory/visual_chain.py` | 已完成 ✅ |
| `tonesoul/memory/decay.py` | 已完成 ✅ |
| `apps/web/` | 前端不動 |
