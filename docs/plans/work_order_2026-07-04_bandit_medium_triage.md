# 工單:bandit 10 個 MEDIUM 分診(2026-07-04)

> Lane:codex(executor)· 模式:codex exec, workspace-write · Reviewer:claude-fable-5(審≠修)
> 出處:外部審計仲裁(`docs/status/external_audit_adjudication_2026-07-04.md`)殘餘清單第 3 條。

## 1. Framing
2026-07-03 重跑的 bandit 報告(`reports/security_bandit_latest.json`)有 58 LOW / 10 MEDIUM /
0 HIGH(唯一 HIGH 已修:semantic_graph MD5)。10 個 MEDIUM 需要逐條分診:真問題修掉;
誤報/刻意設計標 `# nosec BXXX` **並附一行理由**(裸 nosec = 禁區)。

## 2. Ground truth
- 報告:`reports/security_bandit_latest.json`(generated_at 2026-07-03T20:19:37Z);
  用 `python -c "import json;d=json.load(open('reports/security_bandit_latest.json',encoding='utf-8'));[print(r['test_id'],r['filename'],r['line_number'],r['issue_text'][:60]) for r in d['results'] if r['issue_severity']=='MEDIUM']"` 列出十條。
- bandit 1.9.3 已裝。倉庫慣例:UTF-8/LF、black 100、修改處註解說「為什麼」不說「改了什麼」。

## 3. Scope
1. 逐條分診 10 個 MEDIUM:
   - **修**:確有風險且修法不改行為契約(如 subprocess 無 timeout → 加 timeout;
     yaml.load → safe_load;binding 0.0.0.0 若非刻意 → 127.0.0.1)。
   - **標**:誤報或刻意設計 → `# nosec BXXX — <一行理由>`。
   - **不確定 → 停**(升級條款):governance/fail-closed 相關的行為改動不准自行判斷,
     列入報告的 escalation 節。
2. 修完重跑 bandit 覆寫 `reports/security_bandit_latest.json`,MEDIUM 目標=0(全修或全標注)。
3. 被改檔案的既有測試必須照跑。

## 4. 禁區(預設繼承外)
- 不改任何行為契約(fail-closed 路徑、gate 語義);拿不準=停。
- 裸 `# nosec`(無理由、無 BXXX 編號)禁止。

## 5. 驗收(公式含 untracked;sandbox pytest 用 --basetemp=tmp/pytest)
```
python -m bandit -r tonesoul -f json -o reports/security_bandit_latest.json ; python -c "import json;d=json.load(open('reports/security_bandit_latest.json',encoding='utf-8'));print('MEDIUM:',sum(1 for r in d['results'] if r['issue_severity']=='MEDIUM'),'HIGH:',sum(1 for r in d['results'] if r['issue_severity']=='HIGH'))"
python -m pytest tests/ -q -k "<被改模組名的測試>" --basetemp=tmp/pytest
{ git diff --name-only --diff-filter=ACM; git ls-files -o --exclude-standard; } | grep '\.py$' | xargs black --line-length 100 --check
{ git diff --name-only --diff-filter=ACM; git ls-files -o --exclude-standard; } | grep '\.py$' | xargs ruff check
```

## 6. 回報
`tmp/bandit_triage_report.md`:十條逐一(檔:行 / 判定 修|標|停 / 理由)+ 驗收實際輸出。

## 7. 升級條款
同 template §7;外加本單特有:行為契約拿不準=停。

## 8. Lane
codex exec(workspace-write);reviewer=claude-fable-5;終審=owner。

## 9. 執行與仲裁紀錄(2026-07-04 回填)

### 執行(codex)
十條 MEDIUM 全數判「標」,零行為變更:7×B113 為 bandit 1.9.3 誤報(原碼**本來就有**
computed timeout,工具認不出表達式)、B108 demo 路徑可覆寫、2×B608 非 SQL 注入面
(參數化查詢的固定片段拼接 / HTML 模板 f-string)。每個 `# nosec` 均帶 BXXX+一行理由
(裸 nosec 禁令遵守)。無任何一條觸發「行為契約拿不準」的停止條款。
報告:tmp/bandit_triage_report.md。

### Reviewer(claude-fable-5,審≠修)
- 逐條讀 diff:確認全為註解添加,7 條 B113 的既有 timeout 在 diff 上下文親眼驗證;
  ystm/render 的空 f-string 前綴寫法笨但值等價,收。
- 驗收替跑:相關測試 **443 passed**;black+ruff 淨;
  bandit 重跑 **MEDIUM: 0, HIGH: 0**。**收。**

### 終審
owner(併入 owner-decisions PR)。
