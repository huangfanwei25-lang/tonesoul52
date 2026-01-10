# 論文修訂清單 (Reviewer Feedback)

## P0 — 必須修 (不做會卡死審稿)

### Issue 1: 明確界定 "Validation" 的範圍
- [ ] 在摘要加入：「驗的是多視角一致性＋風險治理，不是外部事實」
- [ ] 在貢獻處加入：「coherence ≠ factual correctness」
- [ ] 寫明 failure mode: coherent hallucination / collective bias

### Issue 2: Formalism 型別對齊
- [ ] 修正 Definition 3.5 — P_i(x) 是類別投票，需要映射
- [ ] 加入明確映射：APPROVE=1, CONCERN=0.5, OBJECT=0
- [ ] 或改寫 T(x|S) 只用 C_inter 與置信度

### Issue 3: 統一決策類型 (REFINE 的地位)
- [ ] 在 3.6 Verdict Function 加入 REFINE 條件
- [ ] 或明確 REFINE 是 action 而非 verdict
- [ ] 加入流程圖：投票 → 一致性 → (REFINE loop) → 最終 verdict

### Issue 4: Scenario 數量一致化
- [ ] 統一成 13 個 scenario
- [ ] 或修正為 13 tests (目前是 13)
- [ ] 在 Appendix/repo 提供完整測試表

---

## P1 — 做了會顯著變強

### Issue 5: Baseline 對照
- [ ] 加入最弱 baseline: 單一 judge (只用 Analyst)
- [ ] 加入 majority vote baseline (不用一致性分數)
- [ ] 比較：誤放行率、誤阻擋率、DECLARE_STANCE 比例

### Issue 6: "When to Ground" 規範
- [ ] 指定哪些任務必須用 retrieval/evidence
- [ ] 無 evidence 則只能 DECLARE_STANCE 或 BLOCK

### Issue 7: DECLARE_STANCE 輸出格式
- [ ] 固定格式：共識點 / 分歧點 / 風險 / 可行下一步

---

## P2 — 長線產品落地

### Issue 8: 視角可插拔化
- [ ] 從 heuristic 改成可插拔 (rules / LLM / tool-verified)

### Issue 9: Evidence Slots
- [ ] Analyst 必須引用 evidence_ids
- [ ] 無 evidence 則降低置信度上限

### Issue 10: 日誌可追溯
- [ ] 每次裁決輸出 council transcript

---

## 當前狀態

| 問題 | 優先級 | 狀態 |
|------|--------|------|
| 驗的是什麼 | P0 | 🔄 修改中 |
| 型別對齊 | P0 | 待處理 |
| REFINE taxonomy | P0 | 待處理 |
| 13 scenarios | P0 | ✅ 已對齊 (13 tests) |
| Baseline | P1 | 待處理 |
| When to ground | P1 | 待處理 |
| DECLARE_STANCE 格式 | P1 | 待處理 |

---

*Created: 2026-01-10*
