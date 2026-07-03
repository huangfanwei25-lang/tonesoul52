# 【治理決策記錄】market/ 子套件封存(2026-07-03)

> **狀態**:EXECUTED(owner 於 2026-07-03 對 repo atlas 交還清單回覆「依照你的建議」,
> 本項建議=執行封存;更早的 gate 是 2026-06-15 owner 決策「下次 consolidation 時
> archive,除非 governance wire-in 落地」——至 2026-07-03 無 wire-in,gate 過期 18 天)。

## 決策

把台股分析子套件整組移出 tracked tree:

- 模組 ×4:`tonesoul/market/{__init__,analyzer,data_ingest,world_model}.py`
- 專屬腳本 ×6:`scripts/{hunt_margin_safe_live,hunt_margin_safe_stocks,probe_finmind_schema,run_full_market_pipeline,run_market_analysis_1326,run_market_scanner}.py`
- 專屬測試 ×5:`tests/{smoke_test_market,test_data_ingest,test_market_analyzer,test_market_data_ingest,test_market_world_model}.py`

**恢復方式**(照 corpus 前例):`git checkout f6300db -- tonesoul/market scripts/hunt_margin_safe_live.py ...`
(f6300db = 移除前最後一個含全部檔案的 commit);本機另有完整副本
`.archive/market_archived_2026-07-03/`(.archive/ gitignored)。

## 為什麼

- **Off-thesis**:語魂是問責框架,不做 alpha(「錢的判斷永遠冷」是 owner 長期原則;
  conscience-layer 方向的 finance 介面走 #226 的 calibration wrap,與這包無關)。
- **Gate 過期未執行**:in-file marker 自 2026-06-15 載明 archive 條件,18 天無人
  wire-in;留著=每次盤點都要重新解釋它為什麼還在。
- **零核心依賴**(2026-07-03 重驗):tonesoul/ 內無任何非 market 模組 import 它;
  唯二非專屬引用是 (a) `scripts/run_repo_semantic_atlas.py` 的**路徑字串**
  (canonical_paths,該工具對缺失路徑回報 `available=false`,line 472,優雅降級)、
  (b) 歷史文件(chronicles/plans,不動)。

## 張力來源

- SUCCESSOR_MAP §6 曾列 market 為「strongest archive candidate」但也警告「不 blind-delete」
  ——本次非 blind:importer 重驗 + 本地備份 + 恢復指令 + 本記錄。
- `analyze_codebase_graph.py` 的 LAYER_MAP 保留 `"market": "domain"` 條目(照 corpus
  前例:`"corpus": "evolution"` 也還在)——無害,graph 掃不到檔案就不會出現。
- 除此之外「無」。

## 可逆性

**HIGH**:單一 `git checkout <hash> -- <paths>` 即全量恢復;無資料遷移、無 API 消費者、
無狀態檔。graph artifacts(module 數 303→299)在本 PR 合併後由 TTL 機制自然重生,
不在本 PR 內重生(避免與 PR #274 的 graph artifacts 衝突)。

## 驗證

- `pytest --collect-only`:全套收集無 import error(見 PR 描述的實跑輸出)。
- `python -c "import tonesoul"` 正常。
- 完整 suite green 以 PR required check(Test Python 3.12)為準——本記錄不在
  post-change 全套 run 存在前宣稱 suite-green。
