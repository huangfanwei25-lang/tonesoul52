# Release / Readiness Staging Checklist

最後更新：2026-02-14

來源文件：
- `docs/RELEASE_v0.1.0_PLAN.md`
- `docs/SMALL_BOAT_MVP.md`

## Stage 0: 程式碼基線（Release Gate）

- [x] `pytest -v --tb=short --maxfail=5`
- [x] `black --check --line-length 100 tonesoul tests`
- [x] `ruff check tonesoul tests`
- [x] `pytest tests/red_team -q`

Stage 0 最新驗證（2026-02-14）：
- `python -m pytest -v --tb=short --maxfail=5` -> pass（849 passed）
- `python -m black --check --line-length 100 tonesoul tests` -> pass
- `python -m ruff check tonesoul tests` -> pass
- `python -m pytest tests/red_team -q` -> pass（26 passed）

## Stage 1: 安全與文件

- [x] 生成 vulnerability assessment
- [x] README 與部署文件同步更新

Stage 1 最新驗證（2026-02-14）：
- `python -m bandit -r tonesoul -f json -o reports/security_bandit_latest.json`（有 finding，報告可產生）
- `pip-audit -r requirements.txt --format json --output reports/security_pip_audit_latest.json`（0 vulnerabilities）
- `python scripts/generate_vulnerability_report.py --bandit reports/security_bandit_latest.json --pip-audit reports/security_pip_audit_latest.json --output reports/security_vulnerability_assessment_latest.md`（已更新報告）
- `README.md` 與 `docs/VERCEL_DEPLOY.md` 已同步更新 walkthrough / release gate 引導

## Stage 2: 本地小船 MVP（Ollama）

- [x] `ollama list` 確認模型已下載
- [x] `LLM_BACKEND=ollama python -c "from tonesoul.llm import create_ollama_client; c = create_ollama_client(); print(c.generate('hello'))"` 可回應
- [x] 低張力訊息可維持低張力調度（dispatch A/B）
- [x] 高張力/衝突可升級為衝突調度（dispatch C，並寫入 verdict metadata）
- [x] `pytest tests/ -x -q` 維持現有測試綠燈

Stage 2 最新驗證（2026-02-14）：
- `ollama list`：可用模型包含 `qwen2.5:7b`、`nomic-embed-text:latest` 等
- `LLM_BACKEND=ollama ... c.generate('hello')`：成功回覆
- `python -m pytest tests/ -x -q`：pass（849 passed）
- `python -m pytest tests/test_unified_pipeline_dispatch.py -q`：pass（3 passed，驗證 A/B/C dispatch trace 與 metadata）

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
