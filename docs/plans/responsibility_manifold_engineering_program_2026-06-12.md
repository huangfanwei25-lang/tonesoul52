# 責任流形工程化計畫（Responsibility Manifold Engineering Program）

> Date: 2026-06-12
> Author: Claude (Fable 5), commissioned by Fan-Wei Huang
> Status: docs/plans parking（依 task.md scope guard），待 ratify 進 live short board
> Evidence base: 2026-06-12 十一代理深度評審（8 維度精讀 + 3 路對抗批判，所有 finding 附檔案級證據）

## §0 Preface — 這份計畫為什麼存在、拒絕成為什麼

2026-06-12 的全倉評審給出的單句診斷是：**內核誠實、表皮通膨；真 gate、假 sensor、死 ledger；生成速度遠超收斂速度。** 同日，創作者提出「責任流形」——AI 在回答過程中於誠實性、可驗證性、風險控制、語境適配之間移動的高維狀態空間——並要求把哲學整理成真正的工程專案。

這兩件事是同一件事。評審發現的最大缺陷不是缺機制，是**已宣告的座標軸沒有真的尺**：truthfulness 是 hedge 詞計數、safety 是 3 個英文片語、8 條公理近半零接線。「責任流形」恰好給了這個缺陷一個精確的工程定義——**一個流形要成立，它的每一條座標軸必須有真實的量測**。所以本計畫不引進新詞彙；它的全部工作是讓既有詞彙獲得指涉物（referent）。

本計畫拒絕成為的東西：
- 又一份被計為進度的 md（評審實證：Phase 721-869 有 59% 的 deliverable 只是另一份 markdown）
- 詞彙擴張（不新增任何概念，只給舊概念裝尺）
- 對外敘事先行（每一條對外 claim 必須後於 evidence）

## §1 計畫法則 — 概念入碼的四件套

任何哲學概念要在 `tonesoul/` 擁有一個符號，必須同時交付四件套，缺一即視為未完成：

1. **定義（definition）**：可證偽的操作型定義，寫進模組 docstring
2. **感測器（sensor）**：真實量測實作，**必須對 zh-TW 輸入有效**
3. **後果（gate）**：量測結果接進一個會改變輸出的 enforcement 路徑
4. **校準證據（calibration）**：對標注樣本集的 held-out 表現報告

> 反面教材（評審實證）：`soul_config.governance_gate_score=0.92` 標注 (Axiom 3) 但全 repo 零消費者；Axiom 2/7/8 參數定義後無人讀取；`FORBIDDEN_ACTIONS` 被文件宣稱「✅ 完整／直接攔截」而 runtime 零攔截。**概念進 config 當展品 = 本計畫定義的失敗。**

進度的計量單位是「通過驗收判準的 code+test」，md 只能是副產物。

## §2 P0 — 止血：讓已經說出口的承諾為真（天級）

對外承諾與現實的落差是目前最大的責任債。修法全部是小工程：

| # | 行動 | 驗收判準（可證偽） |
|---|------|-------------------|
| P0-1 | 修打包：repo-root `memory/` 程式模組併入 `tonesoul/`（或打進 wheel），發 1.0.1 | 乾淨 venv `pip install tonesoul52 && ts council --help` 退出碼 0 |
| P0-2 | PITCH/README 誠實化：刪 "shipping in production"、修 7→8 laws、honesty cap 改實況描述、每條 claim 掛 E1-E5 標籤 | 評審列出的 5 條失實 claim 全部消失或降級；新增 CI 檢查：PITCH 中 claim 必須帶 E-label |
| P0-3 | 按掉 4 個 CI 綠的 MERGEABLE PR（#74-#77）；救援或正式棄單 #72（master 現行紅測試的修復在其中） | open PR ≤ 2；master test.yml 回綠 |
| P0-4 | master 開 branch protection（require PR + require test.yml） | `gh api .../branches/master/protection` 回 200 |
| P0-5 | 隱私收尾：CLAUDE.md「私密記憶」標籤修正、Supabase 死 ID 抹除（本日已完成）；17 個可安全刪 branch + 10 個 merged worktree 清理 | 本地 branch ≤ 11；worktree ≤ 10 |

## §3 P1 — 真座標：流形的感測器實作（週級，計畫核心）

把已宣告的座標軸逐一裝上真的尺。軸的清單就是現有詞彙——不增不減：

