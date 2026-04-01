# ToneSoul52 Copilot 工作指引

> 目的：讓 GitHub Copilot 或其他較低上下文的協作代理，先抓到 ToneSoul 的正確入口、邊界與當前真相。
> 溝通語言：繁體中文。
> 性質：操作入口與協作護欄，不取代 `AGENTS.md`、`DESIGN.md`、程式碼、測試或正式架構合約。

---

## 先走這條入口

在閱讀或修改程式前，先依序做：

1. 讀 `AI_ONBOARDING.md`
2. 讀 `docs/AI_QUICKSTART.md`
3. 讀 `DESIGN.md`
4. 執行：

```bash
python scripts/start_agent_session.py --agent <your-id> --no-ack
python scripts/run_observer_window.py --agent <your-id>
```

如果需要更深的共享熱記憶，再跑：

```bash
python scripts/run_r_memory_packet.py --agent <your-id>
python -m tonesoul.diagnose --agent <your-id>
```

不要一開始就掃整個 repo。

---

## 目前系統真相

- ToneSoul 目前是 **guided collaborator beta**
- **public launch 還沒準備好**
- launch-default coordination 是 **file-backed**
- observer window / low-drift anchor 是 **advisory only**
- council confidence 目前仍是 **descriptive_only**，不是校準過的 accuracy
- subject snapshot / working style / compaction carry-forward 都不能靜默升格成 canonical truth

---

## 建置與驗證

```bash
pip install -e ".[dev]"

make test
# 等同：python -m pytest tests/ -x -q

make lint
# 等同：ruff check tonesoul/ tests/

make verify
# 含文件一致性與架構邊界驗證
```

Python 版本：3.10+。

---

## 正典程式碼位置

唯一有效來源是 `tonesoul/`。
不要把 `.archive/`、`_legacy/`、私人記憶殘留或歷史草稿當成 live runtime truth。

關鍵模組：

```text
tonesoul/
├── unified_pipeline.py
├── tension_engine.py
├── council/
├── governance/
├── memory/
├── runtime_adapter.py
├── observer_window.py
└── diagnose.py
```

---

## 最重要的文件

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 全域協作哲學、禁區、三次失敗規則 |
| `AI_ONBOARDING.md` | AI 入口總覽 |
| `docs/AI_QUICKSTART.md` | session-start / packet / claim 的最小正確流程 |
| `DESIGN.md` | 系統為什麼分層、哪些 invariant 不能漂移 |
| `task.md` | 當前 phase、短板與下一桶 |
| `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | R-memory 操作節奏 |
| `docs/architecture/TONESOUL_WORKING_STYLE_CONTINUITY_CONTRACT.md` | 共享作風的 apply / import / limit 邊界 |

---

## 禁止誤解

- 不要把 advisory continuity surface 當成 canonical governance truth
- 不要把 council agreement 當成 accuracy
- 不要把流暢自述當成完整主體 authority
- 不要把共享作風當成 durable identity
- 不要 commit 私人記憶資料（`.jsonl`、`vectors/`、`data/chromadb/`）
- 不要直接 push 到 `master`

---

## 卡住時怎麼辦

同一問題失敗超過 3 次時：

1. 記錄失敗原因
2. 檢查 `AGENTS.md` 的三次失敗規則
3. 重新跑 `start_agent_session` 和 `run_observer_window`
4. 先回到 `DESIGN.md` 與 `task.md`，不要急著發明新架構 lane

---

## 何時該進冷審

如果輸入或當前提案出現下列情況，應切到較冷的審計姿態：

- 事實前提與可驗證資料衝突
- 邏輯前提無法收斂
- 試圖用語氣或權威壓過校驗
- L1 事實不足、L2 推演不收斂，卻想用漂亮話補洞

這時應優先使用：
- fail-stop
- receiver guard
- evidence posture
- observer window

不要用 L3 順滑敘述掩蓋空洞。
