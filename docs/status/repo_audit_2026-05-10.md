# 倉庫整體 Audit 報告 — 2026-05-10

> 作者：Claude (claude-opus-4-7) + Fan-Wei
> 範圍：`c:\Users\user\Desktop\倉庫`（master + feat/wire-epistemic-label-into-perspectives 分支）
> 目的：給 Fan-Wei 一份「整體架構 / 結構 / 不足 / 該整理」的白話審視。
> 注意：本報告是 **快照（snapshot）**，不是長期維護文件；整理動作真的執行時請以當下 `git status` 為準。

---

## 一句話摘要

倉庫**核心已成熟**（v1.0.0 公開、v1.2 Tool-First 已 ship、Council/Memory 子系統穩定），**主要的雜訊在 local 工作層（disk space）而不是 git tree**；真正卡住的「不足」是**對外敘事與 thesis sync 還沒對齊**（5/5 的 epistemic-defense 升級還沒進主要對外面）。

---

## 1 ─ 整體架構：四個 surface 類型

把整個 repo 用「角色」看而不是用「目錄」看，會清楚一點：

| Surface | 對應目錄（tracked） | 角色 |
|---|---|---|
| **Canonical Code** | `tonesoul/` | 唯一有效的程式碼來源（CLAUDE.md 明文）|
| **Apps / Surfaces** | `apps/`, `api/`, `extensions/`, `site/` | 對外端點：API server、web、dashboard、council-playground、VSCode 擴充、靜態站 |
| **Docs / Spec** | `docs/`, `AXIOMS.json`, `DESIGN.md`, `AGENTS.md`, `README.md`, `task.md` | 治理規則 + 架構說明 + 進行中的 phase 紀錄 |
| **Datasets / Fixtures** | `PARADOXES/`, `data/`, `examples/`, `experiments/`, `knowledge/`, `knowledge_base/` | Council 驗證資料、demo、研究素材 |
| **Sandbox** | `games/under_the_island/` | Phase 867 的雙線實驗（Route A 公開 / Route B 私有）|
| **Submodules / Sidecars** | `OpenClaw-Memory`, `tonesoul_evolution/`*, `memory/`* | 私密記憶、evolution 層、runtime soul.db |

\* `tonesoul_evolution/` 與 `memory/` 大部分內容在 `.gitignore`，repo 裡只留進入點。

**核心程式 `tonesoul/` 子層（25 個 subpackage）**（按概念分群）：

- **治理核**：`council/`（Guardian/Analyst/Critic/Advocate/Axiomatic 五個視角 + verdict + transcript）、`governance/`、`gates/`、`deliberation/`
- **記憶層**：`memory/`（soul_db、decay、crystallize、phase transitions）、`semantic/`（embedder + concept store + graph index）、`evolution/`（context distiller、corpus builder）、`corpus/`（consent-driven ingestion）
- **流程**：`pipeline/`、`perception/`、`scribe/`、`tech_trace/`、`loop/`
- **接口**：`backends/`（file_store / Redis）、`gateway/`、`llm/`（Claude/Gemini/Ollama clients）、`inter_soul/`（multi-agent bridge）、`tonebridge/`
- **觀察 / 領域**：`observability/`、`market/`、`ystm/`、`yuhun/`、`shared/`

---

## 2 ─ 子層結構：按 tracked top-level 目錄逐一交代

只列**真的在 git 裡**的東西（`git ls-tree HEAD --name-only`）：

```
.agent/        — agent 設定區
.github/       — workflows + issue templates
.gitignore     — 164 行、寫得認真（細節見 §4）
.gitmodules    — OpenClaw-Memory submodule

頂層 markdown:
AGENTS.md AI_ONBOARDING.md AXIOMS.json CLAUDE.md CONTRIBUTING.md
DESIGN.md LETTER_TO_AI.md LICENSE MEMORY.md README.md README.zh-TW.md
SOUL.md install.sh Makefile package.json package-lock.json
pyproject.toml pytest.ini security_best_practices_report.md task.md

頂層子目錄:
.agent/        agent metadata（保留）
.github/       CI workflows
api/           serverless API（Vercel）
apps/          多個 app（dashboard / web / council-playground / hud / cli / ...）
data/          測試固定資料
docs/          所有正典文件
examples/      可執行範例（quickstart 在這）
experiments/   實驗區
extensions/    VSCode 擴充
games/         under_the_island sandbox
integrations/  外部整合
knowledge/     知識素材
knowledge_base/ 知識素材
memory/        runtime 入口（內容大部分 .gitignore）
OpenClaw-Memory/ submodule
PARADOXES/     Council 用 paradox dataset
scripts/       161 個 utility script
site/          GitHub Pages 內容
spec/          spec 草稿
tests/         431 個 test 檔
tonesoul/      正典程式碼
tools/         工具腳本
zenodo_upload/ 學術 archive 包

commit_attribution.json governance_state.json — runtime governance state
```

