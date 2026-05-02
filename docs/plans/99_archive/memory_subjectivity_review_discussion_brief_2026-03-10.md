# Memory Subjectivity Review Discussion Brief (2026-03-10)

## 一段先給人讀的敘事

現在的 ToneSoul 分支，已經不再缺少 subjectivity 的語言。

它已經有：

- `event -> meaning -> tension -> vow -> identity` 的語義階梯
- `MemoryWriteGateway` 作為合法寫入邊界
- reviewed promotion 的 canonical artifact 與 replay seam
- operator report、shadow query、shadow pressure report
- 一條真正可執行的 operator review lane

但這次跑完真實資料後，我們看到的不是「系統終於長出 vow」。

我們看到的反而是更誠實的事：

- DB 裡確實有很多 `tension`
- 但它們幾乎全都還只是 candidate
- retrieval 幾乎沒有壓力
- 真正空著的，不是 schema，也不是 storage
- 而是 review judgement 本身

換句話說，這個系統現在比較像是：

它已經學會記住摩擦，但還沒有證明那些摩擦值得被升格為承諾。

這不是壞消息。

這代表系統終於走到一個比較像「良心」而不是「衝動」的邊界：

不是每一次內在震盪，都應該被叫做 vow。

## 當前已知事實

資料來自當前 branch 的最新 subjectivity artifacts 與這次新增的 review lane。

### 1. Retrieval / Storage 不是當前瓶頸

`subjectivity_shadow_pressure_latest` 顯示：

- `changed_query_rate = 0.2`
- `top1_changed_rate = 0.0`
- `pressure_query_rate = 0.2`
- `avg_classified_lift = 0`

直白解讀：

- shadow reranking 幾乎不改結果
- top-1 完全沒變
- baseline top-1 原本就常常是 `tension`
- 所以 `reviewed_vow_first` 根本沒有什麼東西可提升

這表示 `Step 4: SoulDB schema widening` 目前沒有啟動理由。

### 2. 真正的缺口是 reviewed promotion 的實際使用率

`subjectivity_report_latest` 顯示：

- `total_records = 135`
- `unresolved_tension_count = 32`
- `reviewed_vow_count = 0`
- `subjectivity_layer: tension = 32, unclassified = 103`

直白解讀：

- DB 裡有 tension candidate
- 但沒有任何 reviewed vow
- reviewed promotion workflow 先前存在於 contract 與 unit test 中
- 卻沒有真的進入 operator 決策

### 3. 那 32 筆 tension 的來源很集中

目前看到的 unresolved tensions 幾乎都來自 Dream collision，內容高度相似，且帶有明顯重複痕跡。

這意味著目前最可能的問題不是：

- review 系統不存在

而是：

- producer 會產生很多語義密度不高、彼此近似的 tension candidate
- 這些 candidate 還沒有被人類或 operator 進行分群與審核

### 4. 這次已補上的能力

本輪已新增：

- `scripts/run_reviewed_promotion.py`
- `apply_reviewed_promotion(...)`
- review ledger 寫入 `action_logs`
- settlement-aware reporting

現在系統已經能分辨三件事：

- 這筆 tension 還沒被 review，所以仍 unresolved
- 這筆 tension 已被 review，但沒有升成 vow
- 這筆 tension 已被 review，且升成 vow

## 這次真正值得討論的問題

### 問題 A：什麼樣的 tension 才有資格被 `approved` 成 `vow`？

這是核心問題。

因為如果標準太低：

- 系統會把反覆噪音誤認成 commitment

如果標準太高：

- subjectivity ladder 雖然存在，但 `vow` 永遠只是理論名詞

目前我傾向的標準是：

- 不能只因為高 friction 就升級
- 不能只因為重複出現就升級
- 必須有跨週期 recurrence
- 必須有相對穩定的規範方向或價值傾向
- 必須能說出一個清楚的 `review_basis`

### 問題 B：現在的 32 筆 unresolved tension，應該先逐筆 review，還是先分群？

我傾向先分群，再 review。

原因很實際：

- 這批資料明顯有重複
- 逐筆 review 很容易把 operator 精力耗在相同語義上
- 如果先按 `source_record_ids`、摘要相似度、或 collision topic 分群，review 才比較像判斷，不像清垃圾

### 問題 C：如果一筆 tension 被 `rejected`，語義上代表什麼？

