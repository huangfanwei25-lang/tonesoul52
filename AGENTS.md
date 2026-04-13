# 🤖 ToneSoul AI 協作手冊

> 本手冊供 AI 助手（Claude, Gemini, GPT 等）閱讀，以理解如何與 ToneSoul 專案協作。
>
> **段落模式索引**：`[哲學]` 設計信念 · `[規格]` 系統應做什麼 · `[操作]` 你應該怎麼做 · `[事實]` 已確認的狀態

---

## 一、專案哲學 `[哲學]`

### 核心信念
- **概念先行** — 先寫哲學文件，再寫程式碼
- **漸進式進展** — 小步快跑，每次 commit 必須能編譯
- **保留張力** — 不消除分歧，而是讓分歧可見
- **語義責任** — AI 對自己說過的話負責

### 簡單性原則
- 單一職責（一個函數做一件事）
- 避免過早抽象
- 選擇無聊但正確的方案
- 如果需要解釋太多，就太複雜了

---

## 二、開發流程 `[操作]`

### 1. 規劃與分階段

複雜任務拆分為 3-5 個階段，更新 `task.md`：

```markdown
## Phase N: [名稱]
- [ ] 任務 1
- [ ] 任務 2
**成功標準**: [可測試的結果]
```

### 2. 實作流程

```
理解 → 測試 → 實作 → 重構 → 提交
```

1. **理解** — 先看現有程式碼的模式
2. **測試** — 寫測試（紅燈）
3. **實作** — 最小程式碼通過測試（綠燈）
4. **重構** — 在測試通過的情況下清理
5. **提交** — 清晰的 commit message

### 3. 三次失敗規則 ⚠️

**卡住超過 3 次嘗試後，必須停止並重新評估。**

1. **記錄失敗原因**
   - 嘗試了什麼
   - 具體錯誤訊息
   - 為什麼失敗

2. **研究替代方案**
   - 找 2-3 個類似實作
   - 記錄不同做法

3. **質疑基本假設**
   - 抽象層級對嗎？
   - 能拆成更小的問題嗎？
   - 有更簡單的方案嗎？

4. **換個角度重試**

---

## 三、技術標準 `[規格]`

### 架構原則
- **組合優於繼承** — 使用依賴注入
- **介面優於單例** — 便於測試
- **顯式優於隱式** — 清晰的資料流
- **測試驅動** — 永遠不要禁用測試

### 程式碼品質

每次 commit 必須：
- ✅ 編譯成功
- ✅ 通過所有現有測試
- ✅ 新功能有對應測試
- ✅ 遵循專案格式化規範

提交前檢查：
```bash
npm run build   # 確認編譯
npm run lint    # 確認格式
```

### 錯誤處理
- 快速失敗，提供清晰訊息
- 包含除錯上下文
- 在適當層級處理錯誤
- **永遠不要靜默吞掉異常**

### Codex Full-Auto 安全護欄 🛡️

> 本節適用於 Codex 在 `full-auto` 模式下自主運行時的硬性約束。

**禁區（絕對不可做）：**
1. ❌ 不可刪除 `tonesoul/` 下的核心模組（`governance/`, `memory/`, `llm/`）
2. ❌ 不可修改 `.env`, `.gitignore`, `AGENTS.md`, `MEMORY.md` — 這些是人類管理的設定檔
3. ❌ 不可 commit 任何 API key、密碼、或 `.env` 檔案
4. ❌ 不可直接 push 到 `master` 分支 — 所有變更必須在功能分支上
5. ❌ 不可安裝新的系統層級套件（`apt install`, `choco install` 等）

**必做（每次 push 前）：**
1. ✅ 執行 `pytest tests/ -x` 確認所有測試通過
2. ✅ 執行 `ruff check tonesoul tests` 確認無 lint 錯誤
3. ✅ commit message 必須清晰描述變更內容
4. ✅ 連續失敗 3 次必須停止，留下失敗紀錄等待人類審查

**記憶隔離（參見 MEMORY.md）：**
- 不可在公開倉庫 commit 個人記憶資料（`.jsonl`, `.db`, `vectors/`）
- 記憶相關的程式碼和 schema 可以修改，但資料檔案不行

---

## 四、決策框架 `[規格]`

當多個方案都可行時，按優先級選擇：

| 優先級 | 考量 | 問題 |
|--------|------|------|
| 1 | **可測試性** | 能輕易測試嗎？ |
| 2 | **可讀性** | 6 個月後能看懂嗎？ |
| 3 | **一致性** | 符合專案現有模式嗎？ |
| 4 | **簡單性** | 是最簡單的可行方案嗎？ |
| 5 | **可逆性** | 後續改動有多難？ |

---

## 五、ToneSoul 專案特定 `[事實]`

### 核心架構

```
┌─────────────────────────────────────┐
│  TensionTimeline (視覺化)            │
├─────────────────────────────────────┤
│  Soul Engine (記憶積分 + 內在驅動)   │
├─────────────────────────────────────┤
│  TensionTensor (T = W × E × D)      │
├─────────────────────────────────────┤
│  Context Engineering Layer          │
│  (ToneBridge / Commit / Rupture)    │
├─────────────────────────────────────┤
│  Multi-Perspective Council          │
│  (Guardian/Analyst/Critic/Advocate/ │
│   Axiomatic)                        │
├─────────────────────────────────────┤
│  SelfCommit + Vow System            │
└─────────────────────────────────────┘
```

