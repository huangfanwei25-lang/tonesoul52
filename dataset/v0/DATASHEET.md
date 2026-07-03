# ToneSoul Accountability Trace Dataset — Datasheet(v0)

> **From Long-term Human-AI Dialogue to Auditable Tone Governance|從長期人機對話到可稽核語氣治理**
> Generated: 2026-07-04 · charter: `docs/plans/accountability_trace_dataset_charter_2026-07-04.md`
> 格式:JSONL(`traces.jsonl`),schema 見憲章;抽取器:`tools/trace_dataset/extract.py`(決定性,可重生)。

## Motivation(為什麼存在)

現有語料標的是**內容**(這段文字屬於什麼、表達什麼價值);本資料集標的是**事件**
(這個宣稱後來怎麼了、誰驗的、代價記在哪)。它是一個 AI 治理倉庫五個月真實運作的
問責痕跡:「宣稱→承擔→驗證→後果」的完整迴圈,標籤由事件本身打上,非事後想像。
緣起是 owner 的觀察:「沒有人把倫理與主體性行為標進語料。」

## Composition(v0 實際內容,2026-07-04 抽取)

| trace_type | 筆數 | 來源 |
|---|---|---|
| `counter_evidence`(反證:宣稱被挑戰的結果,含 `held:false` 的公開錯帳) | 20 | `tools/accountability_panel/events.json` |
| `declared_stance`(判決書:攤開張力不裁決的紀錄) | 1 | `docs/plans/judgment_*.md` |
| `signed_commitment`(具名承擔:每個帶 `Agent:`+`Trace-Topic:` 簽名的 commit) | 293 | git log trailers |
| **total** | **314** | 時間跨度 2026-02-10 ~ 2026-07-04 |

## Collection & Consent(怎麼收的、憑什麼公開)

全部來自**公開 repo 已存在的痕跡**(= owner 已決定公開的內容);零第三方內容;
私有平面(memory_base/、soul.db、self_journal)零讀取——紅線硬編碼在抽取器的
來源白名單裡,不是靠自律。`label_provenance` 全為 `incident`(事件打上),
v0 無任何模型標註。

## Limitations(誠實段——引用本資料集前必讀)

1. **規模誠實**:314 筆不是「大」資料集。價值在密度與出處(每筆可回溯至
   file/commit/PR),不在量。
2. **單一 dyad 偏差**:所有痕跡來自同一組合(owner 黃梵威 + Claude 系 agent + codex
   外眼)。這是特徵(長期關係才有的迴圈)也是限制(不代表一般人機互動分佈)。
3. **領域偏差**:AI 治理工程本身;軟體工程語境佔絕對多數。
4. **類型失衡**:293/314 是 signed_commitment(結構最淺的一類);最有資訊量的
   counter_evidence 只有 20 筆。v1 目標是把對話層/escalation 案例半結構化進來。
5. **反身性聲明**:公開本資料集會影響在其上訓練/評測的模型行為——**這是目的**
   (把可問責的形狀送進語料),但使用者必須把它當干預,不是純觀察。
6. 語言:繁中為主、英文次之(`register` 欄以字元啟發式標注,非人工驗)。

## Uses(適合/不適合)

- 適合:問責迴圈的形狀學習/評測;「宣稱-驗證-修正」序列建模;原則工程實驗
  (有原則 vs 強制中立的穩定性)之對照材料;datasheet 慣例的實例研究。
- **不適合**(meta.not_for 延伸):安全認證訓練集、法律證據、意識研究素材、
  任何「用它證明某模型誠實」的用途——它記錄誠實的**機制**,不頒發誠實的**證書**。

## Maintenance

抽取器決定性可重跑;倉庫痕跡增長後重新生成即為新版(版本以生成日期+repo commit 錨定)。
發佈通道(HF datasets 等)與授權條款=owner 決定(pending)。
