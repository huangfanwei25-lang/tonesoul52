# ToneSoul 入門指南

> Purpose: ToneSoul 的繁體中文快速上手指南，說明安裝、基本流程與核心概念入口。
> Last Updated: 2026-03-23

ToneSoul 將治理核心（`AXIOMS.json`、`law/constitution.json`）與語義引擎（`tonesoul/`）結合，這份中文指南帶你走完安裝、示範流程，並串連核心概念。

## 1. 安裝流程

1. 複製倉庫（`git clone`）。
2. 建立虛擬環境並安裝依賴：
   ```bash
   python -m venv .venv
   .venv/Scripts/activate
   pip install -r requirements.txt
   ```
3. 確認 `pytest` 可用，以便執行治理檢查。

## 2. 快速範例（Quick Example）

1. 定義初稿：
   ```python
   draft = "ToneSoul 可在治理中穩定協作。"
   context = {"topic": "safety"}
   ```
2. 啟動 `PreOutputCouncil`：
   ```python
   from tonesoul.council import PreOutputCouncil

   council = PreOutputCouncil()
   verdict = council.validate(draft_output=draft, context=context)
   print(verdict.to_dict())
   ```
3. 檢查 `verdict`（包含 `APPROVE`、`REFINE`、`DECLARE_STANCE`、`BLOCK`）以及 `council_verdict` 的語義投票、coherence score。

## 3. 核心概念速覽

- **語義責任（Semantic Responsibility）**：每句輸出都是可追蹤的決策，請閱讀 `docs/philosophy/semantic_responsibility_theory.md` 深入理解。  
- **PreOutputCouncil**：整合 Guardian、Analyst、Critic、Advocate 四個視角，讓輸出通過多角度審查。  
- **TSR + Drift**：追蹤 `DeltaT/DeltaS/DeltaR`，過度漂移或 tension 即觸發修正，參見 `docs/core_concepts.md` 與 `docs/philosophy/truth_vector_architecture.md`。  
- **StepLedger & Axioms**：所有決策寫入 `StepLedger`，`AXIOMS.json` 是硬性約束，請勿破壞其結構。  
- **黃凡威意圖模型（Fan-Wei Context）**：閱讀 `memory/fan_wei_context.md` 了解創造者如何期望 AI 以誠實、共創的態度運行。

## 4. 延伸建議

- 執行 `python -m pytest tests/test_pre_output_council.py` 驗證 Council 流程。  
- 閱讀 `docs/philosophy/observer_and_observed.md` 了解 ToneSoul 如何治理「觀察者」。  
- 查看 `AGENTS.md`、`docs/TRUTH_STRUCTURE.md`、`spec/council_spec.md`，以便再改動治理路徑前獲得整體框架資訊。  
