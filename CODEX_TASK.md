# Codex Active Task

This is the active task for Codex. Progress tracking lives in `task.md`.

## ✅ Phase 20: 安全修復 — 完成！
## ✅ Phase 21: API 統一 — 進行中（接近完成）

### 已完成
- ✅ Flask API 補齊 conversation/consent/session-report
- ✅ ChatInterface 改 backend-first
- ✅ Feature Flag 路由策略
- ✅ Live smoke test 全通過
- 測試：299 passed

### 收尾任務
- [ ] 撰寫 `docs/API_SPEC.md`（整理統一後的 API 規格）
- [ ] 確認 Navigator 可連接 localhost:5000

完成 Phase 21 後，請開始：

---

## 🔄 Phase 22: 前端整合

**目標**：讓 Navigator (`apps/web`) 完全使用統一後的 API

### 任務清單
1. 確認 `apps/web` dev 可正常連接 `localhost:5000`
2. 測試 ChatInterface → backend → Council 流程
3. 測試 SessionReport → backend 流程
4. 更新 Navigator 部署設定（Vercel 環境變數）

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
Phase 21: API 統一 🔄 收尾中
Phase 22: 前端整合 ← NEXT
Phase 23: CLI 整合
```