**沒列出的東西全部不在 git 裡**（local-only）。

---

## 3 ─ 不足（gaps）

按重要度排，分三層。

### 3.1 對外敘事（最重要）— thesis sync 還沒做完

**問題**：5/5 的 thesis sharpening（epistemic defense 對 probabilistic optimization）已經進 README、進 thesis-defender skill、進 4 條 memory entry，但**還沒進**：

- 朋友寫的 v8/v10 landing page（still "AI governance framework / trustworthy"）
- 多個對外文件仍用 "auditable, traceable, **trustworthy**" 三連、過度承諾
- 6 pillars vs 3 mechanisms 的 reframe 沒做下去

**操作意涵**：對外 surface 的 framing 跟內部 thesis 有 1-2 週 lag。下一波對外動作前要先 sync。

### 3.2 結構性 gap（Phase 858/863 已找到、部分還沒收尾）

從 task.md 跟 codebase_graph 找出的 honest violation（19-23 條）：

- `governance/` reach into `evolution/`（`council.runtime → benevolence`、`governance.kernel → resistance`）— 要嘛 widen `ALLOWED_DEPS`、要嘛反向依賴
- `mcp_server` 是唯一 `infrastructure` 模組伸進 `governance/` + `pipeline/` — 該重分類成 `surface/gateway`
- `tonebridge` 從 pipeline 反向呼叫
- `__init__.py` 的 re-export 造成的 false positive

**操作意涵**：body map 真實但還在 19-23 條紅燈、需要一次架構決策 pass。

### 3.3 cold-agent routing — Phase 862 測試出來的事還沒補完

cold agent 從 README 進來時走 `README.md → tonesoul/<x>.py → architecture/...SUBSYSTEM_GUIDE.md`、**從不讀 body map** (`docs/status/codebase_graph_latest.md`)。Phase 863 已在 README / `tonesoul/__init__.py` / DESIGN.md 補 pointer、但實際 routing 改變需要再測一次。

### 3.4 Demo / Visual 載體（朋友 review 點到的）

- 沒有跟 thesis 同源的 visual identity（朋友的 `geometry_self_checked.html` 是候選、但檔案還沒進 repo）
- Council 5 perspectives 的視覺化沒有
- Categorical-refusal vs probabilistic-softening 對比動畫沒有

---

## 4 ─ 該整理的部分（cleanup）

### 4.1 分清楚：「git 裡的雜訊」 vs 「local 磁碟雜訊」

**在 git 裡的雜訊（真的要清）**：少。`.gitignore` 工作有效。

**Local 磁碟雜訊（disk space、不影響 repo）**：很多。包括：

| 路徑 | 大小估 | 狀態 | 行動 |
|---|---|---|---|
| `.archive/` | ~8.3 GB | 不在 git、CLAUDE.md 明文「不要讀」| 想釋放空間就 `rm -rf .archive`、不影響 repo |
| `models/` | ~6.1 GB | 不在 git、但 `.gitignore` **沒明寫** | 加一行 `models/` 到 `.gitignore` 比較穩 |
| `temp_ci_lint/`, `temp_ci_memory_hygiene/`, `temp_ci_tonesoul52_job62898495163/` | 小 | 2026-02 stale、`.gitignore` 已涵蓋 | 直接刪 local |
| `htmlcov/`, `.coverage`, `coverage.xml`, `test_results.txt` | ~13 MB | 舊 coverage artifact、`.gitignore` 已涵蓋 | 直接刪 local |
| `dist/`, `tonesoul52.egg-info/`, `graphify-out/` | ~2 MB | build artifact、`.gitignore` 已涵蓋 | 看心情 |
| `tmp/`, `temp/` | 變動 | runtime scratch | 留著沒差 |
| `__pycache__/`（頂層）| 變動 | python cache | 留著沒差 |

### 4.2 `.gitignore` 一個建議補丁

確認 `models/` 的條目，加一行：
```gitignore
models/
```

（避免哪天有人 `git add models/` 不小心 commit 6 GB 模型權重。）

### 4.3 `.gitignore` 不該補丁的部分（防誤判）

下面這些**看起來像 cleanup、實際不是**：