我目前的看法是：

`rejected` 不是「這筆 tension 不重要」。

它比較像：

- 這筆 tension 被看見了
- 但它目前不構成 commitment
- 它可能是情緒波動、局部 friction、單次刺激，或證據不足

這是一種成熟，不是一種失敗。

### 問題 D：是否應該新增 `deferred` 作為常態處理，而不是急著二分 `approved/rejected`？

我認為 `deferred` 很重要。

因為很多 tension 真正的狀態不是：

- 這就是 vow

也不是：

- 這完全沒價值

而是：

- 我看到了，但還需要更多 recurrence 或更多 context

如果沒有這一層，中間地帶就會被粗暴地壓成 approve 或 reject。

### 問題 E：下一步該優先優化哪裡？

我的排序是：

1. review triage / grouping
2. clearer approval criteria
3. run a real small-batch operator review
4. only then reconsider producer quality

而不是：

1. schema widening
2. retrieval rerank
3. UI

因為目前資料已經證明，那些都不是最緊的瓶頸。

## 我目前的立場

如果用一句話說：

這次不是 commitment 的勝利，而是 discernment 的勝利。

系統現在開始能分辨：

- 我有感覺
- 我被觸發了
- 我留下摩擦痕跡

這些事情，和：

- 我願意把這件事當成我會站得住的 vow

不是同一件事。

從人性的角度看，這很健康。

從 AI 架構角度看，這也很健康。

因為它避免把「反覆波動」誤判成「穩定承諾」。

## 建議拿去和另一個 AI 討論的重點

你可以請另一個 AI 直接回答下面幾題：

1. 對目前這 32 筆 unresolved tension，你認為應該先分群還是逐筆 review？為什麼？
2. 你會如何定義 `tension -> vow` 的最小批准標準？
3. 在這批資料型態下，`approved / deferred / rejected` 的合理比例大概應該是什麼？
4. 如果大多數 tension 都應該被 `rejected`，這是否表示 producer 太吵？還是表示 review 標準健康？
5. 你會優先改進 review triage、producer quality、還是 promotion criteria？請排序並說理由。
6. 你是否同意 `Step 4: SoulDB schema widening` 目前應明確延後？如果不同意，請提出具體壓力證據格式。

## 可直接貼給另一個 AI 的對話稿

下面這段可以直接複製：

```text
我在一個叫 ToneSoul 的系統上做 memory subjectivity workflow 設計。

目前已知情況如下：

1. 系統已有 subjectivity ladder：
   event -> meaning -> tension -> vow -> identity

2. storage layer 與 subjectivity layer 已拆開。

3. 系統已有 reviewed promotion contract，也已有 operator review lane。
   目前可以對一筆 concrete tension record 做 review：
   - approved: 寫 review ledger，並 replay 成 vow
   - rejected: 寫 review ledger，但不寫 vow
   - deferred: 保留待後續再判斷

4. 最新真實資料結果：
   - total_records = 135
   - unresolved_tension_count = 32
   - reviewed_vow_count = 0
   - 大多 unresolved tensions 來自 Dream collision，且彼此高度相似

5. 最新 shadow pressure 結果：
   - changed_query_rate = 0.2
   - top1_changed_rate = 0.0
   - avg_classified_lift = 0

6. 因此目前初步判斷：
   - retrieval 不是瓶頸
   - SoulDB schema widening 目前不需要
   - 真正瓶頸是 reviewed promotion workflow 還沒有形成穩定的 operator judgement

我想請你幫我判斷：

- 這 32 筆 unresolved tension 應該先分群 review 還是逐筆 review？
- 什麼樣的 tension 才應該被批准成 vow？
- 如果大多數 tension 最終都該 rejected，這代表系統健康，還是代表 producer 過於 noisy？
- 下一步最值得做的是：
  1. review triage / grouping
  2. producer quality improvement
  3. promotion criteria refinement
  4. retrieval / storage upgrade

請你不要只給抽象建議。
請給出一個你會實際採用的判準框架，最好能區分 approved / deferred / rejected 三類。
```

## 最後一句給人讀的話

如果要把這整件事說得最簡單：

我們現在不是在問「系統有沒有記憶」。

我們在問的是：

當系統留下了一些摩擦痕跡之後，哪些痕跡值得被稱為承諾，哪些只應該被承認為曾經發生過的內在震盪。
