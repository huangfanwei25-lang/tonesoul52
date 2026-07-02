# Output secret redaction — 設計/來源記錄（2026-07-01）

## 這是什麼
`tonesoul/output_redaction.py`：純函數、deterministic、no I/O/LLM。對外 artifact 產出前,遮罩
**credential-shaped** 子字串,附上**可審計的紀錄**(遮了什麼 kind + span,preview 只帶 kind+長度、
不外洩 secret 字元)。

## 來源與界線（誠實標註）
概念來自 AI Team OS(`Fan1234-1/AI-company@7828e7b5`)的 `guardrails.py` redaction——但**只取
output redaction 的想法,程式碼 native 重寫,沒有移植**。經跨模型(codex)確認:
- **不移植它的 input gate**:那個 gate 是 lexical、且 body >16KB 直接 pass-through 可繞,**當不了
  責任閘**。
- **不碰** AI Team OS 的 global hooks / 自更新 / 自主 wake-loop / pipeline_gate。
接 [`consequence_structure_calibration_2026-06-30.md`] 的評估脈絡(AI-company = 不安裝、只萃取)。

## Native 設計選擇（比來源更保守/更誠實）
- **SECRETS 預設、PII(email)opt-in**:語魂內容合法含 email(創作者、被引作者);blanket PII 遮罩
  會毀真內容。secrets 是高訊號/低誤判的 shape,預設遮才安全。
- **可審計、絕不靜默**:`redact` 回傳遮了什麼。遮罩而不留紀錄,正好是問責的反面。
- **遮 value、保結構**:`api_key=sk-...` → `api_key=[REDACTED:assignment]`。
- **overlap 解析**:同一段被多 pattern 命中時,取最高優先/最長那個,不重複計。

## meta.not_for / 界線
這是 **primitive**:只遮罩 + 回報,**不自動接進 live egress 路徑**(那是獨立、owner-gated 的一步)。
它是 **best-effort deterministic mask,不是 safety certification**,不宣稱「secret 不會外洩」。
lexical redaction 是**地板不是證明**:抓已知 shape、抓不到新編碼。漏一個 shape = 加 pattern+test
的 bug,不是盲信它的理由。

## 狀態
- primitive + tests + probe baseline(`docs/status/output_redaction_eval_2026-07-01.md`)已落。
- **codex(不同模型)round-1 review 完成(2026-07-01)** — 抓到 5 條真 finding,全修 + 各加回歸測試:
  - **F1** env-style key 漏遮(`OPENAI_API_KEY=` 因 `\b`+`_` 不匹配)→ 加 `_KEY_PREFIX` env 前綴。
  - **F2** 空白/`&` partial redaction 留下後半 secret → 加 `assignment_quoted` 全 quoted-capture。
  - **F3** connection-string / URL userinfo / Basic auth / Stripe 漏 → 加 targeted patterns。
  - **F4** `sk-` 誤判(`sk-learn-compatible`)→ 收窄到 `sk-ant-`/`sk-proj-` 或 40+ 連續字元。
  - **F5** `:` 吃 prose(`password: strong policy`)→ 未加引號的 value 只認 `=`。
  - idempotency / overlap / audit-preview:codex 判 **no-finding**(設計成立)。
- **known gaps(誠實、刻意)** 見 §N coda:未加引號的 `:` value、無 context 的 raw hex/base64、
  未加引號含空白的 value——候選 opt-in strict/entropy mode。
- **仍 hold merge,等 codex re-confirm**(每次改 pattern 都要不同模型再驗一次)。16 tests + probe 綠。
