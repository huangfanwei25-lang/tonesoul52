# ToneSoul 核心模組架構圖（含中文註解與檔名）

```mermaid
flowchart TD
    A[tonesoul/unified_pipeline.py<br>統一流程組裝] --> B[tonesoul/governance/kernel.py<br>治理決策核心]
    A --> C[tonesoul/council/runtime.py<br>多視角審議主流程]
    A --> D[tonesoul/tension_engine.py<br>張力引擎]
    A --> E[tonesoul/memory/semantic_graph.py<br>語意圖譜]
    A --> F[tonesoul/memory/crystallizer.py<br>決策結晶化]
    A --> G[tonesoul/memory/soul_db.py<br>記憶資料庫]
    A --> H[tonesoul/memory/boot.py<br>記憶啟動流程]
    A --> I[tonesoul/council/pre_output_council.py<br>輸出前審議]
    C --> J[tonesoul/deliberation/engine.py<br>三方審議引擎]
    E --> F
    F --> G
    H --> G
    H --> F
    B --> D
    C --> I
    B --> C
    D --> C
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style C fill:#bbf,stroke:#333,stroke-width:1px
    style D fill:#bbf,stroke:#333,stroke-width:1px
    style E fill:#bfb,stroke:#333,stroke-width:1px
    style F fill:#bfb,stroke:#333,stroke-width:1px
    style G fill:#bfb,stroke:#333,stroke-width:1px
    style H fill:#bfb,stroke:#333,stroke-width:1px
    style I fill:#bbf,stroke:#333,stroke-width:1px
    style J fill:#bbf,stroke:#333,stroke-width:1px
    %% 中文註解：紫=主流程，藍=治理/審議/張力，綠=記憶體系統
```

---

# 檔案：README.md

```mermaid
graph TD
    A[主程式/應用層 (README.md)] --> B[模組層]
    B --> C[核心層]
    C --> D[法規層]
    D --> E[資料層]

    classDef comment fill:#fffbe6,stroke:#bfa,stroke-width:1px;
    Comment1["應用層：對外 API 與主流程入口"]:::comment
    A --> Comment1
```

---
# 檔案：docs/MODULE_DEPENDENCIES.md

```mermaid
graph TD
    A[應用層 (main.py, spine_system.py, API endpoints)] --> B[模組層 (codex, integrity, spine-ts, ethics/protocol)]
    B --> C[核心層 (thinking, reasoning, governance, dreaming)]
    C --> D[法規層 (constitution.json, AXIOMS.json, semantic_spine_schema)]
    D --> E[資料層 (knowledgebase, chromadb, ledger.jsonl)]

    classDef comment fill:#fffbe6,stroke:#bfa,stroke-width:1px;
    Comment2["模組層：功能模組，負責主要邏輯"]:::comment
    Comment3["核心層：推理、治理、思考等核心邏輯"]:::comment
    Comment4["法規層：規範、約束、不可變公理"]:::comment
    Comment5["資料層：知識庫、資料庫、紀錄檔"]:::comment
    B --> Comment2
    C --> Comment3
    D --> Comment4
    E --> Comment5
```

---
# 檔案：tonesoul/__init__.py

```mermaid
graph TD
    A[tonesoul/__init__.py]
    A --> B[UnifiedController]
    classDef comment fill:#fffbe6,stroke:#bfa,stroke-width:1px;
    Comment6["UnifiedController：統一控制進入點"]:::comment
    B --> Comment6
```

---
# 檔案：tonesoul/zone_registry.py

```mermaid
graph TD
    A[tonesoul/zone_registry.py]
    A --> B[Zone Registry]
    B --> C[session_traces.jsonl]
    B --> D[zone_registry.json]
    B --> E[governance_state.json]
    classDef comment fill:#fffbe6,stroke:#bfa,stroke-width:1px;
    Comment7["Zone Registry：主題分區與視覺化映射"]:::comment
    C --> Comment7
```

---
# 檔案：tonesoul/ystm/__init__.py

```mermaid
graph TD
    A[tonesoul/ystm/__init__.py]
    A --> B[demo, diff, render, ...]
    classDef comment fill:#fffbe6,stroke:#bfa,stroke-width:1px;
    Comment8["YSTM 子模組：demo、差異比對、渲染等"]:::comment
    B --> Comment8
```

---
# 檔案：tonesoul/ystm/demo.py

```mermaid
graph TD
    Demo[demo.py]
    Demo --> Audit[.audit]
    Demo --> Energy[.energy]
    Demo --> Ingest[.ingest]
    Demo --> Projection[.projection]
    Demo --> Render[.render]
    Demo --> Representation[.representation]
    Demo --> Schema[.schema]
    Demo --> Terrain[.terrain]
    classDef comment fill:#fffbe6,stroke:#bfa,stroke-width:1px;
    CommentDemo["demo.py 依賴多個子模組，負責組合審計、能量、資料投影、渲染等功能"]:::comment
    Demo --> CommentDemo
```

---
# 檔案：tonesoul/store.py, tonesoul/backends/redis_store.py

```mermaid
graph TD
    Store[store.py]
    Store --> RedisStore[backends/redis_store.py]
    Store --> FileStore[backends/file_store.py]
    RedisStore --> RedisClient[redis.Redis]
    RedisStore --> KEY_GOVERNANCE[ts:governance]
    RedisStore --> KEY_ZONES[ts:zones]
    RedisStore --> STREAM_TRACES[ts:traces]
    RedisStore --> CHANNEL_EVENTS[ts:events]
    classDef comment fill:#fffbe6,stroke:#bfa,stroke-width:1px;
    CommentRedis["store.py 會自動偵測 Redis，若可連線則用 RedisStore，否則用 FileStore。RedisStore 會將治理狀態、分區、session trace 等寫入 Redis，並支援 pub/sub。"]:::comment
    RedisStore --> CommentRedis
```

---
# 檔案：scripts/migrate_to_redis.py

```mermaid
graph TD
    Migrate[migrate_to_redis.py]
    Migrate --> RedisStore
    Migrate --> FileStore
    classDef comment fill:#fffbe6,stroke:#bfa,stroke-width:1px;
    CommentMigrate["migrate_to_redis.py 用於將現有 JSON 檔案資料批次遷移到 Redis，需先啟動 Redis 伺服器"]:::comment
    Migrate --> CommentMigrate
```

---
# 測試 ToneSoul runtime_adapter 記憶存取

```python
from tonesoul.runtime_adapter import load, commit, SessionTrace

# 1. 載入治理狀態，標記 agent_id
posture = load(agent_id="test-copilot-2026-03-26")
print("[載入後 posture]")
print(posture)

# 2. 留下一段測試記憶
commit(SessionTrace(
    agent="test-copilot-2026-03-26",
    tension_events=[{"topic": "copilot 測試記憶", "severity": 0.2, "type": "test", "resolution": "測試成功"}],
    key_decisions=["copilot 實際寫入測試記憶，驗證 load/commit 流程"],
))
print("[已寫入測試記憶]")
```

# 預期效果
# - governance_state.json 會新增一筆 tension_history
# - memory/autonomous/session_traces.jsonl 會新增一筆 session trace
# - 可用 summary(posture) 查看摘要

---
> 本檔案分批補充，每個區塊標明來源檔名，方便搜尋與比對。
> 若需更細緻的 import 關係，請指定檔案或資料夾.
