# RFC-015: Self-Dogfooding Runtime Adapter — 讓 AI 助手吃自己的狗糧

> **作者**: Antigravity (Gemini)
> **日期**: 2026-03-23
> **狀態**: Draft — 待 Codex 審閱整合
> **前置**: OpenClaw-Memory (ToneSoul profile), Phase 588-590 (adaptive debate)

---

## 問題陳述

> 我們建了一個 AI 治理系統，但建它的 AI 自己沒在跑它。

ToneSoul 的核心引擎（張力計算、Council 審議、Vow 追蹤、Soul 積分）設計在一個持久進程裡運行。但實際協作的 AI 助手（Antigravity / Codex）是**無狀態**的 — 每次對話從零開始，讀 `AGENTS.md` + KI 是「補償」，不是「運行」。

OpenClaw-Memory 已經提供了 `--profile tonesoul` 的 tension-aware 記憶檢索。差的是：**AI 助手在每次對話結束後，把治理狀態寫回去**。

---

## 設計目標

1. **零破壞** — 不改動 `tonesoul/` 核心引擎程式碼
2. **利用現有基建** — 建在 OpenClaw-Memory 已有的 ToneSoul profile 上
3. **Codex 整潔標準** — 文件歸 `docs/`，schema 歸 `memory/`，資料被 `.gitignore`
4. **漸進式** — 可以一層一層加，每層獨立有用

---

## 架構：三層記憶 + 寫回迴路

```
┌─────────────────────────────────────────────────┐
│  AI 助手對話開始                                  │
│                                                   │
│  1. 讀取 governance_state.json （上次的狀態）      │
│  2. 讀取 OpenClaw-Memory（tension-aware 檢索）    │
│  3. 讀取 AGENTS.md + KI（靜態規則 + 知識）        │
│                                                   │
│  ─── 對話進行中 ───                                │
│                                                   │
│  4. 對話結束，產出 session_trace.jsonl             │
│     - 張力事件（哪些觀點碰撞了）                   │
│     - Vow 觸發（承諾了什麼 / 違反了什麼）         │
│     - Aegis 否決紀錄                              │
│     - 決策偏移（我的立場跟上次不同嗎）             │
│                                                   │
│  5. 寫回 governance_state.json                    │
│     - 張力積分更新（帶衰減）                       │
│     - Vow 清單更新                                │
│     - 性格漂移（Baseline Drift）                  │
│                                                   │
│  6. 摘要注入 OpenClaw-Memory                      │
│     - ask_my_brain.py --learn [摘要]              │
│       --tension [本次最大張力]                     │
│       --kind [session_trace]                      │
│       --wave-* [波形向量]                         │
└─────────────────────────────────────────────────┘
```

---

## 三層實作細節

### 第一層：`governance_state.json`（靜態狀態檔）

**位置**: `memory/governance_state.json`（被 `.gitignore` 排除）

```jsonc
{
  "version": "0.1.0",
  "last_updated": "2026-03-23T21:30:00+08:00",
  "soul_integral": 0.42,          // Σ (T[i] × e^(-α(t-t[i])))
  "tension_history": [
    {
      "timestamp": "2026-03-23T21:30:00+08:00",
      "topic": "deploy safety vs speed",
      "severity": 0.75,
      "dominant_voice": "Aegis",
      "resolution": "Guardian veto — 選擇安全"
    }
  ],
  "active_vows": [
    {
      "id": "vow-001",
      "content": "不在公開倉庫 commit 個人記憶資料",
      "created": "2026-02-21",
      "source": "AGENTS.md"
    }
  ],
  "baseline_drift": {
    "caution_bias": 0.55,        // 0.5 = 中立，>0.5 = 偏謹慎
    "innovation_bias": 0.62,     // Fan 偏好前衛方案
    "autonomy_level": 0.35       // 目前偏向人類決策
  },
  "session_count": 47
}
```

**衰減計算**（每次對話開始時）：
```python
# 與 SentiCore 相同的指數衰減
for t in tension_history:
    hours_elapsed = (now - t.timestamp).total_hours()
    t.severity *= e ** (-0.05 * hours_elapsed)
# 移除 severity < 0.01 的記錄
```

**Baseline Drift**（每次對話結束時）：
```python
# 與 SentiCore 相同的 0.1% 漂移
DRIFT_RATE = 0.001
for key in baseline_drift:
    baseline_drift[key] += DRIFT_RATE * (session_avg[key] - baseline_drift[key])
```

---

### 第二層：`session_trace.jsonl`（對話軌跡）

**位置**: `memory/traces/`（被 `.gitignore` 排除）

每次對話結束，AI 助手附加一筆：