- `PARADOXES/` — Council/RDD canonical paradox dataset、tracked、**不要動**
- `games/under_the_island/` — Phase 867 sandbox、tracked、**不要動**
- `experiments/` — 86 KB 小、tracked、留著
- `knowledge/` vs `knowledge_base/` — 看起來重複、實際不同用途（前者素材、後者已索引）、不要合併
- `memory_base/` 跟 `memory/` — 前者是可重建索引（rebuildable from `graphify-out/build_graph.py`）、後者是 runtime soul.db 入口、**不是同一個東西**
- `tonesoul_evolution/` — 私有 evolution 層、`.gitignore` 涵蓋

### 4.4 頂層 `add_reset.py` 之類 one-off

`add_reset.py`、`moltbook_feed.json`、`moltbook_register.html`、`Modelfile.formosa1`：

- 全都 **不在 git 裡**（`.gitignore` 涵蓋）
- 想清就 local 刪、不影響 repo

---

## 5 ─ 不該動的東西（防止下一個 agent 誤刪）

按 CLAUDE.md 與 AGENTS.md 的 protect 清單：

- `AGENTS.md`、`MEMORY.md`、`.env*`、`AXIOMS.json` — 受保護的人類管理檔案
- `OpenClaw-Memory/` — submodule、不能 commit 到公開 repo
- `tonesoul/` — 唯一正典、不要在 `.archive/` 找東西複製過來
- `commit_attribution.json` — Phase 857 的 process lesson 紀錄
- `governance_state.json` — runtime governance 狀態、不要手動編輯
- `PARADOXES/` — Council/RDD dataset
- `task.md` 的 active program 段 — 是現行短板、不是 archive

---

## 6 ─ 建議下一步（按優先序）

優先序我**只列、不執行**、由你決定。

1. **對外 thesis sync**（最高）— v10 的 hero / 6 pillars / over-claim 都還沒對齊新 thesis。需要朋友配合或我們直接 fork 一份。
2. **`geometry_self_checked.html` 進 repo**（中、待檔案）— 等你提供檔案，建議放 `apps/web/public/geometry/` 或 `docs/visual/`。
3. **Phase 858 honest violations 收尾**（中）— 19-23 條 layer violation 需要一次架構決策。
4. **Local disk 釋放**（低、隨時可做）— `.archive/` 8 GB + `models/` 6 GB = 14 GB。
5. **`.gitignore` 加 `models/`**（低、5 秒）— 防誤 commit。
6. **Phase 862 cold-agent routing 再測**（低）— Phase 863 補完後沒重測。

---

## 7 ─ 不確定 / 需要你確認

1. **`geometry_self_checked.html` 在哪**？task-c 跟主 repo 都找不到、等你提供。
2. **`models/` 6.1 GB 內容是什麼**？是 GGUF / safetensors / 別的？決定 `.gitignore` 規則。
3. **`tonesoul_evolution/`** 你私下還有在跑嗎？還是已經凍結？影響「該不該補一條 health check」。
4. **`zenodo_upload/`** 是已 archive 還是準備下次再 upload？

---

## 8 ─ 一句話結語

倉庫**結構是健康的**、`.gitignore` 用心、Phase 系統紀律好。**沒有結構災難**、但有兩個明顯 lag：對外 thesis 還沒同步、honest layer violation 還在 19-23 條沒收尾。Local 磁碟空間是另一條獨立軸、跟 repo 健康度無關、想清就清。

朋友 review 那邊真正要做的不是「重寫網頁」、是「等 thesis sync 完再決定 v9/v10 retarget」。

---

## 附錄 A — 檢查指令（給未來的你 / 下個 agent）

```bash
# 看哪些頂層真的在 git 裡
git ls-tree HEAD --name-only

# 看 untracked 但不在 .gitignore 的東西（潛在誤判）
git status --short | grep "^??"

# 看 body map 最新 layer 報告
cat docs/status/codebase_graph_latest.md

# 跑 repo healthcheck
python scripts/run_repo_healthcheck.py

# 看當前進行中的 phase
head -100 task.md
```

## 附錄 B — 此次 audit 的限制

- **沒實際跑**：`.archive/` 沒打開過（CLAUDE.md 明文不讀）
- **沒實際跑**：`tonesoul_evolution/` 沒打開（私有層）
- **沒實際跑**：每個 sub-app 的 build / test，只看了結構
- **沒驗證**：每個 sub-package 內部的 dead code（依靠 `tonesoul/` 沒 TODO 標記推斷、不是 100% 把握）
- **時間點**：2026-05-10、master HEAD `b94f444`、活分支 `feat/wire-epistemic-label-into-perspectives-20260504`
