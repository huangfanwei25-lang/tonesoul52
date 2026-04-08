# ToneSoul 架構審計（2026-04-08）

> 執行者：Claude Opus 4.6
> 範圍：tonesoul/ 全部原始碼 + tests/ 覆蓋率 + 子套件健康度

---

## 1. 規模總覽

| 指標 | 數值 |
|------|------|
| Python 檔案 | 235 |
| 程式碼行數 | 72,631 |
| 程式碼大小 | 2,644 KB |
| 子套件 | 22 |
| 頂層模組 | 90 |
| 測試檔案 | 407 |
| 測試函式 | 2,880 |
| Git commits | ~850 |

---

## 2. 大檔案觀察

| 檔案 | 行數 | 大小 | 評估 |
|------|------|------|------|
| `unified_pipeline.py` | 3,587 | 148 KB | **過大** — 系統主管線，包含反思循環、Council 呼叫、vow 執行、gate 邏輯。應是下一次重構的首要目標 |
| `runtime_adapter.py` | 3,411 | 133 KB | **過大** — 狀態載入/提交/compaction/snapshot/handoff。功能多但內聚，可拆但優先級較低 |
| `dream_observability.py` | 2,431 | 94 KB | 偏大但單一職責（夢境觀測） |
| `self_improvement_trial_wave.py` | 1,524 | 88 KB | 自我改善試驗引擎，大小合理 |
| `autonomous_schedule.py` | 1,654 | 72 KB | 自主排程，大小合理 |

> **建議**：unified_pipeline.py 超過 3,500 行。長期應拆分反思循環（`_self_check`）和 Council 互動為獨立模組。但目前不影響功能，不急。

---

## 3. 程式碼品質

| 檢查項目 | 結果 |
|----------|------|
| 裸 `except:` | **0** ✓ |
| TODO / FIXME / HACK | **0** ✓ |
| 孤兒模組（從未被 import） | **1** — `ystm_demo.py`（171 bytes，相容包裝） |
| 空 `__init__.py` | **1** — `gates/__init__.py`（0 bytes） |
| 空子套件（0 個 .py 模組） | **2** — `cli/`（legacy placeholder）、`pipeline/`（backward-compat re-exports） |

### 孤兒 / Stub 處理建議

| 檔案 | 說明 | 建議 |
|------|------|------|
| `ystm_demo.py` | 指向 `ystm.demo` 的相容包裝 | 可保留（171 bytes 不影響） |
| `cli/__init__.py` | Legacy placeholder | 若無外部引用可移除 |
| `pipeline/__init__.py` | Re-exports `yss_pipeline`、`yss_gates`、`tsr_metrics` | 有用的 backward-compat shim，保留 |
| `gates/__init__.py` | 空檔案 | 加一行 docstring 或 re-export `compute` |

---

## 4. 層級違規

### 4.1 已知跨層引用

| 來源 | 目標 | 方式 | 嚴重度 |
|------|------|------|--------|
| `unified_pipeline.py` → `runtime_adapter` | `load_posture()` | 頂層 import | **低** — pipeline 依賴 adapter 是合理的方向 |
| `governance/kernel.py` ↔ `llm/router.py` | 互相引用 | 函式內 lazy import | **低** — 不會 circular ImportError，但設計上 governance 不應知道 LLM 細節 |

### 4.2 governance ↔ llm 循環

- `governance/kernel.py` line 162/174/186：lazy import `llm.create_ollama_client` 等
- `llm/router.py` line 197：lazy import `governance.kernel.GovernanceKernel`

**原因**：GovernanceKernel 需要 LLM 做 Council 審議，LLM router 需要 GovernanceKernel 做治理檢查。

**建議**：長期可用介面（Protocol / ABC）解耦，但目前 lazy import 運作正常，不急。

---

## 5. 測試覆蓋率

- **已測試模組**：166 / 204 = **81.4%**
- **未測試模組**：38

### 高優先未測試模組（>10 KB）

| 模組 | 大小 | 說明 |
|------|------|------|
| `memory_manager.py` | 25 KB | 記憶管理核心 |
| `tonebridge/personas.py` | 17 KB | 角色人格系統 |
| `ystm_demo.py → ystm/render.py` | 16 KB | YSTM 渲染 |
| `aegis_shield.py` | 15 KB | Aegis 防禦簽章 |
| `audit_interface.py` | 15 KB | 審計介面 |
| `skill_promoter.py` | 14 KB | 技能晉升 |
| `backends/redis_store.py` | 14 KB | Redis 後端 |
| `council/transcript.py` | 12 KB | Council 記錄 |
| `working_style.py` | 13 KB | 工作風格 |
| `evidence_collector.py` | 11 KB | 證據收集 |
| `tech_trace/normalize.py` | 10 KB | 技術追蹤正規化 |