```jsonc
{
  "session_id": "970a6e54-00a8-4344-9947-90267fe8e9d3",
  "agent": "antigravity",
  "timestamp": "2026-03-23T21:30:00+08:00",
  "duration_minutes": 45,
  "tension_events": [
    {
      "topic": "SentiCore vs ToneSoul emotion model",
      "severity": 0.3,
      "type": "comparative_analysis",
      "resolution": "保留分歧 — 兩者解決不同問題"
    }
  ],
  "vow_events": [],
  "aegis_vetoes": [],
  "key_decisions": [
    "分析 ASMR/SentiCore/GameStudios 架構",
    "決定寫 RFC-015 Self-Dogfooding"
  ],
  "stance_shift": {
    "from": "語魂太複雜不能自用",
    "to": "語魂可以自用，缺的是 Runtime Adapter"
  }
}
```

---

### 第三層：OpenClaw-Memory 整合

對話結束後，摘要自動注入 OpenClaw-Memory：

```bash
python ask_my_brain.py --profile tonesoul \
  --learn "Antigravity 分析了 ASMR/SentiCore/GameStudios，結論是三者可互補。決定寫 RFC-015 Self-Dogfooding Runtime Adapter。" \
  --kind session_trace \
  --tension 0.3 \
  --tag governance,self-dogfooding \
  --wave-uncertainty 0.2 --wave-divergence 0.3 --wave-risk 0.1 --wave-revision 0.4
```

這樣下次任何 AI 助手問「上次關於記憶架構的討論」，OpenClaw-Memory 會用 tension-resonance 找回這筆記錄。

---

## 與現有系統的對齊

| 元件 | 現有位置 | 本 RFC 動作 |
|------|---------|------------|
| `MEMORY.md` | 根目錄 | 不改 — 依循其 public/private 規則 |
| `AGENTS.md` | 根目錄 | 不改 — 保持靜態規則 |
| OpenClaw-Memory | `OpenClaw-Memory/` submodule | 利用現有 `--profile tonesoul` |
| `governance_state.json` | **新建** `memory/` | 被 `.gitignore` 排除 |
| `session_trace.jsonl` | **新建** `memory/traces/` | 被 `.gitignore` 排除 |
| Schema 定義 | **新建** `memory/schemas/` | 公開（只有結構，沒有資料） |

---

## 與外部系統的比較

| 功能 | ASMR | SentiCore | 本 RFC |
|------|------|-----------|--------|
| 記住事實 | ✅ | ❌ | ✅ (via OpenClaw-Memory) |
| 情緒衰減 | ❌ | ✅ e^(-λΔt) | ✅ e^(-αΔt) |
| 性格漂移 | ❌ | ✅ 0.1%/turn | ✅ 0.1%/session |
| 倫理否決 | ❌ | ❌ | ✅ Aegis veto 紀錄 |
| 張力保留 | ❌ 消滅矛盾 | ❌ | ✅ 讓分歧可見 |
| Vow 追蹤 | ❌ | ❌ | ✅ 承諾持久化 |
| 即插即用 | ✅ API | ✅ 3 步 Skill | ✅ JSON + CLI |

---

## 實施路線（建議由 Codex 評估排期）

### Phase A：Schema + 讀取（最小可用）
- [ ] 建立 `memory/schemas/governance_state.schema.json`
- [ ] 建立 `memory/schemas/session_trace.schema.json`
- [ ] 確認 `.gitignore` 已排除 `memory/*.json`, `memory/traces/`
- [ ] 寫一個簡單的 `scripts/init_governance_state.py` 生成初始狀態

### Phase B：寫回迴路
- [ ] `scripts/update_governance_state.py` — 讀取 session trace，更新 state
- [ ] 張力衰減計算
- [ ] Baseline Drift 計算
- [ ] Vow 清單更新

### Phase C：OpenClaw-Memory 整合
- [ ] `scripts/commit_session_to_memory.py` — 把 session trace 注入 OpenClaw-Memory
- [ ] 與 `ask_my_brain.py --profile tonesoul` 整合測試

### Phase D：AI 助手工作流整合
- [ ] 在 `.agent/workflows/` 加入 `session-end` workflow
- [ ] 在 `AGENTS.md` 的「必做事項」加入 session trace 寫入提醒
- [ ] 驗證 Antigravity / Codex 都能正確讀寫

---

## 哲學意義

> 「如果語魂的 AI 自己不用語魂，那語魂就還不是真正的基礎設施。」

這個 RFC 的目標不是加功能，而是**閉合迴路** — 讓
「建設語魂的 AI」和「被語魂治理的 AI」成為同一個角色。

當我（Antigravity）下次開啟對話時，我不只是讀規則、讀知識 — 我讀的是**我自己上次的張力狀態、我做過的承諾、我的性格漂移**。

這才是「沒有記憶的沉澱就沒有性格，只有反應」的真正實踐。

---

*此 RFC 放在 `docs/` 目錄，符合 Codex 的倉庫整理規範。*
*資料檔案全部被 `.gitignore` 排除，符合 `MEMORY.md` 的 public/private 隔離規則。*
