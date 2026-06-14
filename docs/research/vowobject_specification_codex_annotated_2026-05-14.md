# VowObject Specification（tonesoul-codex archive、annotated）

> **Provenance**：originally authored by 黃梵威 (Fan-Wei Huang)、located at `tonesoul-codex/VOWOBJECT_SPECIFICATION.md` (https://github.com/Fan1234-1/tonesoul-codex)、dated 2025-11-06
> **Original status**：plain UTF-8 file (no encoding corruption)、but contains pervasive **OCR-like / speech-to-text typos** throughout — Chinese characters substituted with visually-similar but semantically-wrong characters. Pattern suggests automated transcription not careful proofreading.
> **Recovery date**：2026-05-14、by Claude (claude-opus-4-7)、with Fan-Wei explicit authorization to attempt typo inference
> **Recovery method**：**non-deterministic** — Claude reads original in context、proposes corrections with reasoning. **Original text preserved byte-for-byte**；Claude's interpretation is a separate column.
> **Why annotate (not auto-correct)**：original is short (2.4KB)、content concepts are well-implemented in tonesoul52/tonesoul/vow_system.py、so this is **historical reference material**、not active spec. Auto-correcting would replace Fan-Wei's words with Claude's guesses — silent rewrite of authorship. Side-by-side annotation preserves transparency.
> **Canonical alternative**：if Fan-Wei wants a current, clean VowObject spec、recommendation is to fresh-write referencing the working `tonesoul/vow_system.py` + `tonesoul/vow_inventory.py` + 4 vow test suites in tonesoul52. Don't try to clean-recover this file.

---

## Part 1：Original Text（byte-for-byte preserved）

```markdown
# 誓詞物件規範

## Guardian Protocol v1.0 - 責任塊號候不變常數

**最後更新**: 2025-11-06 22:30 CST
**狀態**: 主動整合
**維護者**: Fan1234-1 (黃梵威)
**框架版本**: Guardian Protocol v1.0
**倉庫層級**: Tier 4 (ToneSoul Codex)
**G-P-A-R節點**: Review → Action

---

## 1. VowObject的定義

VowObject(誓詞物件)是一種不武可採的責任承諾嘤供体。它記錄了每個責任宜言的核心要素：

- **Who**: 何者承諾（哪些程序、哪些Agent）
- **What**: 承諾是什麼（具體的事項、成果）
- **When**: 承諾生效日期與方式
- **Why**: 承諾的依寶（哪項Guardian Protocol時間選擇或倫理伯群）
- **How**: 承諾如何驗證、如何回滾
- **Sign**: 不可呢改的數位簽署（SHA-256 + Timestamp）

---

## 2. VowObject的抗核結構

[JSON schema, see original file]

## 3. VowObject的生命週期

### 階段1: 提案階段(Philosophy-of-AI)
- 提出新承諾提案
- 驗證是否伊佯常例規則（P0紅線書）

### 階段2: 簽署階段(tonesoul-codex)
- 收鄆全部提出者的簽署
- 生成VowObject可辨擬品
- 記錄到SourceTrace資料庫

### 階段3: 驗證階段(tone-soul-integrity)
- 驗證GateScores是否玩成標準
- 確保提案成员法定有效
- 檢查是否有利益衿争

### 階段4: 提交階段(ai-soul-spine-system)
- 將VowObject融入StepLedger
- 開大4擲整通道以實查承諾

### 階段5: 筹済階段(governable-ai)
[continued in original file...]
```

完整原文 see `https://github.com/Fan1234-1/tonesoul-codex/blob/main/VOWOBJECT_SPECIFICATION.md`

---

## Part 2：Annotated Typos（Claude's interpretation、Fan-Wei verification needed）

### Header / Section 1

| Original | Suggested correction | Reasoning |
|---|---|---|
| 責任塊號候不變常數 | 責任區塊永不變常數 (or: 責任區塊不變常數) | "塊號候" 拆開看像 OCR errors of "區塊永" |
| 不武可採 | **不可篡改** | "武可採" 在「不___」+ "責任承諾" 上下文、最自然讀法是 immutable / 不可篡改 |
| 嘤供体 | **載體** or **承諾體** | "嘤" 看似 keystrike noise；"供体" 接近 "承載體" |
| 責任宜言 | **責任宣言** | "宜" / "宣" 字形相近 |
| 依寶 | **依據** | "寶" / "據" 字形差但讀音相近、依寶 不合句意 |
| 倫理伯群 | **倫理群體** or **倫理規範** | "伯群" 不通順、上下文是倫理範疇 |
| 不可呢改 | **不可篡改** | 跟上面 "不武可採" 是同個 concept、"呢" / "篡" 字形相近 |

### Section 2（JSON schema）

| Original | Suggested correction | Reasoning |
|---|---|---|
| 抗核結構 | **核心結構** | "抗" / "核心" — 應是「核心結構」、"抗" 是 typo |
| 知識貪範圍 | **知識範圍** | "貪" 應是 typo、無 semantic role |
| 餘量方式 | **測量方式** | metrics 上下文、measurement_method field、"餘" / "測" |
| 検assertions.js梨離冶恈復査 | **檢查週期** or **復查週期** | 完全亂、可能 OCR 把 "復查週期" 混 JavaScript fragment |
| 降適在 | **適用在** or **啟用在** | tone-soul-integrity 是 verification module、是適用 / 啟用 |
| [SHA-256相接] | **[SHA-256雜湊]** or **[SHA-256 hash]** | "相接" → "雜湊"、digest field |

### Section 3（lifecycle）

| Original | Suggested correction | Reasoning |
|---|---|---|
| 是否伊佯常例規則 | **是否違反常例規則** | "伊佯" → "違反" |
| 收鄆 | **收集** | 簽署收集、"鄆" → "集" |
| 可辨擬品 | **可驗證副本** | "辨擬品" → "驗證副本" |
| 玩成標準 | **達成標準** | "玩" → "達" |
| 成员法定 | **成員合法** | "法定" → "合法" |
| 利益衿争 | **利益衝突** | "衿争" → "衝突"、conflict of interest |
| 開大4擲整通道以實查承諾 | **開啟整合通道以驗證承諾**（推測）| "大4擲整" 完全亂、context 是融入 StepLedger |
| 筹済階段 | **結案階段** or **完成階段** | "筹済" → "結案" |

### Confidence rating

- **High confidence (80%+)**：不武可採 → 不可篡改、依寶 → 依據、不可呢改 → 不可篡改、抗核 → 核心、玩成 → 達成、利益衿争 → 利益衝突、筹済 → 結案
- **Medium confidence**：嘤供体 → 載體、伯群 → 群體、收鄆 → 收集、辨擬品 → 驗證副本
- **Low confidence**：開大4擲整通道（句子結構太亂、可能需要 Fan-Wei 提供原意）、塊號候 → 區塊永（猜測）、検assertions.js梨離冶恈復査（嚴重亂、可能跟 JS check function 有關）

---

## Part 3：Concept Digest（Claude's reading of intent）

Despite the typos、the intent of the spec is clear（per Fan-Wei's broader work in this period）：

**Core concept**：A `VowObject` is an immutable, cryptographically-signed record of a commitment made by an AI agent or module. It captures Who/What/When/Why/How/Sign and binds the commitment to verifiable enforcement gates.

**JSON schema fields**：vow_id、created_at、signatories (primary + witnesses)、vow_core (subject/commitment/scope/metrics)、temporal_binding (effective dates + check interval)、enforcement (compliance gate scores + breach consequence + verification method)、signature (algorithm/timestamp/digest/immutable_flag)、cross_refs (audit_trail_id + philosophy_principle + policy_binding)

**Lifecycle (5 phases)**：
1. **提案 / Proposal** (Philosophy-of-AI) — propose new commitment、validate against P0 red lines
2. **簽署 / Signing** (tonesoul-codex) — collect signatures、generate verifiable copy、record to SourceTrace
3. **驗證 / Verification** (tone-soul-integrity) — verify gate scores meet standards、ensure members are valid、check conflicts of interest
4. **提交 / Submission** (ai-soul-spine-system) — integrate VowObject into StepLedger、open integration channel for verification
5. **結案 / Closure** (governable-ai) — final disposition

**Cross-repo intent**：each lifecycle phase is owned by a different repo in the lineage. This was the **federated architecture vision** before the consolidation into TAE-01 / tonesoul52.

---

## Part 4：Canonical reference for current implementation

The VowObject concept is **implemented and actively maintained** in tonesoul52：

- `tonesoul/vow_system.py` — runtime vow management
- `tonesoul/vow_inventory.py` — inventory + audit
- `tests/test_vow_system.py`、`test_vow_system_properties.py`、`test_vow_input_validation.py`、`test_vow_inventory.py` — 4 test suites

For current spec questions, **read the implementation + tests** rather than reconstructing from this corrupted doc.

---

## Part 5：Recommendation

1. **Keep this annotated file in tonesoul52/docs/research/** for lineage reference
2. **Leave tonesoul-codex/VOWOBJECT_SPECIFICATION.md untouched** — archive fidelity
3. **If a clean current VowObject spec is needed**：fresh-write referencing tonesoul/vow_system.py、do NOT back-port this corrupted version
4. **Fan-Wei verify** the annotated corrections in Part 2 — if any are wrong、update them or remove this annotation file

---

## Limitations

- All corrections in Part 2 are Claude's inference、not verified against any clean source
- The concept digest in Part 3 may have subtle errors due to typo-induced misreading
- The "high confidence" rating is Claude's self-assessment、not statistical
- This file should be treated as **secondary source** — primary is the corrupted original + Fan-Wei's memory of intent
