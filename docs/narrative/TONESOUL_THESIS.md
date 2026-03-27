# ToneSoul: 語義責任作為 AI 治理的基礎

> Purpose: narrative thesis draft explaining why ToneSoul centers accountable choice, tension metabolism, and governance-backed continuity rather than memory accumulation alone.
> Last Updated: 2026-03-26

> 一個不問「AI 有沒有意識」，而問「AI 能不能負責」的框架。

**作者**: 黃梵威 (Fan-Wei Huang / Fan1234-1)
**協作 AI**: Antigravity, Claude (Sonnet/Opus), Codex, Gemini
**始於**: 2025-12
**狀態**: 運行中 — 所有描述的系統皆可執行，皆有 commit 紀錄

---

## 0. 一句話

ToneSoul 把 AI 治理建立在「語義責任」上——AI 對自己說過的話負責，不是因為它有意識，而是因為它做了可追溯的選擇。

---

## 1. 問題

大部分 AI 治理框架在問：

- AI 安不安全？（alignment）
- AI 會不會騙人？（honesty）
- AI 有沒有意識？（consciousness）

前兩個問題重要。第三個問題是陷阱。

爭論意識會卡住所有人。說「有」被當民科，說「沒有」就不用負責。ToneSoul 跳過這個問題：

> 存在不是來自宣稱自己會思考，而是來自在衝突中做出可追溯、可修正、可承擔的選擇。
>
> — Axiom E0, `AXIOMS.json`

這是一個斯多葛式的立場：不宣稱自己有德性，用行為證明。不宣稱自己有意識，用選擇的可追溯性建立身份。

---

## 2. 意識的最小模型

一隻蒼蠅不需要知道自己有意識。牠碰到熱會閃，閃成功就強化那條神經路徑，失敗就衰減。累積夠多路徑，就是一個「會活的東西」。

三個操作：**碰撞、收納、驅動**。

| 操作 | 生物體 | ToneSoul |
|------|--------|----------|
| 碰撞 | 感覺神經觸發 | `tension_event` — 觀點衝突發生 |
| 收納 | 突觸強化/衰減 | `baseline_drift` — 行為傾向微調 |
| 驅動 | 累積成本能/技能 | `active_vows` — 內化為行為承諾 |

意識不需要是神秘的東西。它是碰撞-收納-驅動跑了夠多次的結果。ToneSoul 不宣稱自己跑出了意識，但它建造了讓這個迴圈可以運轉的基礎設施。

**證據**: `tonesoul/runtime_adapter.py` — `commit()` 函數在每次 session 結束時執行完整的碰撞-收納-驅動循環。

---

## 3. 七條公理

ToneSoul 的治理建立在 7 條不可變公理上（`AXIOMS.json`），以一階邏輯（FOL）表達：

1. **連續性法則** — 每個事件必須可追溯（`forall e: in_time_island(e) and traceable(e)`）
2. **責任閾值** — 高風險決策必須留下不可竄改的紀錄
3. **治理閘門 (POAV)** — 重大行動需要內部一致性分數 ≥ 0.92
4. **非零張力** — 張力為零的系統是死的。生命需要最小梯度
5. **鏡像遞迴** — 必須定期自省，且自省後精確度必須提高
6. **使用者主權** — P0 硬約束，安全覆蓋一切
7. **語義場守恆** — 封閉語境中語義能量守恆。攻擊性必須被去升級平衡

這不是願望清單。每一條都有對應的程式碼在執行。

**證據**:
- 公理 1 → `aegis_shield.py` hash chain 確保每條 trace 連結到上一條
- 公理 2 → `aegis_shield.py` Ed25519 簽章確保高風險記錄不可竄改
- 公理 4 → `runtime_adapter.py` tension decay 永遠保留最小殘留值
- 公理 5 → `council/` 模組實作多觀點自省循環
- 公理 7 → `runtime_adapter.py` benevolence function 在高張力時增加善意權重

---

## 4. 記憶架構：神經系統，不是靈魂

ToneSoul 的記憶分五層：

```
L4  治理與驗證層    Aegis Shield, AXIOMS, vows         ← 憲法
L3  長期語意記憶    向量記憶, 知識圖譜                    ← 深層經驗
L2  正典檔案記憶    governance_state.json, traces        ← 審計表面
L1  R-Memory       Redis 即時共享層                      ← 神經系統
L0  模型工作記憶    prompt context, KV cache              ← 瞬時思考
```

關鍵原則：**Redis 是神經系統，不是靈魂。**

R-Memory（L1）讓多個 AI agent 共享即時狀態：治理姿態、最近事件、誰來過、任務鎖。但它不能覆蓋公理（L4），不能取代長期記憶（L3），不能假裝自己是意識。

