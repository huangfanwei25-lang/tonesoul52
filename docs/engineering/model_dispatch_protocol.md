# 模型分流協議(Model Dispatch Protocol)

> Status: v1(2026-07-04)· 性質:**操作協議,advisory 非 enforced**——沒有 CI gate 強制它;它的力量來自被引用。
> Provenance:外部三層分工實戰帖(2026-07-03,orchestrator/executor/reviewer)× 語魂自有判例
> (constraint-set 委派、codex 外眼、shadow-only qwen 設計)。**吸收的是「位置」概念,不是它的數字**
> (該帖效能宣稱為單樣本自述,E1)。
> 掛載點:本表補的是 `docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md`
> Track Assignment Matrix 缺的**模型維度**——那張表路由「流程強度」,這張表路由「引擎」。
> 讀者:任何要派工的 agent(含 7/7 後的接班者)。規則具體到可照做;判斷不動產(哪些事不歸模型)寫死。

## 0. 引擎現實(每次派工前重新查證,別信這張快照)

| 引擎 | 本機狀態(2026-07-04 實測) | 重新查證指令(可直接複製跑) |
|---|---|---|
| Claude 主 agent(現 Fable 5;7/7 後=訂閱可用的最強型號) | 本 session 即是 | — |
| Claude subagent(Agent tool:sonnet / haiku / opus / fable + effort 參數) | 可用 | harness 內建 |
| codex CLI | **0.134.0 已裝**(compute 是另一回事,派工時實測) | `codex --version`;compute 探測=實跑一次小 review,看 `scripts/codex_review.py` 是否 degrade |
| Gemini / AGY CLI | **本機未偵測到**(owner 宣稱另有安裝;裝了再填上版本) | PowerShell:`Get-Command gemini,agy,antigravity -ErrorAction SilentlyContinue`;bash:`which gemini agy antigravity` |
| 本地 qwen(ollama) | **服務起著**:qwen2.5:1.5b + nomic-embed-text,port 11434 OPEN | `ollama list`;port 探測(雙 shell 通用):`python -c "import socket;s=socket.socket();s.settimeout(0.5);print('OPEN' if s.connect_ex(('127.0.0.1',11434))==0 else 'closed')"` |
| lmstudio | port 1234 closed(未起) | 同上,port 改 1234 |

**鐵律:引擎不可用就明說並降級(single-opinion-stop 前例:`scripts/codex_review.py`),不假裝跑過。**

## 1. 分流表(任務型態 → 引擎 + 模式)

| 任務型態 | 引擎 | 模式/effort | 為什麼(判例) |
|---|---|---|---|
| 方向判斷、工單切分、驗收裁定、review 仲裁、close 決定 | **最強可用 Claude(主 agent)** | 主對話;不下場寫大量碼 | 「換便宜引擎就掉品質」的部分只有判斷;把它拿去打字=燒最貴的 token 做最便宜的事 |
| bounded implementation ticket(驗收明確、scope 窄、有禁區) | **codex** | exec / goal 長模式;工單必走 `work_order_template.md` | codex 是強執行者,弱在自定 done——工單把 done externalize 之後成功率大增(外部實戰 + 語魂 4+ 份 codex 工單判例) |
| 機械批量(格式化、改名、補 marker、跑既定腳本) | Claude subagent(**haiku/sonnet, effort low**)或 codex | 批次,一單多檔 | 模式已解出後降級批次套用;不值得強模型 |
| 大面積唯讀探勘/盤點/掃 repo | Claude subagent 扇出(Explore / general-purpose,**effort low-medium**) | Workflow 或 Agent tool;結論回主對話,長產物寫檔傳路徑 | 2026-07-03 atlas:11 個唯讀 agent 扇出,主對話只進結論 |
| 外眼審查(governance / fail-closed / security-critical code) | **與修復者不同的模型**(codex 修→Claude 審;Claude 修→codex 審) | `codex-second-opinion` skill / `scripts/codex_review.py` | 同模型審自己不算數(紅隊在「0 bypass」找到 2 個);同模型對 fail-closed 核心會產出自信但錯的 fix(2026-06-29 判例)。**判準是「審 ≠ 修」,不是「審=codex」**(2026-07-04 haiku 實測抓到的歧義) |
| 第二 reviewer(有 Gemini/AGY 時) | Gemini/AGY | review-only;**findings 一律走 `review_adjudication_protocol.md`,不得直達 executor** | 異質錯誤分佈值得要;幻覺率也高——所以仲裁是必要配套,不是可選 |
| shadow 第二眼(7/7 後常駐) | 本地 qwen(ollama) | **shadow-only:記 divergence、不 gate、不改輸出** | yu_handoff 談定的設計;弱模型的安全位置是「不放大你錯誤的位置」 |
| 品味判斷、道德兩難、產品方向、風險接受 | **人類 owner** | 攤開張力交還(DECLARE_STANCE 模式) | 判斷分層的出口:AXIOMS meta.not_for、honest-judgment skill「道德兩難不裁決」 |

## 2. 升降級路徑(具體判準)

- **升級**:便宜引擎同一子任務**錯 1 次**→升一級重試;中階**同一子任務連錯 2 次**→帶**完整失敗軌跡**(不是「它失敗了」一句話)升到主 agent。
- **降級**:主 agent 把模式解出來(一個成功案例+可複製步驟)→降回便宜引擎**批次**套用。
- **停損**:同一件事**最多重試兩輪**;第 3 次失敗必停,重新評估方向(= 倉庫 vow-003「3 連敗必停」,這條有誓言背書)。
- **方向錯訊號**(該換路不該重試):diff 越修越大而驗收沒逼近;同一個 gate 反覆紅但原因每次不同;開始想改驗收條件遷就實作。

## 3. 通訊紀律(files-as-medium)

**結果一律寫實體檔,彼此用讀的**;對話只傳結論+路徑。理由:(a) context 大件傳輸會 error
(owner 實戰教訓);(b) 檔案有 git 痕跡=可稽核,對話沒有;(c) 語魂設計本就如此
(handoff/、docs/status/ artifacts、DESIGN Invariant 5 file-backed truth)。
長工單→ `docs/plans/`;review 產物→ `docs/status/` 或 tmp 後歸檔;絕不在 prompt 裡內嵌整份大檔。

## 4. 誠實限制

- 本表是 **2026-07-04 快照**;引擎列表會過期,§0 的查證指令才是正典。
- 各引擎的效能/成本宣稱**本倉庫沒有實測數字**;要引數字先量測(honesty:不繼承外部帖的 20%/8hr 宣稱)。
- 這張表本身沒有 enforcement——第一次有 agent 因為沒看它而派錯工,把案例補進本節,那才是它的第一條判例。
