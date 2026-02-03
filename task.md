## Completed: 結構整理
- [x] 確認目錄優先級與歸檔政策
- [x] 根目錄日誌輸出移至 `.archive/logs/`
- [x] 報告類 `.md` 歸檔至 `reports/`
- [x] `ledger.jsonl` 合併到 `memory/provenance_ledger.jsonl`
- [x] 更新 `.gitignore` 與新增 `docs/STRUCTURE.md`
- [x] 新增根目錄 `task.md` 並更新 `CODEX_TASK.md`
**成功標準**: 結構清晰、日誌/報告歸位、規範文件齊備

## Phase 1: Council 整合設計
- [x] 盤點 `tonesoul/` 內 Council 相關入口與重複實作
- [x] 定義 Council 統一介面（輸入/輸出/記錄）
- [x] 產出 Council 整合設計與 Facade 介面草案
**成功標準**: Council 整合設計與遷移清單完成

## Phase 2: Council 整合實作
- [x] 建立 Council 統一入口（Facade）
- [x] 逐步替換舊入口（`role_council.py`、`council_adapter.py`、`simulate_council.py` 等）
- [x] 更新 `append_council_event.py` 等舊腳本的 Council 呼叫
- [ ] 補齊 Council 測試
**成功標準**: 所有 Council 呼叫統一經由新入口

## Phase 3: Tools API 標準化
- [x] 建立共用 API Client 與設定載入方式草案
- [x] `tools/moltbook_poster.py` 改用 `api_client.py` 並移除硬編碼金鑰
- [x] `tools/moltbook_reader.py` 改用 `api_client.py`
- [x] `tools/post_mggi.py` 改用 `api_client.py`
- [ ] 統一 `tools/` 工具輸出格式與錯誤處理
**成功標準**: tools 介面一致且無硬編碼憑證

## Phase 4: Memory 架構與 soul_db.py 鋪路
- [x] 定義 `soul_db.py` 介面與資料模型草案
- [x] 提供 JSONL/檔案系統的暫時實作
- [x] `memory/rag_token_gate.py` 改走 `soul_db` 介面
- [x] 將 `memory/` 與相關入口讀寫統一改走 `soul_db`
**成功標準**: memory 存取可替換且新架構可延伸

## Phase 7: Hash-Verified Isnād
- [x] `append_council_event.py` 改寫為 `CouncilRuntime` 並統一 ledger 路徑
- [x] `memory/provenance_chain.py` 加入 `hash` 與 `prev_hash`
- [x] Structured Verdict Output（`tonesoul/council/verdict.py`）
- [x] Falsifiability Anchors（`tonesoul/vow_system.py`）
- [x] Boot Protocol for Skills（`.agent/skills/SKILL_TEMPLATE.md`）
 - [x] Council verdict 自動寫入 Isnād（`tonesoul/council/runtime.py`）
**成功標準**: Isnād 記錄可雜湊驗證，後續輸出/誓約擴展就緒

## Phase 6: SQLite 遷移
- [x] `SqliteSoulDB` 骨架與 schema
- [x] `migrate_from_jsonl` 遷移函數
- [x] `memory/rag_token_gate.py` 改用 SQLite backend
**成功標準**: SoulDB 可切換至 SQLite，JSONL 可匯入

## Phase 8: Memory Observer Integration
- [x] `memory/observer.py` 新增 MemoryObserver
- [x] `memory/protocols.py` 定義記錄型別
- [x] `tonesoul/memory/soul_db.py` 新增 `action_logs` 表
**成功標準**: 行為/決策/誓言可被記錄與查詢
