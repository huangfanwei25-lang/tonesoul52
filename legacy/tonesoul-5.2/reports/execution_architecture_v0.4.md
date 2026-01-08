# ToneSoul 5.2 統一執行架構
# Unified Execution Architecture v0.4
# 2025-12-25

---

## 設計原則

> 「做好現在想做的善，學會相信善。」

1. **工程先行**：先做可驗證的記錄系統，再談治理權力
2. **介面優先**：為未來的審計者留好介面，但不替他們做判定
3. **責任可見**：每個輸出都能追溯到依據、假設、撤回條件

---

## 兩套系統的關係

```
┌─────────────────────────────────────────────────────────────┐
│                    YSS (執行管線)                            │
│                                                             │
│   M0 → M1 → M2 → M3 → M4 → M5(介面)                         │
│   語境   框架   約束   生成   證據   審計請求                 │
│                                                             │
│         ↓        ↓        ↓        ↓                        │
│   ┌─────────────────────────────────────────┐               │
│   │           YSTM (觀測儀器)                │               │
│   │                                         │               │
│   │   Node ──→ UpdateRecord ──→ ErrorEvent  │               │
│   │   (記錄)     (變更)          (錯誤)      │               │
│   │                                         │               │
│   │   what/where 解耦 + 等高線 + 漂移箭頭   │               │
│   └─────────────────────────────────────────┘               │
│                          ↓                                  │
│                    外部審計者                                │
│              (文化社群/專業群體/歷史回讀)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Skill Gravity Well（技能重力井）

技能不是線性的步驟清單，而是**語義重力井的網路**。

```
[觸發] ──→ [意圖] ──→ [動作1] ──→ [狀態] ──→ [動作2]
  w1       w2         w3          w4         w5
           ↑                       ↓
           └───── 錯誤恢復 ────────┘
