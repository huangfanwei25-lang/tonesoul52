# ToneSoul 架構收斂 RFC
## 從治理骨架到有意義分歧（Multi-Perspective Decomposition）

日期: 2026-02-23  
對應分支: `master`  
觀測基線: `1408e52`（same-origin primary mock）/ `509ecda`（fallback + integrity）

---

## 1. 目標與結論（先講結論）

目前 ToneSoul 已有可運作的治理骨架，但離「有意義的分歧」仍差最後一哩:

1. `Council` 已能產生品質分數與分歧摘要，但 fallback/證據/視覺上下文狀態尚未完整閉環到 UI gate。
2. `Web API` 已修復 same-origin 鬼打牆，現在是 mock-first 可用；但需明確區分「可用」與「真後端審議」兩種等級。
3. `技能企業化` 已有 AGENTS + SKILL + verify script + memory，但缺 Skill registry / MCP connector / skill-level eval loop。

這份 RFC 的主軸是:  
把「能跑」提升到「可治理、可審計、可擴展」。

---

## 2. 三視角共識（多人格拆解）

### Philosopher（治理與語義責任）
- 優先維持 fail-closed 與 human gate，不接受僅有表面分歧。
- 分歧必須可解釋: 誰反對誰、反對理由、證據來源、建議行動。

### Engineer（執行與可觀測）
- runtime 主幹已在 `CouncilRuntime` + `PreOutputCouncil`，可透過 transcript/provenance 擴充。
- same-origin 已修為 primary mock，應將「mock vs real deliberation」做成明確狀態機。

### Guardian（風險與長期演化）
- fallback 發生已可檢測 (`fallback_triggered`)，下一步是升級為阻斷或升級 gate 條件。
- 企業級缺口在 Skill registry、MCP adapter、QA lessons 自動回流 memory。

---

## 3. 逐檔拆解（核心檔案責任 + 技術債 + 下一步）

### 3.1 治理骨架（Council Core）

1. `tonesoul/council/runtime.py`
- 當前責任: 審議總控、mode observability、escape valve、VTP、provenance。
- 關鍵訊號: `council_mode_observability`（line ~105）、`vtp`/`escape_valve` transcript。
- 技術債: fallback/visual truncation 尚未作為統一治理旗標輸出給上層 gate。
- 下一步: 在 transcript 增加 `fallback_markers`、`visual_context_status`。

2. `tonesoul/council/pre_output_council.py`
- 當前責任: 投票 -> verdict -> divergence 分析 -> self memory。
- 技術債: divergence 與 evidence 欄位沒有完整被前端消費。
- 下一步: 強制把 collaboration/evidence 進 transcript 標準欄位。

3. `tonesoul/council/summary_generator.py`
- 當前責任: `role_tensions`、`quality.score/band/conflict_coverage`。
- 技術債: 缺 fallback/visual truncation 的品質面向，容易只看表面質量分。
- 下一步: 新增 `fallback_markers` / `visual_context_status` 到 divergence payload。

4. `tonesoul/council/perspective_factory.py`
- 當前責任: perspective mode、ollama fallback、visual context 截斷（`VISUAL_CONTEXT_LIMIT=800`）。
- 已完成: `[fallback_to_rules]` marker + `VTP Philosopher fallback to rules` warning。
- 技術債: truncation 目前偏重 Ollama 路徑，需統一到所有 LLM 路徑。
- 下一步: 抽共用 helper 統一 LLM/Ollama truncation + marker 規格。

5. `tonesoul/council/council_cli.py`
- 當前責任: 將 deliberation 輸出給 bridge，已含 `fallback_triggered`。
- 技術債: 仍以 reasoning marker 推斷 fallback，缺結構化 fallback evidence。
- 下一步: 加入結構化 fallback source（perspective + reason + stage）。

---

### 3.2 Web 治理邊界（Next API + UI）

