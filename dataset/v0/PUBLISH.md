# 出航手冊 — HF 發佈(一次性)

> **已出航(2026-07-04)**:https://huggingface.co/datasets/Famwin/tonesoul-accountability-traces
> ——四步全走完:whoami=Famwin、驗證器綠(318)、repo 建立、上傳 4 檔;線上驗證:卡片渲染 ✓、
> license cc-by-4.0 ✓、traces.jsonl 行數 318=驗證器數字 ✓(viewer 轉檔暖機中,行數以 resolve
> 直抓驗證)。本手冊保留供後續版本重新出航(見「版本紀律」)。
> 前提:owner 已跑 `hf auth login`(token 於 hf.co/settings/tokens 建立,型別 **Write**)。
> 授權:CC BY 4.0(owner 決定 2026-07-04);通道:HF datasets(owner 三決之一)。

## 步驟(依序,每步驗證)

```bash
# 0. 驗登入(應顯示帳號名,不是 Not logged in)
hf auth whoami

# 1. 出海前驗證(fail-closed;任何 finding 都不准上傳)
python -m tools.trace_dataset.validate

# 2. 建 dataset repo(一次性)
hf repo create tonesoul-accountability-traces --repo-type dataset

# 3. 上傳 v0 三件套(traces.jsonl + DATASHEET.md + README.md=資料集卡)
hf upload Famwin/tonesoul-accountability-traces dataset/v0 . --repo-type dataset

# 4. 線上驗(merged ≠ live 紀律)
#    開 https://huggingface.co/datasets/Famwin/tonesoul-accountability-traces
#    確認:卡片渲染、license 顯示 cc-by-4.0、traces.jsonl 行數 = 驗證器印出的 records 數
```

## 版本紀律

v0 錨定於 2026-07-04 抽取(318 筆);之後倉庫痕跡增長,重新 `extract` + `validate` +
更新 DATASHEET 計數,即為新版(同 repo 覆蓋上傳,HF 有版本歷史)。**驗證器綠了才准傳**
——它會抓 schema 破損、洩漏形狀、私有平面引用、與 DATASHEET 數字漂移。
