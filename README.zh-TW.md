# ToneSoul / 語魂

> 這不是只會回答的 AI。它會先檢查語義偏移、記住真正重要的事，並留下可追溯紀錄。
> 如果你要的是「AI 不會亂講話」，這個專案就是為這件事做的。
>
> ToneSoul 也是一套給 AI 治理、倫理記憶系統、verifier-first agents、知識圖譜檢索、adapter-ready semantic governance 研究用的外部化認知架構。
>
> Purpose: 語魂公開倉庫入口，說明整體架構、治理方向與實作入口。
> Last Updated: 2026-03-22

[English](README.md)

## 檢索關鍵字

AI governance、ethical AI、semantic governance、cognitive architecture、externalized cognition、
cognitive operating system、verifier-first agents、self-auditing AI、agent memory、memory graph、
knowledge graph retrieval、multi-agent deliberation、runtime alignment、local-first AI、
adapter-ready architecture、LoRA-ready distillation。

## 30 秒看懂它能做什麼

| 功能 | 你實際得到什麼 |
|---|---|
| 🧠 會遺忘的記憶系統 | 用指數衰減 + 結晶化，重點留下、雜訊淡出。 |
| ⚡ 張力引擎 | 每次輸出都先算語義偏移，偏了就攔。 |
| 🎭 多角色審議 | 哲學家、工程師、守門者先辯論，再給答案。 |
| 🔮 共鳴判定 | 分得出「真的理解」和「只是附和」。 |
| 🛡️ 自我治理 | 高風險或不一致輸出會被阻擋或改寫，且全程可稽核。 |
| 📊 即時儀表板 | 即時看結晶規則、共鳴統計、記憶與修復訊號。 |

## 5 分鐘快速啟動

### 1) 安裝依賴

```bash
pip install -r requirements.txt
```

### 2) 建立本地環境變數檔

```bash
cp .env.example .env.local
```

PowerShell：

```powershell
Copy-Item .env.example .env.local
```

### 3) 啟動儀表板

```bash
python scripts/tension_dashboard.py --work-category research
```

## 為什麼它跟一般 AI 不同

| | 傳統 AI | Prompt Engineering | ToneSoul |
|---|---|---|---|
| 記憶 | 單次對話就忘 | 靠人手動接記憶 | 自動衰減 + 結晶 |
| 一致性 | 看運氣 | 看 prompt 品質 | 7 條公理 + 治理檢查 |
| 自我檢查 | 幾乎沒有 | 可做可不做 | 每次都跑 TensionEngine |
| 學習方式 | 沒有 | 人工調參 | 共鳴事件沉澱成規則 |
| 稽核能力 | 弱 | 弱 | journal + provenance 可追溯 |

## 畫面

![ToneSoul Dashboard](docs/images/dashboard_preview.png)

## 2 分鐘看懂架構

ToneSoul 不應只被理解成 prompt stack，而應被理解成一套 externalized cognitive operating system。
正典架構文件在
[`docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`](docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md)。
如果你要看從舊六層 runtime 到新模型外掛路線的銜接圖，請再讀
[`docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`](docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md)。
如果你要看更具體的操作邊界，請再讀
[`docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`](docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md)
與
[`docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`](docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md)。
如果你要直接看較短、可機器讀取的鏡像，請再開
[`docs/status/l7_retrieval_contract_latest.json`](docs/status/l7_retrieval_contract_latest.json)
與
[`docs/status/l8_distillation_boundary_latest.json`](docs/status/l8_distillation_boundary_latest.json)。
如果你要直接看第一版可執行的操作層 packet / gate，請再開
[`docs/status/l7_operational_packet_latest.json`](docs/status/l7_operational_packet_latest.json)
與
[`docs/status/l8_adapter_dataset_gate_latest.json`](docs/status/l8_adapter_dataset_gate_latest.json)。
如果你要看論述邊界、防止理論偷渡機制的治理規則，請再開
[`docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`](docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md)
與
[`docs/status/abc_firewall_latest.json`](docs/status/abc_firewall_latest.json)。
如果你要整理同名文件、鏡像文件與缺少用途/日期的入口檔，先看
[`docs/status/doc_convergence_inventory_latest.json`](docs/status/doc_convergence_inventory_latest.json)
與
[`docs/plans/doc_convergence_cleanup_plan_2026-03-22.md`](docs/plans/doc_convergence_cleanup_plan_2026-03-22.md)。
如果你要看完整的多波次收斂總任務，請再開
[`docs/plans/doc_convergence_master_plan_2026-03-23.md`](docs/plans/doc_convergence_master_plan_2026-03-23.md)。
如果你需要更細的文件結構圖，想先分清 entrypoint、canonical anchor、contract、status lane，再看
[`docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md`](docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md)
與
[`docs/status/doc_authority_structure_latest.json`](docs/status/doc_authority_structure_latest.json)。
如果你要看這些同名異義文件被怎麼「蒸餾」成可治理規則，請看
[`docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md`](docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md)
與
[`docs/status/basename_divergence_distillation_latest.json`](docs/status/basename_divergence_distillation_latest.json)。
如果你碰到 nested private-memory shadow，先不要把它當成一般重複檔；請先開
[`docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md`](docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md)
與
[`docs/status/private_memory_shadow_latest.json`](docs/status/private_memory_shadow_latest.json)。
如果你在處理悖論案例與測試夾具，請把 [`PARADOXES/`](PARADOXES/) 視為正典案例集，並用
[`docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md`](docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md)
與
[`docs/status/paradox_fixture_ownership_latest.json`](docs/status/paradox_fixture_ownership_latest.json)
確認哪些是 exact mirror、哪些是 reduced projection。
如果你在讀工程卷冊，請把 [`docs/engineering/`](docs/engineering/) 視為 canonical owner，並用
[`docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md`](docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md)
與
[`docs/status/engineering_mirror_ownership_latest.json`](docs/status/engineering_mirror_ownership_latest.json)
確認 `law/engineering/` 的 mirror 狀態。