6. `apps/web/src/app/api/chat/route.ts`
- 當前責任: payload 驗證、retry/timeout、same-origin primary mock。
- 已完成: same-origin 直接 mock，不再探測 `/_backend`。
- 技術債: UI 難區分「mock 回應」與「真審議結果」的治理等級。
- 下一步: 在 response 明確加入 `deliberation_level: mock|runtime`。

7. `apps/web/src/app/api/conversation/route.ts`
8. `apps/web/src/app/api/consent/route.ts`
9. `apps/web/src/app/api/session-report/route.ts`
- 當前責任: same-origin primary mock fallback。
- 技術債: fallback reason 雖有，但未統一映射到前端治理狀態條（readiness meter）。
- 下一步: 統一 fallback reason 枚舉 + 前端可視化映射。

10. `apps/web/src/app/api/backend-health/route.ts`
- 當前責任: same-origin 直接健康回覆（`backend_mode: same_origin`）。
- 技術債: 目前是健康檢查，不代表真實 council runtime 可用。
- 下一步: 新增 `governance_capability` 欄位（mock_only / runtime_ready）。

11. `apps/web/src/app/api/_shared/backendConfig.ts`
- 當前責任: same-origin 判斷、backend URL 解析與 Vercel 驗證。
- 技術債: same-origin 對應「mock-first」已成事實，但語義未明文化到文件與 preflight。
- 下一步: 將 policy 同步到 preflight + docs。

12. `apps/web/src/components/ChatInterface.tsx`
- 當前責任: chat orchestration、CouncilChamber/SoulState UI 入口。
- 技術債: fallback_triggered / quality band / role tension 還不夠強制呈現。
- 下一步: 建立「治理狀態列」固定顯示 fallback、quality、core_divergence。

13. `apps/web/src/components/CouncilChamber.tsx`
- 當前責任: 角色審議視覺展示。
- 技術債: evidence 與衝突鏈未完整可視化。
- 下一步: 顯示 `role_tensions + evidence + recommended_action` 三欄。

---

### 3.3 驗證、記憶、技能企業化

14. `scripts/verify_web_api.py`
- 當前責任: web API smoke、same-origin 驗證、council mode 檢查。
- 技術債: 尚未加入 `deliberation_level`/governance capability 驗證。
- 下一步: 增加 mock_only vs runtime_ready 斷言。

15. `scripts/verify_7d.py`
- 當前責任: 7D 全量治理驗證（timeout 已提升為 2400）。
- 技術債: skill-level 評分未入 7D，仍偏系統層。
- 下一步: 新增 skills quality gate（觸發/功能/成本）。

16. `scripts/verify_vercel_preflight.py`
- 當前責任: Vercel 部署前置配置風險檢查。
- 技術債: 尚未反映 same-origin primary mock 政策等級。
- 下一步: preflight 新增 `same_origin_mock_policy` check。

17. `memory/agent_discussion.py`
- 當前責任: 記憶資料正規化、integrity hash、curate integrity suspect。
- 技術債: 未對應 skill-level incident taxonomy。
- 下一步: topic/status 規格化（deploy, governance, skill, security）。

18. `tools/agent_discussion_tool.py`
- 當前責任: audit/append/append-lessons/curate。
- 技術債: 缺自動從 CI/verify 匯入 lesson 的入口。
- 下一步: 新增 `ingest-verify` 命令。

19. `.agent/skills/local_llm/SKILL.md`
20. `.agent/skills/qa_auditor/SKILL.md`
- 當前責任: 本地模型協作與 QA 角色流程。
- 技術債: 缺中央 skill registry 與統一 metadata 契約。
- 下一步: 建立 `skills/registry.json` 與 schema 驗證。

21. `docs/ARCHITECTURE_DEPLOYED.md`
22. `docs/convergence_audit.md`
23. `docs/context_engineering_reference.md`
24. `AGENTS.md`
- 當前責任: 架構/收斂/上下文工程/治理規範文檔。
- 技術債: same-origin mock-first 新政策與 skill registry 尚未完全文檔化。
- 下一步: 文檔同步 + 可執行命令對齊。

