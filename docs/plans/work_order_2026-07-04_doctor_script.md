# 工單:scripts/doctor.py 一鍵環境診斷(外部審計建議 #1)(2026-07-04)

> Lane:codex(executor)· 模式:codex exec, workspace-write · Reviewer:claude-fable-5(審≠修)
> 出處:外部技術檢驗清單(2026-07-04)最小修復排序第 1 條——「bootstrap/doctor gate:
> 一次檢查 Python deps、Node deps、Git/submodule、ruff/black/pytest 可用性」。
> 仲裁紀錄:docs/status/external_audit_adjudication_2026-07-04.md。

## 1. Framing
外部審計者從 zip 解包後無法自我診斷缺什麼(dev extras 沒裝、node_modules 不在、
submodule 是空殼),浪費了他的時間也讓 8 個 import error 看起來像倉庫壞了。
倉庫只有任務型 preflight,缺一個「新環境第一件事」的自我檢查。

## 2. Ground truth(2026-07-04 親驗)
- 依賴皆已宣告:pyproject.toml `[project.optional-dependencies]` dev(pytest/hypothesis/
  freezegun/pytest-cov 等,:49-56)、flask 在 :33。
- 既有 preflight 均為任務型:scripts/{pr,run_publish_push,run_shared_edit,run_task_board}_preflight.py。
- submodule 判別:`.gitmodules` 宣告 OpenClaw-Memory;空目錄=未 init;
  `git submodule status` 前綴 `-`=未 init、`+`=drift。
- 風格範本:scripts/run_freshness_sweep.py(step 函式回 dict + 總結 + recommendations)。

## 3. Scope(exact edit list)
1. 新檔 `scripts/doctor.py`:唯讀診斷,檢查並逐項回報 PASS/GAP/SKIP:
   - Python 版本(>=3.10);核心 import(tonesoul);dev extras 逐個 import 探測
     (pytest, hypothesis, freezegun, flask, black, ruff——**用 importlib 探測,不執行**);
   - git 存在與否(zip 使用者=GAP + 說明);submodule 狀態(未 init/drift/乾淨);
   - Node 面:node/npm 在不在、apps/web/node_modules 在不在(GAP 附修復指令);
   - 選配工具(codex/gh/ollama):在=版本,不在=SKIP(非 GAP);
   - 結尾:總結行 + 每個 GAP 附一行可複製的修復命令(如 `pip install -e ".[dev]"`、
     `git submodule update --init`、`npm --prefix apps/web install`);
   - `--json` 輸出結構化結果;exit code:0=全 PASS/SKIP,1=有 GAP(**診斷非 gate,
     不用 2**)。檔頭 `__ts_layer__ = "surface"` + `__ts_purpose__`。
2. 新檔 `tests/test_doctor.py`:對檢查函式做單元測試(monkeypatch 模擬缺依賴/
   缺 git/空 submodule 等),**不得依賴真實環境狀態**(在 CI 和本機都要綠)。

## 4. 禁區(預設繼承外)
- doctor 本身零副作用:不安裝、不寫檔(--json 印 stdout)、不打網路。
- 不改任何既有檔案。

## 5. 驗收條件(回報前必跑,lint 範圍用 git diff 推導)
```
python scripts/doctor.py ; echo "exit=$?"
python scripts/doctor.py --json | python -c "import json,sys; json.load(sys.stdin); print('json ok')"
python -m pytest tests/test_doctor.py -q --basetemp=tmp/pytest
black --line-length 100 --check $(git diff --name-only --diff-filter=ACM | grep '\.py$')
ruff check $(git diff --name-only --diff-filter=ACM | grep '\.py$')
```

## 6. 回報格式
寫 `tmp/doctor_impl_report.md`:per-file+行號、驗收命令實際輸出、殘餘風險。

## 7. 升級條款
同 template §7(spec 衝突/敗 2 次/需碰禁區/驗收跑不動 → 停下寫報告)。

## 8. Lane
codex exec(workspace-write);reviewer=claude-fable-5;終審=owner(併入 audit-response PR)。

## 9. 執行與仲裁紀錄(2026-07-04 回填)

### 執行(codex)
- 全 scope 完成:scripts/doctor.py(16 項檢查,唯讀,--json,exit 0/1)+ tests/test_doctor.py(9 案)。
- **升級條款又一次正確觸發**:(a) black --check 在其 sandbox 反覆不返回;(b) sandbox 禁寫
  .git/index → 無法 `git add -N`,工單的 diff-based lint 公式**天生漏 untracked 新檔**
  ——codex 抓到工單缺陷,停下寫報告(tmp/doctor_impl_report.md,135 行)。

### Reviewer(claude-fable-5,審≠修)
- 驗收替跑:doctor 實跑 16 PASS/0 GAP、--json 合法、black+ruff 淨、
  **tests 9/9(預設 temp)**。
- 發現:`--basetemp=tmp/pytest` 在含中文路徑的 Windows 本機觸發 pytest 清理錯誤
  (9 errors 全是 fixture rmtree,非測試本身)——該旗標僅限 codex sandbox 使用。
- 唯讀性抽查:subprocess 皆帶 timeout、無寫檔、無網路。**收。**

### 判例回填
兩條寫回 `work_order_template.md` §5:lint 公式須含 untracked(`git ls-files -o`);
basetemp 旗標的環境邊界。

### 終審
owner(併入 audit-response PR)。
