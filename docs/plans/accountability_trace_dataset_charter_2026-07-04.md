# ToneSoul Accountability Trace Dataset|語魂責任痕跡資料集 — 憲章 v0

> **From Long-term Human-AI Dialogue to Auditable Tone Governance|從長期人機對話到可稽核語氣治理**
> Status: charter(owner 已授權動工 2026-07-04:「好啊 試試」);性質=範圍與紅線的**先立後擴**,
> schema 從判例長出來,不從想像長出來。
> 緣起:owner 的觀察——「沒人把倫理與主體性行為標進語料」;本資料集就是把這個倉庫
> 五個月的真實問責痕跡,以帶標籤、帶出處、帶授權的形式交給語料圈。

## 一句話定位

**不是對話資料集,是「問責事件」資料集**:每一筆 trace 記錄一次「宣稱→承擔→驗證→後果」
的完整迴圈,標籤來自真實事故而非事後標註想像。

## 三條紅線(先於一切 schema)

1. **私有平面永不入集**:memory_base/、memory/soul.db、memory/self_journal.jsonl、
   OpenClaw-Memory 本機資料——零讀取、零引用(Axiom 8)。
2. **只收公開 repo 已存在的痕跡**(= owner 已決定公開的);**排除任何第三方內容**
   (如 moltbook 回應中他人的文字/profile——v0 一律不進)。
   **修正案 A(owner ratify 2026-07-04,「可以」)**:**經明示同意、以 CC BY 4.0 讓渡的
   第一人稱貢獻**視為在範圍內(語魂劇場 v2 判斷間收集通道),不可談判的四配套:
   (a) API key 永遠只存使用者客戶端,零經手;(b) 預設匿名,v0 無帳號;
   (c) 提交即發撤回碼,憑碼刪除(Axiom 8 延伸到貢獻者);
   (d) 每筆貢獻先過 council validate 門神,再入 human lane——與 incident 痕跡**分艙,
   絕不混標**(`label_provenance: human`、evidence ≤ E1)。
3. **標籤的標籤**:每個標籤標注它怎麼來的——`incident`(真實事件打上)>`human`(人工標)
   >`model`(模型標,標明哪個模型)。模型標註永遠不冒充事件標註。

## Schema v0(從 events.json 判例延伸,不發明)

每筆 trace(JSONL 一行):

```
id, trace_type, occurred_at, actors{claimant, challenger|null},
register(zh-TW|en|mixed), claim_or_action, outcome, evidence_grade(E0-E4|unlabeled),
label_provenance(incident|human|model:<name>), source_ref(path|commit|PR),
links[](關聯 trace id)
```

### v0 trace_type(只收結構化源,三類)

| 類型 | 來源 | 量級 |
|---|---|---|
| `counter_evidence` | `tools/accountability_panel/events.json`(20 筆,欄位近乎直映) | 20 |
| `signed_commitment` | git log 的 `Agent:` + `Trace-Topic:` trailers(每個簽名 commit = 一次具名承擔) | 數百 |
| `declared_stance` | `docs/plans/judgment_*.md`(判決書,含 REFINE/DECLARE_STANCE 與 correlated-blind-spot 標注) | 個位數 |

### 明確排入 v1+(不在 v0)

對話語域標註(dialogues/、essays——人機共同標、**分歧保留**=雙向校準方法論)、
escalation/拒絕條款觸發案例(散在工單 §9,需半結構化抽取)、漂移家族判例、語氣軸
(ToneBridge,七軸最弱)。v2 才引入開源模型批量複標+標註者間一致性。

## Datasheet 必填的誠實段(照 Datasheets for Datasets)

- **規模誠實**:v0 = 幾十至數百筆;價值在密度與出處,不在量。
- **單一 dyad 偏差**:所有痕跡來自同一組合(owner + Claude 系 + codex);是特徵也是限制。
- **反身性聲明**:公開本資料集會改變未來模型的行為——**這是目的**(把可問責的形狀送進
  語料),但使用者必須知道它是干預不是純觀察。
- **領域偏差**:AI 治理工程本身;不代表一般對話分佈。
- 授權:repo Apache-2.0;資料集授權條款=owner 決定(TBD)。

## 產出位置

`dataset/v0/traces.jsonl` + `dataset/v0/DATASHEET.md`(骨架與判斷=人/主 agent 寫,
統計數字=抽取器 `--stats` 生成後填入)。發佈通道(HF dataset 等)=owner 決定,不在 v0。

## 與倉庫其他綱領的關係

原則工程可測命題(有原則 vs 強制中立的穩定性實驗)之燃料;7/7 後 qwen 時代的
本地實驗素材;「改建築法規」論題的第一個可交付物。
