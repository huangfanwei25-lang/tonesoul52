# 2025-2026 論文分流審計（Peer-reviewed 優先）

日期：2026-02-22  
範圍：`docs/PHILOSOPHY.md`, `docs/PHILOSOPHY_EN.md`, `docs/WHITEPAPER.md`, `docs/RESEARCH_EVIDENCE.md` 與外部來源核對

## 1) 執行規則（本次採用）

1. A 層（可作為事實依據）：已審查來源（期刊、正式會議 Proceedings、標準）。
2. B 層（僅作概念輸入）：preprint / working paper / workshop。
3. C 層（待修正）：引用標題與編號不一致，或來源不可驗證。

---

## 2) A 層：2025-2026 可用（已審查）

1. SafeChain: Safety of Language Models with Long Chain-of-Thought Reasoning Capabilities  
   - 出處：Findings of ACL 2025  
   - DOI：10.18653/v1/2025.findings-acl.1197  
   - 連結：https://aclanthology.org/2025.findings-acl.1197/
2. Tree of Agents: Improving Long-Context Capabilities of Large Language Models through Multi-Perspective Reasoning  
   - 出處：Findings of EMNLP 2025  
   - DOI：10.18653/v1/2025.findings-emnlp.246  
   - 連結：https://aclanthology.org/2025.findings-emnlp.246/
3. Red Queen: Exposing Latent Multi-Turn Risks in Large Language Models  
   - 出處：Findings of ACL 2025  
   - DOI：10.18653/v1/2025.findings-acl.1311  
   - 連結：https://aclanthology.org/2025.findings-acl.1311/
4. Forewarned is Forearmed: Pre-Synthesizing Jailbreak-like Instructions to Enhance LLM Safety Guardrail to Potential Attacks  
   - 出處：Findings of EMNLP 2025  
   - DOI：10.18653/v1/2025.findings-emnlp.266  
   - 連結：https://aclanthology.org/2025.findings-emnlp.266/
5. Benchmarking large language models on safety risks in scientific laboratories  
   - 出處：Nature Machine Intelligence (2026, vol. 8, pages 20-31)  
   - DOI：10.1038/s42256-025-01152-1  
   - 連結：https://www.nature.com/articles/s42256-025-01152-1

---

## 3) B 層：先歸檔哲學 / 概念（未審查）

1. Recursive Language Models (arXiv:2512.24601)  
   - 狀態：arXiv preprint（2025-12 提交，2026-01 修訂）
2. LLM Collaboration With Multi-Agent Reinforcement Learning (arXiv:2508.04652)  
   - 狀態：arXiv preprint
3. On the Dynamics of Multi-Agent LLM Communities Driven by Value Diversity (arXiv:2512.10665)  
   - 狀態：arXiv working paper

建議：以上先作為「概念靈感」與「設計假設」，不作為主線事實聲明依據。

---

## 4) C 層：目前倉庫中的引用風險

1. `docs/PHILOSOPHY.md` 與 `docs/PHILOSOPHY_EN.md` 目前有一條引用：  
   - 文案：Prompting LLMs to Compose Meta-CoT Prompts by Leveraging Multi-Perspective Perspectives  
   - 標記：arXiv:2411.18654
2. 核對結果：arXiv:2411.18654 實際標題為  
   - AToM: Aligning Text-to-Motion Model at Event-Level with GPT-4Vision Reward
3. 判定：引用編號與標題不一致，需改為可驗證來源或降級為無引用概念敘述。

---

## 5) 建議落地（你剛剛要求的策略）

1. 主線文件（架構、治理、安全、RFC）只允許 A 層引用。
2. 哲學文件可使用 B 層，但必須加註「Concept / Not peer-reviewed」。
3. C 層引用先建立修正清單，不直接當證據使用。
4. 每次新增 2025-2026 引用時，先檢查：
   - 是否有 DOI 與正式會議/期刊頁
   - 標題是否與 arXiv/DOI 一致
   - 是否標記層級（A/B/C）

---

## 6) 已有可用基礎

`docs/RESEARCH_EVIDENCE.md` 已經是「Peer-reviewed / standards 優先」框架，可直接作為 A 層主索引；  
本報告只補上 2025-2026 的分流與風險點。
