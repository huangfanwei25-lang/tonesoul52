# 外部技術審計仲裁紀錄(2026-07-04)

> 來源:owner 轉交的外部審計「技術檢驗清單」(.docx,桌面;審計方法=**從 zip 解包**,
> 非 git clone——此方法論本身產生若干預期落差,審計者多數有自標 EXPECTED/ENV GAP)。
> 仲裁協議:`docs/engineering/review_adjudication_protocol.md`(reviewer 無決策權;
> 逐條獨立重現後才存在)。仲裁者:claude-fable-5;終審:owner(已於對話中裁「好」,
> 授權執行修復)。
> 先記這個:**24 個 PASS 是倉庫核心衛生的一次獨立外部驗證**(compileall、303/303 layer
> 宣告、quickstart、CLI、全部 verify_* 腳本綠)——外眼沒欠我們,我們也不只欠外眼錯誤。

## 逐條判定(全部經獨立重現)

| # | 指控 | 判定 | 關鍵證據 | 處置 |
|---|---|---|---|---|
| 1 | 驗證環境未閉合(缺 flask/hypothesis/freezegun) | **NARROWED** | 三者皆已宣告(pyproject.toml:33,52,55)——審計者未裝 `[dev]` extras;但「無一鍵自我診斷」核心有理 | **`scripts/doctor.py` 落地**(codex 實作、fable 審,16 檢查/9 測試);README Quick Start 改為 `pip install -e ".[dev]"` + doctor 指引 |
| 2 | submodule 不乾淨(空目錄) | **NARROWED** | zip 本性(審計者對 .git 標 EXPECTED 卻對 submodule 打 FAIL,標準不一);但 README 對 OpenClaw-Memory 零說明屬實;注意 `verify_submodule_integrity.py` 在其環境**正確地 FAIL**=防線工作中 | README 補「optional submodule」說明段 |
| 3 | status artifact stale/不可當 release verdict | **CONFIRMED——且比指控更重** | (a) `reports/` 整目錄在保鮮契約掃描外(verify_status_freshness.py 原僅掃 docs/status);bandit 與 coverage 在此**殭屍化 140 天**;(b) committed `repo_healthcheck_latest.json` = overall_ok:false @ 2026-06-01,與每日綠的 CI 矛盾——根因:**workflow 只 upload-artifact,從不 commit 回**(repo_healthcheck.yml:110-116) | 契約擴至 `reports/`(scan_dirs + meta.timestamp 嵌套支援 + 2 測試;現追 **81 artifacts**);bandit 重跑(2026-07-03Z,58L/10M/1H;唯一 HIGH=semantic_graph MD5→已加 `usedforsecurity=False`);**coverage 重跑:43% 是化石,實測 88.8%**(8,091 tests)——staleness 藏了 45 個百分點的**進步**;healthcheck 本地重生——追根過程本身成了判例鏈:fresh run 揭出 (i) 本機 6,175 loose objects+240 dangling(→`git gc --prune=now`)、(ii) audit_7d 的 TDD=0 = **本機 venv 缺 pytest-xdist,而 doctor 上線首日的探測清單沒含 xdist**(doctor 的第一個自身盲區,已補探測+裝依賴);最終 run **overall_ok=true, failing=[]**(2026-07-03T21:40Z),本 PR 提交的即此真判決 |
| 4 | 部署邊界無說明 | **REFUTED(如其所述)** | `docs/ARCHITECTURE_DEPLOYED.md` 存在且詳細(§6 專講 apps/web + Vercel 拓撲) | 成立的殘餘=可發現性:README 補兩行指標 |
| 5 | 維護熱點過大 | **CONFIRMED** | unified_pipeline 3,686 行、ChatInterface.tsx 1,948 行(實測吻合;與 codebase graph 一致) | 已在 repo_atlas 記錄;**依 SUCCESSOR_MAP 紀律不在本輪拆**——需專門工單+多眼驗證;審計者「最後才拆、先 web 後 pipeline」的排序簽收 |

## 審計者修復排序 vs 實際執行

他的排序(doctor → freshness → submodule 說明 → 部署文件 → 最後拆大檔)**照單執行前四項**,
第五項刻意擱置(理由如上)。他排序的品味與倉庫既有紀律完全同向。

## 本輪新增判例(進 work_order_template §5)

- lint 公式須含 untracked 新檔(`git ls-files -o --exclude-standard`)——codex 在 doctor
  工單裡抓到工單自身的缺陷。
- `--basetemp` 僅限 sandbox;含非 ASCII 路徑的 Windows 本機會炸 pytest 清理。

## 未攤平的殘餘(誠實清單)

- healthcheck workflow「只上傳不 commit」的結構性問題未改(改法涉及對受保護 master 的
  自動寫回,需要 owner 決策:bot-PR 模式 or 接受「本地手動刷新」慣例)。
- `reports/decay_query_benchmark_latest`(2026-02-21)由新契約浮出為 stale-episodic——
  尚未重跑或降級,留待下輪。
- bandit 10 個 MEDIUM 未逐條處理(多為 subprocess/try-except-pass 慣用型),
  需要一張專門工單。
- 大檔拆分:未動,如上。