25. `task.md`（Phase 108）
- 當前責任: Elisa x ToneSoul integration 任務追蹤。
- 技術債: P0/P1/P2 仍有未完成項（payload profile、preflight status、CI smoke）。
- 下一步: 優先補齊 P0 契約測試與 blocking smoke。

---

## 4. 優先級（P0 / P1 / P2）

### P0（阻塞上線）
1. 完成 Phase 108 的 Elisa P0 契約測試與 verify 場景。  
2. 將 fallback 與治理等級顯示成前端固定狀態（不可隱藏）。  
3. 在 `/api/backend-health` 或 `/api/chat` 補 `deliberation_level`，區分 mock/runtime。

### P1（提升分歧質量）
1. divergence payload 加入 fallback/visual-context status。  
2. CouncilChamber 顯示 role tensions + evidence + recommended action。  
3. 統一 LLM/Ollama visual context truncation 規格與測試。

### P2（企業化擴展）
1. 建立 `skills/registry.json` + schema。  
2. 設計 MCP connector abstraction（skill 入口一致化）。  
3. verify 結果自動回寫 `agent_discussion`（skill QA loop）。

---

## 5. 執行 Phase（可直接貼 task.md）

## Phase 109: Governance Visibility Closure
- [ ] API 增加 `deliberation_level`（mock/runtime）與 fallback 結構化欄位
- [ ] `ChatInterface` 固定顯示 governance status bar（quality/fallback/core_divergence）
- [ ] `verify_web_api.py` 新增治理欄位斷言
**成功標準**: 前端每次回應都能明確判讀是 mock 或 runtime 審議，且驗證腳本可阻擋缺欄位部署。

## Phase 110: Meaningful Divergence Upgrade
- [ ] `summary_generator` 輸出 fallback/visual-context 狀態與 evidence 索引
- [ ] `CouncilRuntime` transcript 貫通新欄位至 API 層
- [ ] `CouncilChamber` 顯示 role_tensions + evidence + recommended_action
**成功標準**: 分歧可追蹤到「角色-理由-證據-建議」，不再只有文字摘要。

## Phase 111: Skill Contract & Registry
- [ ] 新增 `skills/registry.json` 與 metadata schema（license/compatibility/version/triggers/trust）
- [ ] 對 `.agent/skills/*` 執行 registry 校驗
- [ ] 文檔同步 (`AGENTS.md` / `context_engineering_reference.md`)
**成功標準**: skills 可被機器枚舉、驗證、版本化。

## Phase 112: MCP Connector & Enterprise QA Loop
- [ ] 定義 MCP connector 介面（skill invocation contract）
- [ ] `verify_7d.py`/`verify_web_api.py` 納入 skill-level 指標
- [ ] `agent_discussion_tool` 新增 verify 結果匯入路徑
**成功標準**: 技能從變更到部署有可審計的閉環（測試 -> 記憶 -> 追蹤）。

---

## 6. 建議驗證命令（收斂門檻）

```bash
python scripts/verify_web_api.py --web-base <url> --api-base <url> --same-origin
python scripts/verify_7d.py --sync
python scripts/verify_vercel_preflight.py --same-origin
cd apps/web && npx vitest run src/__tests__/apiRoutes.chatTransport.test.ts src/__tests__/apiRoutes.transportFallback.test.ts
```

---

## 7. Decision Record

- 決策 A: same-origin 目前定義為 `mock-first`，不再假設 `/_backend` 可用。  
- 決策 B: fallback 不是隱性容錯，而是治理訊號，必須可視化。  
- 決策 C: 分歧價值以 evidence + tension chain 決定，不以文字長度決定。  
- 決策 D: skills 需從「文件」升級為「可驗證契約資產」。

