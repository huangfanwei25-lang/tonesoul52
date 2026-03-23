# Soul DB 草案

> Purpose: draft the minimum interface and data model for a unified Soul DB memory entrypoint.
> Last Updated: 2026-03-23

本文件定義 `soul_db.py` 的最小可行介面與資料模型，作為未來 Memory 架構的統一入口。

**目標**

- 統一 `memory/` 讀寫入口，降低 JSONL 檔案直接耦合。
- 保持可替換：未來可切換到 SQLite / Vector DB 而不改上層呼叫。

**資料模型**

```python
class MemorySource(Enum):
    SELF_JOURNAL = "self_journal"
    SUMMARY_BALLS = "summary_balls"
    PROVENANCE_LEDGER = "provenance_ledger"
    ENTROPY_MONITOR = "entropy_monitor"
    SCAN_LOG = "scan_log"
    CUSTOM = "custom"

@dataclass
class MemoryRecord:
    source: MemorySource
    timestamp: str
    payload: Dict[str, object]
    tags: List[str] = field(default_factory=list)
    record_id: Optional[str] = None
```

**介面草案**

```python
class SoulDB(Protocol):
    def append(self, source: MemorySource, payload: Dict[str, object]) -> str:
        ...

    def stream(self, source: MemorySource, limit: Optional[int] = None) -> Iterable[MemoryRecord]:
        ...

    def list_sources(self) -> List[MemorySource]:
        ...
```

**最小可行實作**

- `JsonlSoulDB`：以 JSONL 檔案作為存儲層。
- 預設路徑位於 `memory/` 目錄。
- 仍保留 `memory/provenance_ledger.jsonl`、`memory/self_journal.jsonl` 作為核心白名單。

**遷移策略**

1. 先在 `tonesoul/memory/soul_db.py` 提供 `JsonlSoulDB`。
2. 新增存取點時改走 `SoulDB` 介面。
3. 逐步遷移現有檔案式讀寫（例如 `memory/rag_token_gate.py`）。