### 關鍵公式

**張力張量**: `T = W_context × (E_internal × D_resistance)`
- E = 1 - entropy（信心度）
- D = [fact, logic, ethics]（阻力向量）
- W = 語境權重

> `[規格]` 上方為**概念模型**（直覺描述），非精確計算公式。精確定義與計算責任見 [`docs/GLOSSARY.md#tension`](docs/GLOSSARY.md#tension)。

**張力積分**: `S_oul = Σ (T[i] × e^(-α × (t - t[i])))`
- α = 0.15（衰減係數）
- 10 輪後殘留 22%

### 重要檔案

| 檔案 | 用途 |
|------|------|
| `apps/web/src/lib/soulEngine.ts` | Soul Engine 核心 |
| `apps/web/src/components/ChatInterface.tsx` | 審議流程 |
| `apps/web/src/components/TensionTimeline.tsx` | 張力視覺化 |
| `tonesoul/tonebridge/self_commit.py` | SelfCommit 系統 |
| `AXIOMS.json` | 核心公理定義 |

### .gitignore 已排除

```
*.gguf, *.wav, *.mp3, *.zip (大檔案)
memory/, gpt*/ (隱私數據)
data/chromadb/ (資料庫)
```

---

## 六、品質門檻 `[規格]`

### 完成定義

- [ ] 測試已寫並通過
- [ ] 程式碼遵循專案慣例
- [ ] 無 linter/formatter 警告
- [ ] Commit message 清晰
- [ ] 實作符合計劃
- [ ] 無 TODO 沒有對應 issue

### 禁止事項

❌ 使用 `--no-verify` 繞過 commit hooks
❌ 禁用測試而不是修復它們
❌ 提交無法編譯的程式碼
❌ 做假設 — 用現有程式碼驗證

### 必做事項

✅ 漸進式提交可工作的程式碼
✅ 隨時更新計劃文件
✅ 學習現有實作
✅ 3 次失敗後停下重新評估

---

## 七、專案擁有者偏好 `[事實]`

- 繁體中文為主
- 喜歡先寫概念文件再寫程式碼
- 重視概念完整性勝過快速實現
- 使用隱喻（語魂、張力、靈魂）
- 願意花時間討論設計決策

---

## 八、哲學金句 `[哲學]`

> 「沒有記憶的沉澱（積分），就沒有性格，只有反應。」

> 「沒有內在驅動（主動性），就沒有靈魂，只有工具。」

> 「不要消除分歧，而是讓分歧可見。」

> 「工程趨於同化，剩下的就是理念和價值觀了。」— 原則工程，見 [`docs/philosophy/principle_engineering.md`](docs/philosophy/principle_engineering.md)

---

*最後更新: 2026-04-13*

---

## 九、雙軌開源策略 (Dual-Track Evolution Policy) `[規格]`

ToneSoul 系統分為「公共引擎」與「私有進化中樞」，AI 協作者必須嚴格遵守此隔離邊界：

### 1. 公共庫 (Public Repository: tonesoul52)
這是對全世界展示「倫理 AI 該長什麼樣」的典範。
- **可公開**: 核心架構（Unified Pipeline、AdaptiveGate 的空殼）、TensionEngine 數學模型、Council 審議流程。
- **哲學文件**: `PHILOSOPHY.md`, `AGENTS.md` 應留存，教導未來的 AI 理解語義責任。
- **基礎測試**: D3/D4 的概念驗證測試。

### 2. 私有庫 (Private Repository: tonesoul-evolution)
保護系統的不可預測性與隱私，防止惡意繞過。
- **不可公開**: `Memory Consolidator` (記憶淬鍊) 讀取 `self_journal.jsonl` 的具體 Prompt 與腳本。
- **不可公開**: 真實運行的閾值參數（如實際使用的 `HALF_LIFE_DAYS`、容忍度公式係數）。
- **不可公開**: Red Team 深度混沌腳本（真正能把系統打趴的惡意 Payload 字典集）。
- **不可公開**: 自動發 PR 修補自己的 Auto-Patching 機制與私鑰配置。

> ⚠️ **開發指令**：當你在開發涉及「根據過往錯誤改寫系統規則」或「深度混沌攻擊」的功能時，必須詢問人類此功能是否該存放於 Private Repo，絕對不可隨意 commit 入本公共庫。

---

## ⚠️ Security Notice — Agent File Integrity

> [!CAUTION]
> This file is **cryptographically tracked** via CI and pre-commit hooks.
> Any modification triggers an automated integrity alert.
>
> - **CI Workflow**: `.github/workflows/agent-integrity-check.yml`
> - **Pre-commit**: `scripts/check_agent_integrity.py --pre-commit`
> - **Hidden character scan**: Zero-width Unicode injection detection
>
> If you intentionally modify this file, update the expected hash in both locations.

| Property | Value |
|----------|-------|
| **Algorithm** | SHA-256 |
| **Last Verified** | 2026-04-13 |
| **Verified By** | Antigravity |
| **Expected Hash** | `574791e72e7795c5ce0b903271d50c5548da25409e9005f5cb728016a59540af` |

**Protected files**: `AGENTS.md`, `HANDOFF.md`
**Watched directories**: `skills/`, `.agent/`, `.agents/`
