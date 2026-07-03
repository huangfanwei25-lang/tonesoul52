# 工單:責任痕跡資料集 v0 抽取器(2026-07-04)

> Lane:codex(executor)· 模式:codex exec, workspace-write · Reviewer:claude-fable-5(審≠修)
> 憲章(先讀):`docs/plans/accountability_trace_dataset_charter_2026-07-04.md` — 三條紅線
> 與 schema v0 以憲章為準,本單只負責機械抽取。

## 1. Framing
把倉庫既有的結構化問責痕跡統一成一份 JSONL,讓「倫理標籤語料」從想法變成檔案。
抽取器只做確定性轉換,不做任何判斷性標註(判斷欄位缺值就標 unlabeled,不猜)。

## 2. Ground truth(2026-07-04 親驗)
- `tools/accountability_panel/events.json`:list of 20 dicts,欄位 lane/claim/
  evidence_at_claim/held/caught_by/correction/method/outcome/evidence_ref(部分早期
  紀錄缺 method/outcome/evidence_ref——**缺就缺,標 null,不補**)。
- git trailers:`git log --format` 可取 `Agent:` 與 `Trace-Topic:`(非 merge commit
  幾乎全有;merge commit 豁免)。倉庫根即 git repo。
- `docs/plans/judgment_open_vs_monopoly_2026-07-02.md`:唯一判決書;標題行、
  「判決:」行、correlated-blind-spot 標注可 regex 抽。
- Python 3.13;倉庫慣例:UTF-8 無 BOM、LF(寫檔一律 `newline="\n"`)。

## 3. Scope(exact edit list)
1. 新檔 `tools/trace_dataset/__init__.py`(一行 purpose)與 `tools/trace_dataset/extract.py`:
   - 三個 extractor 函式(events / commits / judgments),各回傳 list[dict],統一 schema
     (憲章 §Schema v0 的欄位,`label_provenance`:events 與 judgments = "incident",
     commits = "incident";`register` 用簡單啟發:含 CJK → zh-TW,否則 en,混合 → mixed)。
   - commits extractor:`git log --no-merges --format=%H%x00%aI%x00%(trailers:key=Agent,valueonly)%x00%(trailers:key=Trace-Topic,valueonly)%x00%s` 之類**單次呼叫**解析;
     無 Agent trailer 的 commit 跳過(不算 trace)。
   - CLI:`python -m tools.trace_dataset.extract --out dataset/v0/traces.jsonl --stats`
     (--stats 印各 type 計數與時間範圍;寫檔 UTF-8/LF;id = type 前綴+短雜湊,決定性)。
   - **紅線硬編碼**:來源路徑白名單只有上述三個;任何讀取白名單外路徑的程式路徑不得存在。
2. 新檔 `tests/test_trace_dataset_extract.py`:每個 extractor 一組 fixture 測試
   (tmp 假 events.json / 假 git repo 用 subprocess init+commit / 假 judgment md);
   schema 欄位齊全性測試;決定性測試(同輸入兩次輸出相同)。
3. `dataset/v0/` 目錄由 CLI 建立;**不要 commit dataset 產物**(reviewer 決定)。

## 4. 禁區(預設繼承外)
- 憲章三紅線;不讀 docs/outreach/results/(含第三方內容)。
- 不裝新依賴(stdlib + 既有 dev extras)。

## 5. 驗收條件(回報前必跑;lint 範圍公式含 untracked)
```
python -m tools.trace_dataset.extract --out tmp/traces_v0_test.jsonl --stats
python -m pytest tests/test_trace_dataset_extract.py -q --basetemp=tmp/pytest
{ git diff --name-only --diff-filter=ACM; git ls-files -o --exclude-standard; } | grep '\.py$' | xargs black --line-length 100 --check
{ git diff --name-only --diff-filter=ACM; git ls-files -o --exclude-standard; } | grep '\.py$' | xargs ruff check
```

## 6. 回報格式
`tmp/trace_dataset_impl_report.md`:per-file+行號、--stats 實際輸出、驗收輸出、殘餘風險。

## 7. 升級條款
同 template §7。

## 8. Lane
codex exec(workspace-write);reviewer=claude-fable-5;終審=owner。

## 9. 執行與仲裁紀錄(2026-07-04 回填)

### 執行(codex)
- 全 scope 完成:tools/trace_dataset/{__init__,extract}.py + 5 測試;紅線自證
  (報告明列未讀四個禁區路徑);黑名單事件重演:其 sandbox black 非 --diff 模式
  懸住(EXIT:124 如實入報),逐檔 --diff 驗 unchanged 繞過。
- 報告:tmp/trace_dataset_impl_report.md(161 行)。

### Reviewer(claude-fable-5,審≠修)
- 驗收替跑:`--stats` = **314 traces**(20 counter_evidence + 1 declared_stance +
  293 signed_commitment,2026-02-10~07-04);pytest 5/5;black+ruff 淨;
  白名單硬編碼抽查(extract.py:15-16)確認。**收。**
- 正式產物已生成:`dataset/v0/traces.jsonl`(314 行)+ `dataset/v0/DATASHEET.md`
  (判斷欄位由 reviewer 撰寫:limitations 六條含單一 dyad 偏差與反身性聲明)。

### 終審
owner(併入 audit-response PR;發佈通道與授權=owner 另決)。
