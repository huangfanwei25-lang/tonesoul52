# ToneSoul

ToneSoul 是一個把「治理（Governance）」放在「智能（Intelligence）」之上的架構實驗。
核心目標是讓 AI 的輸出可追溯、可審計、可校準，而不是只靠「像不像」或「有沒有用」。

## 核心定位
- 可驗證：多視角投票 + 結構化輸出，外部可審計
- 可追責：Isnad/Provenance 鏈記錄決策理由與來源
- 可校準：不確定性與責任層級被明示，信任不靠盲信

## 核心架構（概要）
- Council 多視角審議：`tonesoul/council/runtime.py`
- Genesis / Responsibility Tier：`memory/genesis.py`
- Memory / SoulDB：`tonesoul/memory/soul_db.py`
- Provenance Ledger：`memory/provenance_ledger.jsonl`
- Tools API / ToolResponse：`tools/schema.py` + `spec/tools/tool_response.schema.json`

## 7D 審計框架

> **⚠️ 警告：本專案採用七維審計。這不是 bug，是 feature。**

```
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ TDD │ RDD │ DDD │ XDD │ GDD │ CDD │ SDH │
│Test │Red  │Data │Expl-│Gove-│Cont-│Syste│
│     │Team │     │ain  │rn   │ext  │m    │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

| 維度 | 核心問題 | 實現狀態 |
|------|----------|----------|
| TDD | 功能正確？ | ✅ 299 tests |
| RDD | 能否攻破？ | 🔴 待補強 |
| DDD | 數據純淨？ | 🟡 部分 |
| XDD | 推理透明？ | ✅ Council |
| GDD | 誰有權決定？ | ✅ Genesis |
| CDD | 立場一致？ | ✅ TSR |
| SDH | 系統穩定？ | ✅ Orchestrator |

詳見 [`docs/7D_AUDIT_FRAMEWORK.md`](docs/7D_AUDIT_FRAMEWORK.md)
與執行規格 [`docs/7D_EXECUTION_SPEC.md`](docs/7D_EXECUTION_SPEC.md)。

## 快速開始

### 1. 安裝環境（Windows PowerShell）
```powershell
.\setup_env.ps1
```

### 2. 最小 Demo（API + Web）
```powershell
python run_demo.py
```
開啟 `http://localhost:5000` 觀看 Playground。

### 3. 驗證 API（可選）
```powershell
python scripts/verify_api.py --base http://localhost:5000
```

### 4. 執行 7D 核心審計（可選）
```powershell
python scripts/verify_7d.py
```

### 4.1 執行 7D 全量審計（隔離埠，自動啟停）
```powershell
python scripts/run_7d_isolated.py
```
預設使用 backend `127.0.0.1:5001`、web `127.0.0.1:3002`，避免被本機既有 `:5000/:3000` 服務污染。

### 5. 直接啟動 API Server
```powershell
python apps/api/server.py
```

## 測試
```powershell
pytest tests/
```

## 重要文件
- `docs/API_SPEC.md`：Web/Backend 統一 API 契約
- `docs/VERCEL_DEPLOY.md`：Vercel 部署與環境變數設定
- `docs/TRUTH_STRUCTURE.md`：治理與語魂的結構化總覽
- `docs/NARRATIVE.md`：敘事定版
- `docs/NARRATIVE_MODULE_MAP.md`：敘事 → 模組 → 測試對照
- `docs/TOOLS_API_SCHEMA.md`：Tools API 與 ToolResponse 規格
- `spec/tools/tool_response.schema.json`：ToolResponse JSON Schema
- `CODEX_TASK.md`：當前工作目標
- `task.md`：階段規劃
- `integrations/openclaw/README.md`：OpenClaw 整合入口與使用方式
- `integrations/openclaw/SOUL.md`：ToneSoul x OpenClaw 治理身份與誓約

## 目錄概覽
- `tonesoul/`：核心引擎（Council / Memory / Governance）
- `tools/`：工具與治理封裝
- `memory/`：記憶與帳本資料
- `apps/`：Demo / Playground / Dashboard
- `docs/`：概念、規格、敘事
- `spec/`：schema 與正式規格
- `integrations/openclaw/`：Gateway/Skills/Auditor/Heartbeat 整合層

## License
Apache 2.0