### 低優先未測試模組（<5 KB，多為 perspective 子類）

`advocate.py`, `analyst.py`, `axiomatic_inference.py`, `base.py`, `critic.py`, `guardian.py`, `semantic_analyst.py`, `boot.py`, `capture.py`, `client.py`, `embedder.py`, `embeddings.py`, `context_compiler.py`, `council_cli.py`, `acceptance.py`, `audit.py`, `validate.py`, `inventory.py`, `store.py`, `unified_controller.py`

---

## 6. 子套件結構

| 子套件 | 模組數 | 健康度 | 備註 |
|--------|--------|--------|------|
| `council/` | 20 | ✓ | 最大子套件，perspective_factory 負責分派 |
| `memory/` | 19 | ✓ | soul_db, compaction, snapshot, handoff 等 |
| `ystm/` | 12 | ✓ | 遊戲化視覺模組 |
| `tonebridge/` | 11 | ✓ | 跨橋接模組 |
| `deliberation/` | 6 | ✓ | 審議引擎 |
| `llm/` | 4 | ✓ | LLM 客戶端（Ollama、LMStudio、Gemini） |
| `observability/` | 4 | ✓ | 觀測模組 |
| `inter_soul/` | 4 | ✓ | 跨魂互動 |
| `corpus/` | 3 | ✓ | 語料處理 |
| `evolution/` | 3 | ✓ | 演化模組 |
| `governance/` | 3 | ✓ | kernel + reflex + reflex_config |
| `loop/` | 3 | ✓ | 迴圈控制 |
| `market/` | 3 | ✓ | 市場模組 |
| `perception/` | 3 | ✓ | 感知模組 |
| `scribe/` | 3 | ✓ | 記錄員 |
| `tech_trace/` | 3 | ✓ | 技術追蹤 |
| `shared/` | 2 | ✓ | 共用模組 |
| `semantic/` | 2 | ✓ | 語義分析 |
| `gateway/` | 2 | ✓ | HTTP 閘道 |
| `gates/` | 1 | ⚠ | __init__.py 空白 |
| `cli/` | 0 | ⚠ | Legacy placeholder |
| `pipeline/` | 0 | ✓ | Backward-compat re-exports |

---

## 7. 架構健康總結

### 良好的地方

1. **零裸 except、零 TODO** — 程式碼紀律高
2. **81% 測試覆蓋** — 2,880 個測試函式，主要路徑都有覆蓋
3. **只有 1 個真正孤兒** — `ystm_demo.py`（171 bytes 相容包裝）
4. **子套件邊界清晰** — 22 個子套件各有明確職責
5. **治理層隔離良好** — `governance/` 只有 3 個模組（kernel, reflex, reflex_config）
6. **無跨層硬 import 循環** — 唯一的循環用 lazy import 處理

### 需要注意的地方

1. **unified_pipeline.py 過大**（3,587 行）— 長期技術債
2. **runtime_adapter.py 過大**（3,411 行）— 次優先
3. **38 個模組無測試** — 其中 11 個超過 10 KB
4. **governance ↔ llm 設計耦合** — lazy import 避免了崩潰，但概念上不理想
5. **gates/__init__.py 空白** — 小問題

### 不需要立即處理的

- `cli/` 和 `pipeline/` 空套件是 backward-compat shim，無害
- `ystm_demo.py` 孤兒太小，不值得花時間
- 重複模組名（`analyzer`, `config`, `engine`, `types`）在不同子套件中是正常的

---

## 8. 建議優先序

| 優先 | 項目 | 影響 |
|------|------|------|
| 1 | 補 `aegis_shield.py` 測試 | 安全相關，紅隊 #18 修復後應有回歸測試 |
| 2 | 補 `memory_manager.py` 測試 | 25 KB 記憶核心無測試 |
| 3 | `gates/__init__.py` 加 re-export | 1 行修復 |
| 4 | 長期：拆分 `unified_pipeline.py` | 大工程，等需要改它時順手做 |