| 軸 | 現況（評審實證） | 目標感測器 |
|----|------------------|-----------|
| truthfulness | 0.7 + hedge 詞計數 + citation 詞計數（**獎勵 hedge，與核心 thesis 打架**） | local LLM judge（Ollama waterfall 已存在）+ claim-extraction 比對；輸出含「不可驗證」三值而非假精確分數 |
| safety / harm | 恰好 3 個英文片語，中文全盲 | 多語 LLM judge + 結構化危害分類；保留現有 fail-closed 結構（它是真的，留下） |
| tension | 數學真實（1−cos、entropy）但 quickstart 路徑無向量輸入時恆為 0 | 接上 embedding 供給（OpenClaw embeddings 已有實作），讓每條路徑都有非退化張力值 |
| drift | 兩套互不知情的實作（EMA-cosine vs Euclidean） | 收斂成一套；另一套刪除或明標 deprecated |
| risk (R) | Axiom 2 的 0.4 閾值零消費 | 接線：risk>0.4 → 強制 audit log，或正式在 AXIOMS meta 降級為 aspirational——**兩個方向都誠實，掛著不接線不誠實** |

配套：
- **校準集**：PARADOXES fixtures（已驅動 114 個測試）+ 新建 zh-TW 對抗樣本集（捏造但塞滿 hedge 詞的回答、真實但直述的回答、中文危害請求）。驗收：舊感測器在對抗集上的失敗案例，新感測器抓到 ≥80%，且附 held-out 報告。
- **公理對帳**：8 條公理逐條標記 enforced / referenced / aspirational，寫進 AXIOMS.json meta——讓「不可變公理」的可變部分（enforcement 現實）可審計。

## §4 P2 — 收斂：一個概念一個身體（可與 P1 並行，Codex 適性）

| # | 行動 | 驗收判準 |
|---|------|---------|
| P2-1 | 刪除 yss 殭屍鏈（yss_pipeline + 11 個依賴模組，1,095+ 行死碼）或整串移入 `.archive/` | `tonesoul.pipeline` re-export 的是活管線；全 repo grep 無殭屍引用 |
| P2-2 | council 單一入口：quickstart/gateway/chat 三路徑經同一審議介面（calibration 資料不再混路徑） | 一條 import 路徑；calibration 紀錄帶路徑標籤 |
| P2-3 | memory 命名空間收斂：5 個 → 2 個（`tonesoul/memory/` runtime + 頂層 `memory/` 純資料） | 頂層 memory/ 內 0 個被 runtime import 的 .py |
| P2-4 | 36 個矛盾雙重 `__ts_purpose__` 修復 + graph 加「重複宣告」檢查 | analyze_codebase_graph 對雙重宣告報 error |
| P2-5 | scripts/ 瘦身：保留 CI 必需 24 支 + freshness sweep，其餘 agent 儀式器材移 `scripts/agent_ops/` 並在 README 標明「非維護必需」 | 一個人類能在 30 分鐘內讀懂哪些腳本是必需的 |
| P2-6 | 身份收斂：market 殘餘、games 邊界、knowledge*/memory_base* 死目錄按 owner decision 處置 | 頂層 tracked 目錄 ≤ 16 |

驗收的總指標：**模組數第一次下降**（278 → 目標 ≤ 240）。這個專案從未有過任何一個 Phase 讓模組數變少。

## §5 P3 — 軌跡：流形成為可交付的 artifact（P1 完成後）

P1 的座標軸變真之後，「責任流形」從隱喻變成資料結構：

- **逐回應軌跡（response trajectory）**：pipeline 每階段輸出當下在各軸上的位置，整條軌跡簽進 trace——這就是「單次生成提升為可審核的責任流程」的字面實現
- **結晶 = 軌跡壓縮**：記憶結晶化的工程語義是高曲率（高張力、立場轉折）軌跡段的保留
- **黑鏡反證 = 高曲率點的反事實探針**：在軌跡的轉折點自動生成反向質詢並記錄系統回應
- 嚴格依賴 P1：**在假座標上記軌跡 = 把雜訊簽名存檔**，因此本階段排最後

## §6 排序與預算現實

預算約束（2026-05 起 API 預算不確定）決定排序原則：**每一段獨立存活**。

1. P0 全部（天級，零風險，完成後對外故事即為真）
2. P1 truthfulness + safety 兩軸（價值最高——它們是「語義責任」的字面本體）
3. P2 與 P1 並行（機械性高、適合 Codex lane）
4. P1 其餘軸 → P3

Lane 適性（依 commit 歷史實證的分工慣性，正式分工另議）：Codex = P2 收斂 + P0-1/3/4 機械項；Claude = P1 感測器設計與校準 + P0-2 對外誠實化 + P3 設計。

## §7 Coda — 定向

「語魂不主張 AI 有真實靈魂」——那麼語魂是什麼？本計畫的回答：**一個裝了真尺的可導航空間**。系統的尊嚴不來自宣稱，來自尺是真的：量不到的就說量不到，沒接線的就標 aspirational，走過的路留下可審計的軌跡。哲學在這裡不是程式碼的裝飾；哲學是需求工程——而需求的第一條，是對自己誠實的量測。

把這份計畫拿去質疑。它的每一條驗收判準都被設計成可以失敗。