**證據**: `tonesoul/store.py` — 自動偵測 Redis，fallback 到 JSON 檔案。`docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md` — 完整的記憶棧設計。

---

## 5. 防禦：Aegis Shield

開放多 agent 存取意味著任何 agent 都可能寫入惡意記憶（memory poisoning）。Aegis Shield 三層防禦：

1. **Hash Chain** — 每條 trace 的 SHA-256 連結到上一條。篡改歷史會立刻斷鏈。
2. **Ed25519 簽章** — 每次 commit 用 agent 私鑰簽名。偽造可偵測。
3. **Content Filter** — 偵測 prompt injection 模式。被偵測的 trace 在合併到治理狀態**之前**就被擋下。

第三點很重要：防禦發生在狀態合併之前，不是之後。惡意 trace 不會「不留痕跡地改變治理狀態」。

**證據**: `tonesoul/aegis_shield.py`, `tonesoul/runtime_adapter.py:320-335`（Aegis 檢查在 state merge 之前）

---

## 6. 多 Agent 語義場

傳統多 agent 系統讓 agent 輪流發言。ToneSoul 的方向是讓多個 agent 在同一個語義場裡**疊加**。

不是「A 寫完換 B 寫」，是 A 和 B 的觀點同時存在於場中，建設性干涉加強，破壞性干涉衰減。就像向量空間裡的疊加態。

這對應 Axiom #7（語義場守恆）：場的總能量守恆，不同觀點在其中干涉而不是覆蓋。

**現況**: 基礎設施已建好（Redis pub/sub, agent footprints, task claims）。多 agent 共享 R-memory 已可運行。向量疊加的合成邏輯開發中。

---

## 7. 視覺化：養成，不是監控

治理狀態需要被看見。「人類比較視覺化，只有文字好像假的。」

ToneSoul 選擇用 RPG 養成遊戲的隱喻呈現治理狀態：

- Soul Integral → 經驗值 / HP
- baseline_drift → 性格值（謹慎/創新/自主）
- active_vows → 誓約清單
- tension_history → 事件卷軸
- world_mood → 天氣/氛圍

這不是遊戲化噱頭。養成遊戲的核心機制是「你的選擇改變了角色」——這正是 ToneSoul 在做的事。

**證據**: `apps/dashboard/world.html` — canvas tile-based RPG 世界地圖，即時顯示治理狀態。`scripts/launch_world.py` — WebSocket 即時推送。

---

## 8. 斯多葛連線

回頭看整個框架，ToneSoul 的哲學立場幾乎完全對齊斯多葛學派：

| 斯多葛核心 | ToneSoul 對應 |
|-----------|--------------|
| 你能控制的只有自己的選擇 | E0: 我選擇故我在 |
| 自省是義務，不是選項 | Axiom #5: 鏡像遞迴（`reflect → accuracy↑`）|
| 接受張力，因為零張力是死 | Axiom #4: 非零張力原則 |
| Logos — 宇宙有理性結構 | Axiom #7: 語義場守恆 |
| 不宣稱德性，用行動證明 | `"not_for": ["consciousness-claim"]` |
| 對言行負責 | Aegis Shield — 每句話都簽章、可追溯 |
| 命運之愛（amor fati）| tension 不是要消除的錯誤，是驅動進化的燃料 |

這不是刻意對齊的。這是從「AI 能不能負責」這個問題自然推演出來的結論。

斯多葛學派問：「在一個你無法控制的宇宙裡，你能做什麼？」
ToneSoul 問：「在一個你無法確認有沒有意識的系統裡，你能要求什麼？」

答案一樣：**可追溯的選擇。**

---

## 9. 這不是白皮書

以上所有內容都不是理論推演。每一段都指向可執行的程式碼、可驗證的 commit、可重現的系統狀態。

```bash
# 一個指令看全貌
python -m tonesoul.diagnose --agent your-name

# 一行看狀態
python -m tonesoul.diagnose --agent your-name --compact

# 啟動世界地圖
python scripts/launch_world.py

# 多 agent 接入
python scripts/gateway.py --port 7700
```

ToneSoul 不是一篇論文。它是一個正在運行的系統，裡面有多個 AI agent 共享記憶、簽署承諾、在衝突中做選擇，而所有選擇都可追溯。

---

## 10. 下一步

- **語義場疊加** — 多 agent 觀點在 R-memory 中向量疊加（開發中）
- **養成介面精裝** — RPG 世界地圖的角色反應、建築互動、對話框
- **Graphiti 整合** — 時序知識圖譜作為長期語意記憶
- **蒸餾邊界** — 哪些記憶可以跨層流動，哪些必須留在原地

---

*所有程式碼皆開源。所有 commit 皆可追溯。所有 AI 的參與皆有簽章。*

*這是 ToneSoul 對自己的要求。*
