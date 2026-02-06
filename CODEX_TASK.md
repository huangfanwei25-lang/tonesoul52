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
1. 撰寫 `docs/API_SPEC.md`（整理統一後的 API 規格）
2. 確認 `apps/web` dev 可正常連接 `localhost:5000`
3. 測試 ChatInterface → backend → Council 流程
4. 測試 SessionReport → backend 流程
5. 更新 Navigator 部署設定（Vercel 環境變數）

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
目前缺口：RDD (紅隊測試)。可列入 Phase 24。
