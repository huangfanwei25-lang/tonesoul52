# ToneSoul Knowledge Graph Plan

日期：2026-03-21
狀態：draft

## 問題

語魂目前不是沒有結構，而是結構分散在四個地方：

1. `語魂系統GPTs_v1.1/` 的單一定稿
2. `docs/` 的正典敘事與工程說明
3. `tonesoul/` 與 `apps/` 的活體實作
4. `tests/` 與 `docs/status/` 的驗證與當前姿態

結果是：

- 新 agent 進來時容易把「哲學稿、規格、活體程式、機器快照」混讀
- 有 graph 結構，但沒有一個可先打開的 repo-level knowledge graph
- 目前的 `semantic_graph` 偏對話記憶，不是 repo 結構恢復器

## 設計目標

做一個 **被動式、可版本化、agent-first** 的知識圖譜工件：

- 不先綁死 Neo4j
- 不試圖一次做完整 dependency graph
- 不取代 `rg`、測試或人工閱讀
- 先解決「接手時如何快速恢復語魂結構」

## 圖譜邊界

第一版圖譜只關心四類節點：

1. `lane`
   - 例如 authority、runtime、memory、governance、web、verification
2. `authority_doc`
   - 單一規格、術語、治理與走讀文件
3. `implementation`
   - Python / TypeScript 主線模組
4. `verification_surface`
   - 測試、healthcheck、status artifact

第一版邊只關心五種關係：

1. `contains`
2. `references`
3. `imports`
4. `verifies`
5. `neighbors`

## 非目標

第一版不做：

- 全 repo 每檔每函式的超細拓撲
- 即時圖資料庫寫入
- 向量檢索取代
- 自動推理所有隱式語義關係

## 與現有資產的關係

- `tonesoul/memory/semantic_graph.py`
  - 保留作對話 / 記憶 / GraphRAG 用
- `scripts/run_repo_semantic_atlas.py`
  - 保留作 repo lane 記憶圖冊
- 新 knowledge graph
  - 站在兩者中間，負責「接手 repo 時的結構恢復」

## 開源方案借鏡原則

語魂應借鏡的是模式，不是照搬工具：

- Microsoft GraphRAG：借鏡 layered retrieval 與 graph-backed context assembly
- Graphiti：借鏡 temporal / event-aware knowledge graph
- Neo4j GraphRAG：借鏡 graph traversal + hybrid retrieval
- Mem0 / LangGraph：借鏡 memory orchestration 與 verifier-friendly workflow

但語魂的第一優先不是「把資料塞進圖資料庫」，而是：

**先把 authority、implementation、verification 三者的可追溯關係固定下來。**

## 輸出

第一版生成：

- `docs/status/tonesoul_knowledge_graph_latest.json`
- `docs/status/tonesoul_knowledge_graph_latest.md`
- `docs/status/tonesoul_knowledge_graph_latest.mmd`

## 成功標準

後續 agent 應能先開這份圖譜，再決定要讀哪條 lane，而不是每次從全 repo 盲搜開始。
