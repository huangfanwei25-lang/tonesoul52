# ToneSoul L7/L8 開源框架與實證理論地圖（2026-03-22）

> 狀態：research map / convergence note
> 範圍：L7 `compiled retrieval + verifiers`、L8 `model attachment + distillation boundary`

## 0. 為什麼要有這份文件

語魂現在已經有：

- 八層總圖
- L7 的知識圖譜 / verifier 基礎
- L8 的概念邊界

但還缺一件事：

> 哪些外部框架真的值得借鏡，哪些理論真的有 benchmark 或論文支撐，哪些只是名字很新但還不該直接內化成主線。

這份文件的目的不是追熱門名詞，而是建立一個比較嚴格的判準：

1. `production reference`
   - 開源社群採用度高，架構模式清楚
2. `paper / benchmark support`
   - 至少有公開論文、benchmark、或可追溯實驗主張
3. `ToneSoul fit`
   - 是否符合語魂的公開 / 私有邊界、治理優先、可審計要求

## 1. 目前工作結論

### 一句話版

語魂 L7 不應抄單一記憶產品，而應組合：

- `GraphRAG / Graphiti` 的圖式檢索
- `LangGraph` 的 stateful orchestration
- `Mem0` 的 extraction/update memory mutation 思路
- `ComplexBench / LoCoMo / LongMemEval` 的驗證觀點

語魂 L8 則不應直接把私密記憶蒸餾進模型，而應先走：

- `public-safe trace distillation`
- `LoRA / adapter`
- 小範圍、可回滾、可審計的外掛路線

## 2. 開源框架地圖

## A. L7 主要參考對象

| 專案 | 類型 | 公開訊號 | 對語魂最有價值的部分 | 不該直接照抄的部分 |
| --- | --- | --- | --- | --- |
| `microsoft/graphrag` | graph-based retrieval pipeline | GitHub 顯示約 `30.2k` stars（2026-03-22） | 全域問題用 graph + community summaries，不只做局部 chunk retrieval | indexing 成本高，不適合每個 repo / 每輪都重建 |
| `getzep/graphiti` | temporal knowledge graph memory | GitHub 顯示約 `24.1k` stars（2026-03-22） | 時序化關係、歷史狀態查詢、事件感知記憶 | 依賴圖資料庫與完整服務棧，對語魂主 repo 來說太重 |
| `langchain-ai/langgraph` | orchestration runtime | GitHub 顯示約 `27.1k` stars（2026-03-22） | durable execution、checkpoint、human-in-the-loop、可回復 state machine | 不該把 LangGraph 當成語魂本體 ontology |
| `mem0ai/mem0` | production memory layer | GitHub 顯示約 `50.7k` stars（2026-03-22） | extraction/update/delete/noop 記憶變異模型、實務 API、speaker/user attribution | vendor benchmark 不能直接當客觀真理；預設比較偏產品 memory layer |
| `Fan1234-1/OpenClaw-Memory` | 本地輕量記憶基線 | GitHub 顯示 `3` stars（2026-03-22） | `FAISS + BM25 + RRF + time decay` 的本地、可離線、低依賴 baseline | 不足以單獨承擔 graph / temporal / governance memory 全部需求 |

### 對語魂的判斷

- `GraphRAG` 最適合語魂的地方，是回答「整個 corpus 的主題 / 關係 / 全域結構是什麼」這種問題。
- `Graphiti` 最適合語魂的地方，是回答「關係如何隨時間改變」這種問題。
- `LangGraph` 最適合語魂的地方，是把 verifier、人工覆核、agent state 做成 durable workflow。
- `Mem0` 最適合語魂的地方，是記憶抽取與更新操作模型，不是它的 hosted 產品外殼。
- `OpenClaw-Memory` 最適合保留為本地 baseline，讓語魂不必一開始就綁重型 graph stack。

## B. L8 主要參考對象

| 專案 / 路線 | 類型 | 公開訊號 | 對語魂最有價值的部分 | 風險 |
| --- | --- | --- | --- | --- |
| `Gen-Verse/OpenClaw-RL` | agentic RL framework | GitHub 顯示約 `3.9k` stars（2026-03-22） | 非同步 rollout / judging / training loop；把真實對話變成訓練訊號；已標示支援 LoRA | 目前更像快速演進中的 RL 工程框架，不該直接當語魂主線真理 |
| `LoRA` / adapter 路線 | parameter-efficient adaptation | 經典基礎論文與廣泛實作 | 讓語魂把「穩定、公開、安全」的行為外掛進模型，而不必全量微調 | 很容易被誤用成把私密記憶直接壓進權重 |

### 對語魂的判斷

- `OpenClaw-RL` 值得研究，但在語魂裡應被定位為 `L8 experiment rail`，不是治理主幹。
- 語魂真正需要的是：
  - 先定義 `public-safe distillation surface`
  - 再決定哪些 trace 可以進 adapter
  - 最後才談 RL 或長期自我優化

## 3. 實證支撐較強的理論與 benchmark

