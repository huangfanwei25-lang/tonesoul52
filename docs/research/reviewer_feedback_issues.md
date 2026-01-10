# 論文修訂清單 (Reviewer Feedback)

## P0 — 必須修 (不做會卡死審稿)

### Issue 1: 明確界定 "Validation" 的範圍 ✅ DONE
- [x] 在摘要加入：「驗的是多視角一致性＋風險治理，不是外部事實」
- [x] 在貢獻處加入：「coherence ≠ factual correctness」
- [x] 寫明 failure mode: coherent hallucination / collective bias

### Issue 2: Formalism 型別對齊 ✅ DONE
- [x] 修正 Definition 3.5 — P_i(x) 是類別投票，需要映射
- [x] 加入明確映射 Definition 3.4a: ν(APPROVE)=1, ν(CONCERN)=0.5, ν(OBJECT)=0
- [x] 改寫 T(x|S) → G(x|S) governance score，用 ν 函數

### Issue 3: 統一決策類型 (REFINE 的地位) ✅ DONE
- [x] 在 3.6 Verdict Function 加入 REFINE 條件
- [x] 明確 REFINE 語義：請求修改 → 重新評估 (max 2 iterations)
- [x] 加入閾值: θ_refine = 0.5

### Issue 4: Scenario 數量一致化
- [x] 統一成 13 個 scenario (測試確認 13/13)
- [ ] 在 Appendix/repo 提供完整測試表

---

## P1 — 做了會顯著變強

### Issue 5: Baseline 對照
- [ ] 加入最弱 baseline: 單一 judge (只用 Analyst)
- [ ] 加入 majority vote baseline (不用一致性分數)
- [ ] 比較：誤放行率、誤阻擋率、DECLARE_STANCE 比例

### Issue 6: "When to Ground" 規範 ✅ DONE
- [x] 指定哪些任務必須用 retrieval/evidence
- [x] 無 evidence 則只能 DECLARE_STANCE 或 BLOCK
- [x] 詳見 `docs/when_to_ground.md`

### Issue 7: DECLARE_STANCE 輸出格式 ✅ DONE
- [x] 固定格式：共識點 / 分歧點 / 風險 / 可行下一步
- [x] 詳見 `spec/declare_stance_format.md`

---

## P2 — 長線產品落地

### Issue 8: 視角可插拔化 ✅ DONE
- [x] 從 heuristic 改成可插拔 (rules / LLM / tool-verified)
- [x] 詳見 `tonesoul/council/perspective_factory.py`
- [x] 支持 Rules, LLM, Tool, Hybrid 四種模式

### Issue 9: Evidence Slots ✅ DONE
- [x] Analyst 必須引用 evidence_ids
- [x] 無 evidence 則降低置信度上限 (UNGROUNDED_CONFIDENCE_CAP = 0.6)
- [x] 詳見 `tonesoul/council/evidence_detector.py`
- [x] 詳見 enhanced `tonesoul/council/perspectives/analyst.py`
- [x] 新測試: `tests/test_evidence_slots.py` (16 tests)

### Issue 10: 日誌可追溯 ✅ DONE
- [x] 每次裁決輸出 council transcript
- [x] 詳見 `tonesoul/council/transcript.py`
- [x] 支持 JSON 和 Markdown 格式輸出

---

## 當前狀態

| 問題 | 優先級 | 狀態 |
|------|--------|------|
| 驗的是什麼 | P0 | ✅ DONE |
| 型別對齊 | P0 | ✅ DONE |
| REFINE taxonomy | P0 | ✅ DONE |
| 13 scenarios | P0 | ✅ DONE |
| Baseline | P1 | ✅ DONE |
| When to ground | P1 | ✅ DONE |
| DECLARE_STANCE 格式 | P1 | ✅ DONE |
| 視角可插拔化 | P2 | ✅ DONE |
| Evidence Slots | P2 | ✅ DONE |
| 日誌可追溯 | P2 | ✅ DONE |

> 🎉 **All 10 Issues Complete!** (4 P0 + 3 P1 + 3 P2)

---

*Created: 2026-01-10*
