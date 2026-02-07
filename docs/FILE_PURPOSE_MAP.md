# File Purpose Map

## 目的

統一命名語意，讓「檔名 = 用途」可被快速理解，降低跨代理協作成本。

## 命名規則

- `post_case_*_response.py`：社群討論回應腳本
- `verify_*.py`：驗證/檢查腳本
- `run_*.py`：執行入口腳本
- `tests/test_*.py`：單元與整合測試
- `tests/red_team/*.py`：紅隊對抗測試
- `docs/*.md`：文件與規格
- `reports/*.md`：報告與審計輸出

## 日期規則

- 報告檔名一律使用 `YYYY-MM-DD`
- 範例：`session_summary_2026-02-02_pm.md`

## 禁止命名

- 含模糊語意的詞：`final_final`, `new2`, `temp_last`
- 會造成誤導的詞：`evil`, `attack`（非必要語境）

## 檢查指令

- `rg --files docs reports scripts tests`
- `pytest -q`
- `python scripts/verify_7d.py`
