---
description: how to perform a professional architecture audit on the tonesoul codebase
---

# 架構審計技能（源自 GPT-5.3/5.4 雙模型分析）

## 核心推理守則

### 1. 證據先行，不空談
每個發現都必須附具體引用：**檔案路徑 + 行號**。
- ✅ `pyproject.toml:70 的 include = ["tonesoul52*"] 但實作目錄是 tonesoul/`
- ❌ 「打包設定可能有問題」

### 2. 用 Git 做診斷，不只看程式碼
Git 本身就是一個診斷工具：
- `git shortlog -sn` → 作者歸屬是否合理
- `git log --format=%f -- <file> | wc -l` → 哪些檔案被改最多次（熱點）
- `git ls-files <dir>` → 哪些不該追蹤的檔案進了版控
- `git submodule status` → 外部依賴是否完整
- `git diff --stat origin/master` → 本地和遠端有多少漂移

### 3. 按風險排序，不按模組排序
分析結果不要按目錄結構排列，要按 **「如果不修會怎樣」** 排序：
1. 資安/資料外洩（P0）
2. 正確性/合約破壞（P0）
3. 工程品質/可維護性（P1）
4. 技術債/美觀（P2）

### 4. 量化一切
- 檔案行數 → 判斷是否需要拆分（>500 行是警訊，>1000 行必須拆）
- 目錄大小 → 判斷是否該從版控移除
- Commit 次數 → 判斷熱點和噪音
- API 端點數 → 判斷面積大小和重複

### 5. 找「多套疊加」問題
最危險的架構債不是某個模組壞掉，而是**同一件事有多個實作**：
- 兩套 API（Flask + Vercel serverless）
- 四套記憶儲存（JSONL + SQLite + Supabase + FAISS）
- 多個 LLM 呼叫路徑（local_llm + tonesoul_llm + ollama_client）

問自己：「這件事的 source of truth 是哪一個？其他的角色是什麼？」

### 6. 檢查「名實不符」
- 套件名叫 `tonesoul52`，目錄叫 `tonesoul/` → 哪個對？
- 規格引用 `body/*`，但目錄結構已變 → 文件過期
- 測試覆蓋率高，但 CI 用 `PYTHONPATH=.` 繞過封裝 → 假的安全感

## 審計執行清單

```bash
# 1. 倉庫基本掃描
git log --oneline -20                    # 最近活動
git shortlog -sn --all | head -5         # 作者分布
git diff --stat origin/master            # 本地漂移
git submodule status                     # 外部依賴

# 2. 大小/衛生
du -sh memory/ models/ *.db *.jsonl      # 大檔偵測
git ls-files --others --ignored          # .gitignore 有效性
python -c "open('.gitignore','rb').read().count(b'\x00')"  # 污染檢查

# 3. 複雜度熱點
find tonesoul/ apps/ -name "*.py" | xargs wc -l | sort -rn | head -10
git log --format=%f -- unified_pipeline.py | wc -l  # 改動頻率

# 4. 架構面積
grep -r "def " apps/api/server.py | wc -l          # API 路由數
find tests/ -name "*.py" | wc -l                    # 測試檔案數

# 5. 契約一致性
grep "include" pyproject.toml                       # 封裝範圍
grep -r "from tonesoul" --include="*.py" | head -5  # 實際 import 路徑
```

## 比對腳本
已建立 `experiments/compare_model_reports.py`，可用於未來任何雙模型 A/B 比對。
