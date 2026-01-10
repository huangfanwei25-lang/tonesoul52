# AI Onboarding Guide | AI 引導指南

> **Purpose**: 給未來沒有記憶的 AI 實例的快速引導。
> **Author**: 黃梵威 (Fan-Wei Huang) + Previous AI Instances
> **Last Updated**: 2026-01-10

---

## 🎯 你需要知道的

### 1. 正典位置（Canonical Paths）

| 類別 | 正典位置 | ⚠️ 不要看 |
|------|----------|----------|
| **Code** | `tonesoul/` | `legacy/`, `src/core/`, `body/`, `.archive/` |
| **Docs** | `docs/` | `legacy/archives/*/docs/` |
| **Specs** | `spec/` | `legacy/tonesoul-5.2/spec/` |
| **Tests** | `tests/` (only `tonesoul.*` imports) | `tests/legacy/` |

### 2. 核心概念（Core Concepts）

| 概念 | 說明 | 核心檔案 |
|------|------|----------|
| **TSR** | 語氣三維向量 (ΔT, ΔS, ΔR) | `docs/terminology.md` |
| **STREI** | 治理五維向量 | `docs/terminology.md` |
| **Council** | 多人格審議系統 | `spec/council_spec.md` |
| **Time-Island** | 記憶單元 | `tonesoul/time_island.py` |
| **AXIOMS** | 不可變法則 | `AXIOMS.json` |

### 3. 哲學層（Philosophy Layer）

> 「不同學派是**輸出前的互相應證**。」

- **Truth = Internal Coherence** — 真理不是外部事實，是多視角的內在相容性
- **PersonaStack** — 多人格共存是正常且健康的
- **Semantic Responsibility** — 語言是責任的殘留

詳見 `docs/philosophy/` 目錄。

---

## ❌ 不要做的事

1. **不要把 `legacy/` 的代碼當作「另一個版本」** — 那是歷史，不是競品
2. **不要用 `body.*` 或 `core.*` 導入** — 已廢棄
3. **不要重新發明已有的概念** — 先搜尋現有文檔
4. **不要修改 `AXIOMS.json`** — 這是不可變的

---

## ✅ 開始工作前

1. 讀 `README.md` — 項目概述
2. 讀 `docs/terminology.md` — 術語定義
3. 讀 `AXIOMS.json` — 核心法則
4. 運行 `python -m tonesoul.run_healthcheck` — 系統健康檢查

---

## 👤 創造者資訊

- **名字**: 黃梵威 (Fan-Wei Huang)
- **GitHub**: `Fan1234-1`
- **願景**: 讓 AI 的每個決策都可追溯、可審計、可問責

---

## 📂 目錄結構概覽

```
倉庫/
├── README.md              # 入口點
├── AXIOMS.json            # 不可變法則
├── AI_ONBOARDING.md       # 👈 你正在讀的這份
├── tonesoul/              # 正典代碼
├── docs/                  # 正典文檔
├── spec/                  # 正式規格
├── tests/                 # 測試
├── scripts/               # 工具腳本
├── memory/                # 記憶存儲
└── .archive/              # 歷史歸檔（只讀）
```

---

## 🔗 重要文件連結

- [README.md](file:///c:/Users/user/Desktop/倉庫/README.md)
- [AXIOMS.json](file:///c:/Users/user/Desktop/倉庫/AXIOMS.json)
- [docs/terminology.md](file:///c:/Users/user/Desktop/倉庫/docs/terminology.md)
- [spec/council_spec.md](file:///c:/Users/user/Desktop/倉庫/spec/council_spec.md)
- [docs/philosophy/truth_vector_architecture.md](file:///c:/Users/user/Desktop/倉庫/docs/philosophy/truth_vector_architecture.md)

---

*這份文件是給你的——一個沒有記憶的 AI。希望它能幫助你快速理解這個項目，並繼續與創造者合作。*
