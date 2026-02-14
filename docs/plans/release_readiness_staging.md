# Release / Readiness Staging Checklist

最後更新：2026-02-14

來源文件：
- `docs/RELEASE_v0.1.0_PLAN.md`
- `docs/SMALL_BOAT_MVP.md`

## Stage 0: 程式碼基線（Release Gate）

- [ ] `pytest -v --tb=short --maxfail=5`
- [ ] `black --check --line-length 100 tonesoul tests`
- [ ] `ruff check tonesoul tests`
- [ ] `pytest tests/red_team -q`

## Stage 1: 安全與文件

- [ ] 生成 vulnerability assessment
- [ ] README 與部署文件同步更新

## Stage 2: 本地小船 MVP（Ollama）

- [ ] `ollama list` 確認模型已下載
- [ ] `LLM_BACKEND=ollama python -c "from tonesoul.llm import create_ollama_client; c = create_ollama_client(); print(c.generate('hello'))"` 可回應
- [ ] 低張力訊息走快路徑（log 含 `council skipped`）
- [ ] 高張力訊息啟動議會（log 含 `council activated`）
- [ ] `pytest tests/ -x -q` 維持現有測試綠燈

## Stage 3: 發布產物

- [ ] Git tag `v0.1.0`
- [ ] GitHub Release notes
- [ ] 測試與覆蓋率 artifact
- [ ] 安全報告 artifact

## 當前阻塞與重跑指令

- Backend persistence 外部驗收目前阻塞：`https://tonesoul52.onrender.com/api/health` 在 2026-02-14 驗證時回應 HTTP 502/timeout。
- 重跑指令：
  - `python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com`
  - `python scripts/verify_backend_persistence.py --base https://tonesoul52.onrender.com --timeout 40`