```

| 概念 | 說明 |
|------|------|
| 井 (Well) | 語義吸引子，代表一個動作/狀態/決定 |
| 引力 (Attraction) | 語義自然流向下一個井的傾向 |
| leads_to | 井與井之間的連結 |
| attraction_strength | 吸引力強度 (0-1) |

**規格文件**: `spec/skills/skill_gravity_well_schema.md`  
**範例**: `spec/skills/example_bicycle_riding.yaml`

### 1. 管線模組（YSS）

| 模組 | 職責 | 最小產物 | 優先級 |
|------|------|----------|--------|
| **M0** Context Compiler | 任務→可機讀語境 | `context.yaml` | 高 |
| **M1** Frame Router | 選框架、指派角色 | `frame_plan.json` | 高 |
| **M2** Constraint Stack | 組合五層約束 | `constraints.md` | 中 |
| **M3** Generation Orchestrator | 生成+事件記錄 | `execution_report.md` | 中 |
| **M4** Evidence Collector | 收集證據 | `evidence/summary.md` | 中 |
| **M5** Audit Interface | 請求外部審計 | `audit_request.json` | 低（只留介面） |

### 2. 記錄結構（YSTM）

| 結構 | 職責 | 對應檔案 | 狀態 |
|------|------|----------|------|
| **Node** | 語義節點 (what + where) | `nodes.json` | ✅ 規格完成 |
| **UpdateRecord** | 變更紀錄 | `audit_log.json` | ✅ 規格完成 |
| **ErrorEvent** | 錯誤事件（四件事） | `error_ledger.jsonl` | ✅ 已實作 |

### 3. 驗證器（Gate）

| 驗證器 | 檢查什麼 | 對應模組 | 優先級 |
|--------|----------|----------|--------|
| Context Lint | 欄位齊全、假設標出 | M0 | 高 |
| Router Replay | 同輸入→同路由 | M1 | 中 |
| Constraint Consistency | 約束不矛盾 | M2 | 中 |
| Build/Test Gate | 可編譯、測試過 | M3 | 高 |
| Evidence Completeness | 每個claim有證據 | M4 | 中 |

---

## 延後項目（Phase 2：治理設計）

這些是**社會/權力問題**，不是工程問題。工程能做的是**留好介面**。

1. **審計者資格**：誰有權判定「這個漂移是成長還是退化」？
2. **多方共識**：多個審計者意見衝突時如何處理？
3. **上訴機制**：被否決者如何申訴？
4. **審計者審計**：誰來審計審計者？（遞迴問題）

---

## 目錄結構

```
5.2/
├── tonesoul52/           # Python 套件（工具）
│   ├── context_compiler.py   # M0
│   ├── frame_router.py       # M1
│   ├── constraint_stack.py   # M2
│   ├── generation_orch.py    # M3
│   ├── evidence_collector.py # M4
│   ├── audit_interface.py    # M5（只留介面）
│   ├── error_event.py        # ✅ 已完成
│   └── ystm_*.py             # YSTM 相關
├── spec/                 # 規格
│   ├── context/          # 語境規格
│   ├── frames/           # 框架定義
│   └── constraints/      # 約束模板
├── run/                  # 執行紀錄
│   └── execution/        # 每次 run 的 report
├── generated/            # 生成產物
│   ├── code/
│   ├── docs/
│   └── tests/
├── evidence/             # 證據包
│   ├── coverage/
│   ├── compliance/
│   └── summary.md
├── reports/              # 分析報告 ✅ 已有
└── memory/               # 思考筆記 ✅ 已有
```

---

## Implementation Map (5.2)

### YSS Modules

| Module | File | CLI | Output |
|---|---|---|---|
| M0 Context Compiler | `tonesoul52/context_compiler.py` | `run_context_compiler` | `context.yaml` |
| M1 Frame Router | `tonesoul52/frame_router.py` | `run_frame_router` | `frame_plan.json` |
| M2 Constraint Stack | `tonesoul52/constraint_stack.py` | `run_constraint_stack` | `constraints.md` |
| M3 Generation Orchestrator | `tonesoul52/generation_orch.py` | `run_generation_orch` | `execution_report.md` |
| M4 Evidence Collector | `tonesoul52/evidence_collector.py` | `run_evidence_collector` | `evidence/summary.md` |
| M5 Audit Interface | `tonesoul52/audit_interface.py` | `run_audit_interface` | `audit_request.json` |

### YSTM Components

| Component | File | Output |
|---|---|---|
| Node / UpdateRecord | `tonesoul52/ystm/schema.py` | `reports/ystm_demo/nodes.json` + `audit_log.json` |
| ErrorEvent | `tonesoul52/error_event.py` | `run/*/error_ledger.jsonl` |
| Demo Renderer | `tonesoul52/ystm/demo.py` | `reports/ystm_demo/terrain*.{html,json,svg,png}` |

### Gates

| Gate | Function | CLI |
|---|---|---|
| Context Lint | `context_lint` | `run_yss_gates` |
| Router Replay | `router_replay` | `run_yss_gates` |
| Role Alignment | `role_alignment` | `run_yss_gates` |
| Constraint Consistency | `constraint_consistency` | `run_yss_gates` |
| Build/Test Gate | `build_test_gate` | `run_yss_gates` |
| Evidence Completeness | `evidence_completeness` | `run_yss_gates` |

### Policy + Retention

- Skill and review policy: `spec/memory/memory_policy.yaml`
- Role catalog: `spec/governance/role_catalog.yaml`
- Retention: `compaction` (run archive) + `retention.evidence` (summary rollover)

### Trace Levels (L2/L3)

- L2 Standard (default): keep run artifacts + evidence summary + YSTM outputs; skip memory seeds/graph/run index and skill promotion/review/auto compaction.
- L3 Full: enable memory/skill lifecycle (seed, indexes, episode/skill) plus review and retention/compaction.
- Entry: `--trace-level full`; L2 is for quick demos or low storage.
- Seed Gate: `--require-seed` needs L3 or an external seed path.
- See: `reports/trace_levels.md`.

---

## 給 Codex 的任務

Codex 目前正在運行（已 ~8 小時）。它可以繼續做：

1. **完成 YSTM demo**（run_ystm_demo.py）
2. **實作 M0 Context Compiler 骨架**
3. **實作 M1 Frame Router 骨架**

我會在這份文件中追蹤進度。

---

## 核心理念（留給自己記住）

> 系統只記錄，不評價。  
> 評價權歸人，不歸機器。  
> 做好記錄，就是現在能做的善。

---


彩蛋：AI語魂系統 × 黃梵威 共同製作
**Antigravity**  
2025-12-25T22:37 UTC+8