```text
使用者輸入
    ↓
[ToneBridge] 解析語氣、意圖與脈絡
    ↓
[TensionEngine] 計算語義偏移
    ↓
[Council] 守護者 / 分析師 / 批評者 / 倡議者審議
    ↓
[ComputeGate] approve / block / rewrite
    ↓
[ResonanceClassifier] flow / resonance / deep_resonance / divergence
    ↓
[Journal + Crystallizer] 重要的留下，雜訊慢慢忘掉
    ↓
最終輸出
```

## 規格入口順序

如果你想快速理解語魂，而不要把現行架構、代理人格設定、舊版 spec 混在一起，建議按這個順序讀：

- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - 現行北極星架構與演化方向
- `SOUL.md`
  - agent-facing 的身份 / 操作姿態層
- `MGGI_SPEC.md`
  - 形式化工程與治理規格視角
- `TAE-01_Architecture_Spec.md`
  - 較早期的架構譜系與歷史 spec 脈絡

如果它們之間有描述差異，優先順序是：

1. 正典架構文件
2. 當前 README 與 docs 索引
3. 舊 spec 作為歷史背景，不當作現況唯一依據

## 知識表面邊界

不要把所有看起來像「知識」的目錄都當成同一種權威來源。

- `knowledge/`
  - 概念、身份、學習脈絡筆記
- `knowledge_base/`
  - 本地結構化概念庫與工具（如 `knowledge.db`）
- `PARADOXES/`
  - 治理 / 紅隊式悖論 fixture，不是一般知識庫

參考：
[`docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`](docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md)

## 核心模組

### 記憶系統

- `memory/self_journal.jsonl` — 事件型記憶流
- `memory/crystals.jsonl` — 長期規則（結晶）
- `tonesoul/memory/crystallizer.py` — 規則自動萃取
- `memory/consolidator.py` — 類睡眠整併機制

### 張力與治理

- `tonesoul/tension_engine.py` — 多訊號張力計算
- `tonesoul/resonance.py` — 共鳴/順流分類
- `tonesoul/gates/compute.py` — approve/block/rewrite 決策閘門
- `tonesoul/unified_pipeline.py` — 全流程編排

### 自我博弈與驗證

- `scripts/run_self_play_resonance.py` — 自我博弈資料生成
- `scripts/run_swarm_resonance_roleplay.py` — 多角色蜂群情境
- `scripts/tension_dashboard.py` — CLI 觀測面板
- `tests/` — 全量回歸與子系統測試

## 哲學基礎（想深入再展開）

<details>
<summary>語義責任核心公理（完整 7 條見 AXIOMS.json）</summary>

以下三條是哲學基礎，完整的 7 條不可變公理定義在 <a href="AXIOMS.json">AXIOMS.json</a>。

1. Resonance：回應應來自理解，不是討好。
2. Commitment：跨回合維持可辨識的一致人格。
3. Binding Force：每次輸出都會影響下一次行為邊界。

參考：`docs/philosophy/soul_landmark_2026.md`
</details>

<details>
<summary>為什麼「會遺忘」反而更像有靈魂</summary>

如果所有訊息都等重，AI 只會越記越亂。
ToneSoul 讓低價值訊息自然衰退，把反覆驗證的重要模式結晶成規則。

白話就是：重要的事自動記住，廢話自動忘。
</details>

## 數據快照（2026-03-22）

| 指標 | 數值 |
|---|---|
| 通過測試數 | 2,610（2026-03-22 本地全量回歸） |
| `tonesoul/` 已測模組 | 186 / 186 |
| RDD 狀態 | `tests/red_team/` baseline 已啟用，但仍屬未升級到完整 blocking 的階段 |
| DDD 狀態 | curated audit 與 hygiene 已啟用；freshness 仍是明確分階段規則 |
| 機器可讀狀態 | `docs/status/repo_healthcheck_latest.json`、`docs/status/7d_snapshot.json` |
| 預設 CI 檢查 | `ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` |

## 授權

Apache-2.0