## A. 長上下文不可靠，不該把長 md 當主 runtime 介面

### `Lost in the Middle`

核心結論：

- 模型對長上下文中的資訊使用有明顯位置偏差
- 開頭與結尾較容易被用到
- 中段資訊明顯更容易被忽略

對語魂的直接意義：

- 不要讓 agent 每次都生吞長 md
- 要把長文件編譯成：
  - policy cards
  - authority maps
  - verifier checklists
  - knowledge graph artifacts

這條理論直接支撐語魂的 `L7 compiled retrieval` 路線。

## B. 多重約束組合本身就是弱點，不該只靠 prompt 遵守

### `ComplexBench`

核心結論：

- 複雜 instruction 的困難不只是 constraint 種類
- 更大的難點在於多個 constraint 的組合與依賴結構

對語魂的直接意義：

- 你先前提到的「6 個布林條件」「SQL 超過兩個 join 就掉準確率」這種痛點，不是孤例
- 語魂不能只寫「請遵守這些規則」
- 規則應外化成：
  - hooks
  - protected-path verifiers
  - changed-surface checks
  - stop verifiers

這條理論直接支撐語魂的 `verifier-first` 路線。

## C. 長期對話記憶確實很難，單靠長 context 或簡單 RAG 不夠

### `LoCoMo`

核心結論：

- 它把 very long-term conversation memory 做成公開 benchmark
- 平均約 `300 turns / 9K tokens / up to 35 sessions`
- 結論很清楚：即使有 long-context 或 RAG，模型仍明顯落後人類

對語魂的直接意義：

- 語魂如果要聲稱自己在 memory 上有進展，就不能只看單輪 QA 或短上下文
- 後續 L7 / L8 的評估，應至少模仿：
  - multi-session reasoning
  - temporal reasoning
  - event consistency

### `LongMemEval`

核心結論：

- 它把長期互動記憶拆成 5 個能力：
  - information extraction
  - multi-session reasoning
  - knowledge updates
  - temporal reasoning
  - abstention

對語魂的直接意義：

- 語魂未來的 memory verifier 不應只問「有沒有找到相似內容」
- 還要問：
  - 有沒有處理更新 / 衝突
  - 有沒有時間順序感
  - 不知道時能不能 abstain

## D. retrieval 應該是自適應的，不是每次都固定塞同樣數量的文件

### `Self-RAG`

核心結論：

- retrieval 不是越多越好
- 模型應根據需求自適應檢索
- 並對檢索內容與自身生成結果做 self-reflection

對語魂的直接意義：

- 語魂不應永遠固定 top-k 或固定 memory injection 量
- 更合理的方向是：
  - need-to-retrieve 判斷
  - evidence quality check
  - retrieval 後的 critique / verifier

## E. 圖式檢索真正強的是全域 sensemaking，不只是 entity lookup

### `GraphRAG`

核心結論：

- 傳統 RAG 對全域問題不夠好
- graph index + community summaries 對大型私有語料的 global question 更有效

對語魂的直接意義：

- 語魂的 knowledge graph 不應只做 repo 導航
- 中期應發展成：
  - 全域主題摘要
  - 層級社群摘要
  - 針對「整體架構 / 主線變化 / 近期 drift」的 global query path

## F. 記憶應該有層級與切換，不是一個永遠膨脹的 prompt buffer

### `MemGPT`

核心結論：

- 受限 context window 可以透過 memory tiers 管理
- 作法像作業系統的虛擬記憶體

對語魂的直接意義：

- working memory
- durable memory
- private vault

這三者要維持分層，不該混成一個巨大上下文池。

## G. temporal knowledge graph 是目前最貼近語魂長期方向的外部記憶論文之一

### `Zep / Graphiti`

核心結論：

- 以 temporal knowledge graph 處理 ongoing conversations + business/state data
- 論文宣稱在 DMR 超過 MemGPT，且在 LongMemEval 類任務有明顯優勢

對語魂的直接意義：

- 語魂不應只記「相似文本」
- 更應該記：
  - 關係何時成立
  - 何時失效
  - 是否被更新 / 推翻

這很適合語魂後續的：

- provenance + memory update
- conflict / contradiction handling
- temporal governance memory

## H. 模型內長期記憶是值得研究的，但目前仍屬 L8 之後的研究出口

### `Titans`

核心結論：

- 把 attention 視為短期記憶
- neural memory 視為較持久的長期記憶
- 在長上下文與 needle-in-haystack 類任務有優勢

對語魂的直接意義：

- 這支持了「短期工作記憶」與「長期持續記憶」分離的方向
- 但 Titans 是模型架構級研究，不是語魂現在應立刻重寫 runtime 的理由

所以它目前更適合作為：

- `L8 theoretical north star`
- 而不是 `L7 implementation checklist`

## I. 參數外掛路線目前最穩定的基礎仍是 LoRA，而不是把記憶直接寫進權重

### `LoRA`

核心結論：

- 冻結原模型，插入低秩可訓練矩陣
- 以極少參數達到接近或優於 full fine-tuning 的效果

