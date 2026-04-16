# ToneSoul / 語魂

> 這不是只會回答的 AI。它會先檢查語義偏移、記住真正重要的事，並留下可追溯紀錄。
> 如果你要的是「AI 不要一本正經亂講話」，這個專案就是為這件事做的。
>
> ToneSoul 是一套外部化認知治理架構，關心的是可挑戰、可追溯、可稽核的 AI，而不是只追求更順的回答。
>
> Purpose: 語魂公開倉庫中文入口，說明整體架構、治理姿態與實作入口。
> Last Updated: 2026-04-14

[English](README.md)

## 30 秒看懂它做什麼

| 功能 | 你實際得到什麼 |
|---|---|
| 🧠 會遺忘的記憶系統 | 指數衰減 + 結晶化，重點留下、雜訊淡出 |
| ⚡ 張力引擎 | 每次輸出都先檢查語義偏移，偏了就攔 |
| 🎭 多角色審議 | 守護者、分析師、批評者、倡議者先辯論，再給答案 |
| 🛡️ 自我治理 | 高風險或不一致輸出會被阻擋或改寫，而且全程可稽核 |
| 📊 即時儀表板 | 看結晶規則、共鳴統計、記憶與修復訊號 |

## 5 分鐘快速啟動

### 1) 安裝

```bash
pip install tonesoul52
```

或從原始碼安裝：

```bash
git clone --depth 1 https://github.com/Fan1234-1/tonesoul52.git
cd tonesoul52
pip install -e .
```

### 2) 跑 demo

```bash
python examples/quickstart.py
```

### 3) 驗證治理狀態有載入

```python
from tonesoul.runtime_adapter import load

posture = load()
print(f"Soul Integral: {posture.soul_integral}")
print(f"Active Vows: {len(posture.active_vows)}")
```

### 4) 啟動儀表板（選用）

```bash
pip install tonesoul52[dashboard]
python scripts/tension_dashboard.py --work-category research
```

### 5) 跑測試

```bash
pip install tonesoul52[dev]
pytest tests/ -v
```

## 30 秒系統地圖

ToneSoul 不是單一 prompt，也不是單純的記憶外掛。
它比較像一套把治理、審議、連續性、證據與觀測外部化的 AI 架構。

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
[Journal + Crystallizer] 重要的留下，雜訊慢慢忘掉
    ↓
最終輸出
```

如果你只想看一份能解釋整個堆疊的文件，先開 [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md)。
如果你要看設計中心與不該漂移的 invariant，先開 [DESIGN.md](DESIGN.md)。
如果你要先看最薄、最適合人類與 AI 重新進場的專案 packet，先開 [docs/foundation/README.md](docs/foundation/README.md)。

## 選你的入口

| 讀者 | 先讀 | 再讀 | 為什麼 |
|---|---|---|---|
| 開發者 | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | [docs/foundation/README.md](docs/foundation/README.md) -> [docs/README.md](docs/README.md) | 先安裝，再讀薄 packet，還不清楚時才進 curated docs gateway |
| 研究者 | [DESIGN.md](DESIGN.md) | [docs/foundation/README.md](docs/foundation/README.md) -> [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md) | 先抓設計中心，再補 bounded packet，最後看整體地圖 |
| AI 代理 | [docs/AI_QUICKSTART.md](docs/AI_QUICKSTART.md) | `python scripts/start_agent_session.py --agent <your-id>` -> [AI_ONBOARDING.md](AI_ONBOARDING.md) | 先走 operational first hop，再做 session handshake，最後才進 routing map |
| 一般讀者 | [README.md](README.md) | [SOUL.md](SOUL.md) -> [LETTER_TO_AI.md](LETTER_TO_AI.md) | 先看公共入口，再看身份與意圖層 |

一次只先開一個 owner surface，不要整列一起讀。
[docs/README.md](docs/README.md) 是策展式入口。
[docs/INDEX.md](docs/INDEX.md) 是完整索引，只有在策展入口還不夠時再開。

## 證據誠實

當 README 說 ToneSoul「有某個能力」時，請用這個濾鏡讀：

- `E1 test-backed`：有回歸測試支撐，CI 能抓到退化
- `E3 runtime-present`：程式存在也能跑，但測試深度還不夠
- `E4 document-backed`：有 contract / spec 描述，但 runtime 仍未完全證明
- `E5 philosophical`：是設計命題或哲學壓力，不是已驗證機制

如果這個差異很重要，先開 [docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)。

## 公式誠實

入口文件裡出現的公式或符號，預設都只是 orientation aid，不是 executable owner。
如果你需要知道某個公式到底是 rigorous、heuristic 還是 conceptual，先看 [docs/GLOSSARY.md](docs/GLOSSARY.md) 和 [docs/MATH_FOUNDATIONS.md](docs/MATH_FOUNDATIONS.md)。

## 品質快照（2026-04-13）

| 指標 | 數值 |
|---|---|
| 通過測試數 | 3,137（Python 3.13，Windows / Ubuntu） |
| `tonesoul/` 已測模組 | 166 / 204（81%） |
| 程式碼行數 | 72,631 行 / 235 檔 |
| bare `except:` / TODO / FIXME | 0 / 0 / 0 |
| 紅隊發現 | 18 個，已修 17 個，1 個延後（semantic analysis） |
| RDD 狀態 | `tests/red_team/` baseline 已啟用，但仍低於 full blocking maturity |
| DDD 狀態 | hygiene + curated audit 已啟用；freshness 仍是明確分階段規則 |
| 機器可讀狀態 | `docs/status/repo_healthcheck_latest.json`、`docs/status/7d_snapshot.json`、`docs/status/architecture_audit_2026-04-08.md` |
| 預設 CI 檢查 | `ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` |

## 授權

Apache-2.0
