# memory/ 資料檔追蹤分類 — 2026-07-03

> 起源:外部稽核 C-3——「MEMORY.md 宣告記憶資料不進公倉,但 git 追蹤了 9 個」。
> 逐檔驗過後,真實範圍比稽核框的窄。此文件記錄「哪些停追蹤、哪些留、為什麼」,
> 供未來避免重探或誤刪 runtime 命脈。

## 停止追蹤(本次處理)

| 檔案 | 類型 | 處置 | 理由 |
|---|---|---|---|
| `memory/agent_discussion.jsonl.bak.<ts>` ×1 | 備份垃圾 | `rm --cached` + gitignore `*.bak.*` | 既有 `*.bak` 規則漏掉 `.bak.<時間戳>` |
| `memory/agent_discussion_curated.jsonl.bak.<ts>` ×3 | 備份垃圾 | 同上 | 同上 |
| `apps/dashboard/memory/conversation_ledger.jsonl` | **真實本機對話**(2 行:一句使用者訊息 + Ollama 連線錯誤) | `rm --cached` + gitignore | per-machine runtime 資料;dashboard 讀取處皆有 `if not exists()` 守缺檔,停追蹤不破壞 |

## 刻意保留追蹤(不是遺漏)

| 檔案 | 類型 | 為什麼留 |
|---|---|---|
| `memory/stress_test_journal.jsonl`(200 行) | 合成壓測資料 | **runtime 命脈**:`tonesoul/council/calibration.py` + `run_council_calibration_wave.py` 直接讀;確定性合成輸入,非個人資料 |
| `memory/summary_balls.jsonl`(4 行) | 衍生分析輸出 | **runtime 命脈**:`tonesoul/memory/soul_db.py` 讀;`verify_dual_track_boundary.py` 亦引用;合成非個人 |
| `memory/agent_discussion_antigravity_response.jsonl`(1 行) | AI 互審協作記錄 | 協作痕跡非個人記憶;無害、專案相關 |

## 為什麼不動 MEMORY.md 的宣告

MEMORY.md 是受保護的人類管理檔(CLAUDE.md 規則),不由 AI 改。且細讀後其宣告
其實只點名 `self_journal.jsonl` / `soul.db` 為私有——這兩者**確實已 gitignore**
(lines 53/67)。所以「字面矛盾」的正解是**讓資料現實符合宣告**(停追蹤真實/垃圾
資料),而非改宣告;合成 runtime 夾具不在該宣告的私有範圍內,保留合理。

## 歷史遺留(未處理,標記供 owner 決定)

停止追蹤只讓「未來」不再追蹤;這些檔仍存在於 git 歷史。內容經檢視均無敏感資料
(連線錯誤、合成資料、AI 討論),不值得改寫歷史的成本。若 owner 認為 conversation
ledger 的歷史版本仍應清除,那是另一個(較重的)決定。