對語魂的直接意義：

- 語魂若要做模型外掛，最合理的第一步是 adapter / LoRA
- 但資料來源只能是：
  - 公開
  - 低風險
  - 可公開審計
  - 不含個資 / vault / 不可逆記憶

## 4. 對 ToneSoul 的收斂建議

## A. 先收斂 L7，不要先追求「智慧地內化」

優先順序：

1. `artifact compiler`
   - 把長 md 壓成 policy card / authority map / verifier checklist
2. `memory benchmark harness`
   - 至少用 LoCoMo / LongMemEval 的能力切分思路
3. `temporal graph layer`
   - 讓記憶關係有時間性，而不只是相似度
4. `retrieval policy`
   - 改成 conditional retrieval + evidence checks

## B. L8 只能蒸餾行為，不能蒸餾私密歷史

`可蒸餾`

- 穩定治理傾向
- 公開哲學姿態
- 工具路由偏好
- 可公開的語氣 / style
- 經 verifier 篩過的 trace patterns

`不可蒸餾`

- 私人記憶 vault
- 原始對話歷史
- 可識別個人資料
- 攻擊字典與私有紅隊 payload
- 必須可刪除的記錄級資料

## C. 對 OpenClaw 相關路線的定位

`OpenClaw-Memory`

- 適合當本地 baseline memory substrate
- 讓語魂維持 local-first / no-cloud dependency 的底盤

`OpenClaw-RL`

- 適合當 L8 的實驗支線
- 研究如何把 conversation trace 變成訓練訊號
- 但目前不該取代語魂治理主線

## 5. 建議的下一步實驗順序

### Phase A: L7 research-to-engineering

做一份 `L7 retrieval contract`：

- 什麼情況讀 graph
- 什麼情況讀 status artifact
- 什麼情況讀 raw docs
- 什麼情況直接跑 verifier

### Phase B: temporal memory pilot

在不引入完整外部 graph DB 的前提下，先做：

- temporal edge schema
- relation validity / superseded markers
- contradiction / update semantics

### Phase C: L8 distillation boundary contract

做一份正式文件定義：

- public-safe traces
- adapter dataset schema
- forbidden training surfaces
- adapter evaluation criteria

### Phase D: tiny adapter experiment

只對公開安全 trace 做非常小的 LoRA / adapter 實驗，觀察：

- 是否改善穩定治理姿態
- 是否破壞可審計性
- 是否引入刪除與 provenance 問題

## 6. 證據等級標記

| 等級 | 意義 |
| --- | --- |
| `A` | 公開論文 + benchmark / 實驗結果明確 |
| `B` | 公開 repo + 清楚架構模式，但效果多來自作者主張 |
| `C` | 值得追蹤的前沿方向，尚不應直接作為主線依據 |

### 目前建議

- `A`: Lost in the Middle, ComplexBench, LoCoMo, Self-RAG, GraphRAG, MemGPT, Zep, Titans, LoRA
- `B`: Mem0, LangGraph, Graphiti
- `C`: OpenClaw-RL 作為語魂主線理論依據

說清楚一點：

- `OpenClaw-RL` 很值得研究
- 但現在更像高潛力工程框架與實驗路線
- 還不是語魂可以直接宣稱「已被充分證實」的核心理論

## 7. 目前最合理的總結

語魂下一步不應該是：

- 再塞更多長 markdown
- 或直接把私密記憶做成模型內化

而應該是：

1. 用 `L7` 把檢索、約束、驗證做成工程現實
2. 用 `LoCoMo / LongMemEval / ComplexBench` 類基準，校準真正弱點
3. 用 `L8` 做小步、可逆、public-safe 的 adapter 實驗

如果只用一句話記住：

> 語魂要追的不是「更大的上下文」，而是「更可靠的外部記憶與治理結構」，再把其中穩定、公開、安全的部分，選擇性外掛進模型。

## Sources

- Microsoft GraphRAG repo: https://github.com/microsoft/graphrag
- GraphRAG paper: https://arxiv.org/abs/2404.16130
- Graphiti repo: https://github.com/getzep/graphiti
- Zep paper: https://arxiv.org/abs/2501.13956
- LangGraph repo: https://github.com/langchain-ai/langgraph
- Mem0 repo: https://github.com/mem0ai/mem0
- Mem0 research page: https://mem0.ai/research
- OpenClaw-RL repo: https://github.com/Gen-Verse/OpenClaw-RL
- OpenClaw-Memory repo: https://github.com/Fan1234-1/OpenClaw-Memory
- LoRA paper: https://arxiv.org/abs/2106.09685
- MemGPT paper: https://arxiv.org/abs/2310.08560
- Self-RAG paper: https://arxiv.org/abs/2310.11511
- Titans paper: https://arxiv.org/abs/2501.00663
- Lost in the Middle: https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long
- ComplexBench paper: https://arxiv.org/abs/2407.03978
- LoCoMo paper: https://arxiv.org/abs/2402.17753
- LongMemEval repo: https://github.com/xiaowu0162/LongMemEval
