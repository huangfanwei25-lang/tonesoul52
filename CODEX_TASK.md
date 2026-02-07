# Codex Active Task

This is the active task for Codex. Progress tracking lives in `task.md`.

## ✅ Phase 20: 安全修復 — 完成！
## ✅ Phase 21: API 統一 — 完成！

### 已完成
- ✅ Flask API 補齊 conversation/consent/session-report
- ✅ ChatInterface 改 backend-first
- ✅ Feature Flag 路由策略
- ✅ Runtime drift hardening
- ✅ Live smoke test 全通過
- 測試：299 passed

---

## 🔄 Phase 22: 前端整合

**目標**：讓 Navigator (`apps/web`) 完全使用統一後的 API

### 任務清單
1. 撰寫 `docs/API_SPEC.md`（整理統一後的 API 規格）✅
2. 確認 `apps/web` dev 可正常連接 `localhost:5000` ✅（smoke）
3. 測試 ChatInterface → backend → Council 流程 ✅（smoke）
4. 測試 SessionReport → backend 流程 ✅（smoke）
5. 更新 Navigator 部署設定（Vercel 環境變數）✅（文件完成：`docs/VERCEL_DEPLOY.md`，待平台套用）

### 驗證標準
- `npm --prefix apps/web run dev` + `python apps/api/server.py` 可正常互動
- Vercel 部署後可連接 backend

---

## 📦 組件提醒

| 組件 | 狀態 |
|------|------|
| Navigator 前端 | Phase 22 整合中 |
| YuHun CLI | Phase 23 |
| Dashboard | 待評估 |

---

## 路線圖

```
Phase 20: 安全修復 ✅
Phase 21: API 統一 ✅  
Phase 22: 前端整合 ← CURRENT
Phase 23: CLI 整合
```

---

## 新增：7D 審計框架

已加入 `docs/7D_AUDIT_FRAMEWORK.md` 和 README。
目前缺口：RDD (紅隊測試) 與 DDD/SDH gate 升級策略。

### Phase 24（提案）：7D 落地
1. 建立 `tests/red_team/` 最小對抗測試集（已擴充至 11 tests）
2. 以 `scripts/verify_7d.py` 彙整七維檢查結果
3. SDH gate 決議：維持 SOFT_FAIL（已定案）
4. DDD SLA：7 天 stale 門檻（已定案）
5. systemic betrayal user confirmation gate（已接到 orchestrator，待細化規則）
