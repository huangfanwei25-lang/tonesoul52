# ToneSoul / 語魂

> 這不是只會回答的 AI。它會先檢查語義偏移、記住真正重要的事，並留下可追溯紀錄。
> 如果你要的是「AI 不會亂講話」，這個專案就是為這件事做的。

[English](README.md)

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
| 一致性 | 看運氣 | 看 prompt 品質 | 三公理 + 治理檢查 |
| 自我檢查 | 幾乎沒有 | 可做可不做 | 每次都跑 TensionEngine |
| 學習方式 | 沒有 | 人工調參 | 共鳴事件沉澱成規則 |
| 稽核能力 | 弱 | 弱 | journal + provenance 可追溯 |

## 畫面

![ToneSoul Dashboard](docs/images/dashboard_preview.png)

## 2 分鐘看懂架構

```text
使用者輸入
    ↓
[ToneBridge] 解析語氣、意圖與脈絡
    ↓
[TensionEngine] 計算語義偏移
    ↓
[Council] 哲學家 / 工程師 / 守門者審議
    ↓
[ComputeGate] approve / block / rewrite
    ↓
[ResonanceClassifier] flow / resonance / deep_resonance / divergence
    ↓
[Journal + Crystallizer] 重要的留下，雜訊慢慢忘掉
    ↓
最終輸出
```

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
<summary>語義責任三公理</summary>

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

## 數據快照（2026-03-03）

| 指標 | 數值 |
|---|---|
| 通過測試數 | 1,156 |
| Journal 條目 | 11,242 |
| 啟用中的結晶規則 | 3 |
| Resonance 收斂次數 | 28 |
| Flow 偵測次數 | 39 |
| 修復事件追蹤數 | 74 |
| `unified_pipeline.py` 規模 | 1,517 行 |
| 七悖論 fixture 數 | 7 |

## 授權

Apache-2.0
