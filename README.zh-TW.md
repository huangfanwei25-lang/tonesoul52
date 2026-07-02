# ToneSoul / 語魂

> ToneSoul 是一套 AI 輸出治理與問責層。
> 它不承諾讓模型變成真理來源；它把模型輸出放進可讀、可跑、可追溯的治理流程裡。

> Purpose: 語魂公開倉庫中文入口，說明目前架構、治理姿態、證據邊界與實作入口。
> Last Updated: 2026-06-17

[English](README.md)

## 90 秒看懂

ToneSoul 的核心不是「讓 AI 更會回答」，而是讓 AI 的輸出在送出前留下可審查的痕跡：誰反對、為什麼反對、哪些 claim 超過邊界、哪些只是 advisory 訊號。

它目前做三件事：

- **邊界檢查**：`AXIOMS.json` 宣告不應靜默跨越的 claim 類型，例如意識宣稱、安全認證、法律證明語言。
- **保留分歧**：Council 會保留 Guardian、Analyst、Critic、Advocate、Axiomatic 的意見和 evidence-chain branch，而不是把分歧磨平成一段順滑答案。
- **證據分級**：文件與 status artifact 會區分已測試、runtime 已存在、文件約束、哲學命題，避免把設計願望說成已驗證能力。

## 它不是什麼

ToneSoul 不能被描述成：

- 真理神諭
- 防越獄保證
- 內建道德編譯器
- AI 協作者有意識的證明
- model-side alignment、人類審查、domain verifier 的替代品

目前的真實邊界很窄：許多 gate 仍是 lexical / heuristic；較新的 semantic overclaim 與 intent-proportionality 類訊號是 advisory、record-only；`AXIOMS.json` 目前沒有任何 axiom class 達到最強執行層級。egress gate characterization 是測量目前 gate 行為，不是安全宣稱。

## 目前已有的東西

| Surface | 目前姿態 |
|---|---|
| Council deliberation | runtime 已存在，機制層有測試；五個 perspective 是同一 draft 上的 heuristic voters，不是五個獨立心智。 |
| Output gates | 依 gate 類型可 block、refine、record；有些是 required，有些只是 telemetry 或 advisory。 |
| Evidence chains | verdict 會留下 branch label，讓 reviewer 看得出 gate 為什麼反應。 |
| Memory / continuity | decay、crystallization、handoff、session surface 已存在，但效果宣稱要保持保守。 |
| Advisory sensors | semantic overclaim、intent proportionality 類訊號預設只記錄，不自動阻擋。 |
| Egress characterization | 用 sanitized fixtures 測目前 gate 行為；生成報告在 `docs/status/egress_gate_characterization_latest.json`。 |

## 快速開始

先看瀏覽器 demo：

[https://fan1234-1.github.io/tonesoul52/demo/](https://fan1234-1.github.io/tonesoul52/demo/)

安裝：

```bash
pip install tonesoul52

# 若你要使用這個 repo 的最新狀態，改用 source install
git clone --depth 1 https://github.com/Fan1234-1/tonesoul52.git
cd tonesoul52
pip install -e .
```

跑機制層 demo：

```bash
python examples/quickstart.py
```

確認 governance state 可載入：

```python
from tonesoul.runtime_adapter import load

posture = load()
print(f"Soul Integral: {posture.soul_integral}")
print(f"Active Vows: {len(posture.active_vows)}")
```

開發測試：

```bash
pip install tonesoul52[dev]
pytest tests/ -v
```

## 選你的入口

| 讀者 | 先看 | 再看 | 原因 |
|---|---|---|---|
| 開發者 | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | [docs/foundation/README.md](docs/foundation/README.md)、[docs/README.md](docs/README.md) | 先安裝，再讀最薄 project packet，最後走策展式 docs gateway。 |
| 研究者 | [DESIGN.md](DESIGN.md) | [docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md](docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md) | 先抓設計中心，再看完整 subsystem map。 |
| AI agent | [docs/AI_QUICKSTART.md](docs/AI_QUICKSTART.md) | `python scripts/start_agent_session.py --agent <your-id>`、[AI_ONBOARDING.md](AI_ONBOARDING.md) | 先走 operational first hop，再做 session handshake，避免直接 bulk-read 或亂改共享路徑。 |
| 一般讀者 | 這份 README | [SOUL.md](SOUL.md)、[LETTER_TO_AI.md](LETTER_TO_AI.md) | 先看公開姿態，再看身份與意圖層。 |

## 證據誠實

當這個 repo 說 ToneSoul「有某能力」時，請用這個分級讀：

- `E1 test-backed`：有回歸測試支撐，CI 應能抓到退化。
- `E3 runtime-present`：程式存在且能跑，但測試深度或真實使用證據仍薄。
- `E4 document-backed`：contract / spec 描述了意圖，但 runtime 尚未證明。
- `E5 philosophical`：設計命題或哲學壓力，不是已驗證機制。

如果這個區分很重要，先讀 [docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)。

Claim 邊界（機制層 / 可觀察層 / 詮釋層怎麼分、什麼話不能寫進入口文件）以 [docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md](docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md) 為準。

## 品質快照

| 指標 | 數值 |
|---|---|
| 測試 | 7,778 collected / 7,777 passing / 1 skipped，2026-06-16 clean-CI 驗證 |
| `tonesoul/` 已測模組 | 166 / 204 |
| 程式碼行數 | 72,631 across 235 files |
| bare `except:` / TODO / FIXME | 0 / 0 / 0 |
| 紅隊發現 | 18 found, 17 fixed, 1 deferred |
| 預設 CI gate | `ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` |

## 授權

Apache-2.0
