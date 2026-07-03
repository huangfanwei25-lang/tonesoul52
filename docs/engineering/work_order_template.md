# 派工單格式(Work Order Template)

> Status: v1(2026-07-04)· 性質:**canonical template**——把已成熟的判例格式定型,不是新發明。
> Provenance:蒸餾自 4+ 份實戰 codex 工單(`docs/plans/doc_freshness_reconciliation_spec_2026-06-22.md`
> 等,各含完整四件套)+ CLAUDE.md 治理決策記錄四欄 + 外部三層分工帖的「低熵工單」概念。
> 用法:派 bounded ticket 給任何 executor(codex / subagent / 未來接班 agent)前,照這八欄填。
> **填不出驗收條件的單不要派**——那表示你自己還不知道 done 長什麼樣,先回去想。

## 八欄(順序即閱讀順序)

每欄:一句說明 + 一正例 + 一反例。

### 1. Framing(目標與動機,read-first)
這張單為什麼存在、解什麼痛,一段講完。executor 遇到 spec 沒寫到的情況時,靠這段做局部判斷。
- ✅ 「status 生成器在 Windows 吐 CRLF、靠 git 正規化撿回——要修在源頭,別靠安全網(判例:feedback_encoding_discipline)。」
- ❌ 「修一下 CRLF 問題。」(沒有為什麼,executor 遇到邊界情況只能亂猜)

### 2. Ground truth(已驗證的現實錨點)
你**親自驗過**的事實,附 file:line 或命令輸出 + 驗證時間戳;超過三條用表格。executor 從這裡
出發,不用重新考古——**但它有權重驗**;重驗結果與本欄衝突=觸發 §7(a),這是 feature
(2026-07-04 haiku 實測:executor 重驗發現任務前提已不成立,正確 HOLD 而非幻覺出工作)。
- ✅ 「已驗:`analyze_codebase_graph.py:1151` 與 `run_doc_convergence_inventory.py:831` 的 write_text 無 newline 參數;`run_identity_card.py:233` 已有——照它的寫法。」
- ❌ 「相關程式碼在 scripts/ 下面。」(把考古成本轉嫁給 executor,而且它考古的結論你沒法驗)

### 3. Scope(exact edit list)
逐檔列出要動什麼。列表之外=不准動。
- ✅ 「只改:`scripts/analyze_codebase_graph.py`(2 個 write_text 呼叫)、`scripts/run_doc_convergence_inventory.py`(1 個)。」
- ❌ 「把所有生成器都修好。」(scope 無界=diff 無界=沒人敢收)

### 4. 禁區(Do NOT touch)
明列不准碰的檔案/行為。**預設禁區(每張單自動繼承,不用抄)**:AGENTS.md、MEMORY.md、.env、
`AXIOMS.json`(protected,contract:62——工單明文授權才可動)、`.gitignore`(codex lane 硬禁,
AGENTS.md:106;其他 lane 動它要工單明文授權)、私有記憶資料(memory_base/、memory/soul.db、
memory/self_journal.jsonl)、順手重構、擴 scope、放鬆任何 gate。**executor 同時繼承 AGENTS.md
對其 lane 的全部禁區**(如 codex full-auto 的五禁四必)——本欄只列「這張單額外的」。
- ✅ 「不准動 .gitattributes(git 安全網要留著,修源頭不等於拆網)。」
- ❌ (整欄空白)——空白=executor 以為到處都能碰。

### 5. 驗收條件(可執行,report 前必跑)
命令 + 預期輸出。executor 回報前**必須實跑**;「應該會過」不是驗收。
**lint/format 的檔案範圍用 `git diff --name-only` 推導,不准手抄清單**——首個判例(2026-07-04,
de-bind 工單):手寫五檔清單漏了第六個被改的既有測試,executor 與 reviewer 照單一起漏,
master 上非 required 的 ruff job 紅了一輪(CI #1094)。同時記住:**required checks 綠 ≠ 全部
workflow 綠**,merge 後掃一眼全部 checks。
- ✅ 「跑 `python scripts/analyze_codebase_graph.py` 後,`python -c "print(open('docs/status/codebase_graph_latest.md','rb').read().count(b'\r\n'))"` 輸出 0;black+ruff 兩檔全過。」
- ❌ 「確保沒有 CRLF。」(不可執行=每個人驗的東西不一樣)

### 6. 回報格式(結論進對話,長產物寫檔)
per-file 說改了什麼+證據;長輸出寫到指定路徑,回傳路徑。**禁止**在回報裡宣稱驗收條件之外的
成就(「順便也修了 X」=紅旗,見禁區)。
- ✅ 「回報:每檔一行 diff 摘要 + 驗收命令的實際輸出;完整 diff 寫 `tmp/wo_<id>_report.md`。」
- ❌ 「做完跟我說一聲。」(=收到一句「做完了」,然後你要自己考古它做了什麼)

### 7. 升級條款(什麼時候停下來)
遇到以下情況**停下回報,不硬幹**:(a) spec 與現實衝突(ground truth 錯了)——明說,別默默配合
也別自作主張(判例:constraint-set 委派);(b) 同一子任務失敗 2 次;(c) 發現要碰禁區才能完成;
(d) 驗收條件本身跑不起來。
- ✅ 「發現 write_text 在 3.9 不支援 newline 參數?停,回報 Python 版本前提錯誤。」
- ❌ (硬幹)自己改成 open() 繞過——現在有兩種寫法並存,下一個人不知道哪個是慣例。

### 8. Lane(引擎 + 驗收人)
依 `model_dispatch_protocol.md` 指定引擎/模式/effort;寫明誰驗收、review findings 走
`review_adjudication_protocol.md`。
- ✅ 「Lane:codex exec;驗收:主 agent(read-back + 實跑驗收命令);異議走仲裁協議。」
- ❌ 「找個 AI 做。」

## 最小可用版(小單允許摺疊)

機械小單(< 30 分鐘、單檔、零風險)可摺疊為四欄:Framing 一句 + Scope + 驗收命令 + 禁區繼承預設。
**驗收條件永遠不可省。**

## 誠實限制

- Template 本身不保證單的品質——垃圾 framing 填進好格式還是垃圾;格式只保證垃圾**可被看見**。
- 這是 v1,蒸餾自 codex 工單判例;第一次派給非 codex 引擎(qwen/Gemini)踩到格式不合用,把案例寫回本檔。
