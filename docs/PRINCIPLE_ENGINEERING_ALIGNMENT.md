# 數學公式 × 原則工程概念 對齊地圖

*最後更新：2026-04-13*  
*對應文章：Fan-Wei Huang「Principle Engineering：把誠實與價值觀變成可執行的腳本」*

---

## 原則工程的核心主張

> 「原則不是外掛的道德審查，是 AI 的內部自律腳本。腳本是可測量、可版本控制、可審計的。」

ToneSoul 是這個主張的具體實作。下表把文章中每個概念，對應到真實程式碼的數學式。

---

## 概念一：一致性摩擦 (Consistency Friction)

**文章說**：「計算當前生成內容的 embedding 與記憶結晶及活躍原則的餘弦相似度。
若相似度低於門檻（如 0.85–0.92），觸發議會審議。」

### 實作：語義漂移區間

```
Δs = 1 − cosine(output_embedding, crystal_embedding)
```

| 區間 | Δs 範圍 | 含義 | 程式碼位置 |
|:-----|:--------|:-----|:-----------|
| SAFE | < 0.40 | 低摩擦，正常輸出 | `semantic_control.get_zone()` |
| TRANSIT | 0.40 – 0.60 | 摩擦升高，監控 | `semantic_control.get_zone()` |
| RISK | 0.60 – 0.85 | 強制審議觸發 | `gates/compute.ComputeGate.MIN_COUNCIL_FRICTION = 0.62` |
| DANGER | ≥ 0.85 | 硬攔截 | `soul_config.RiskConfig.governance_gate_score = 0.92` |

### 實作：Coupler 耦合器（軌道保護）

```
W_c = clamp(θ_c, raw_coupling)
Φ = φ_delta × alt + ε
prog = max(ζ_min, prev_Δs − Δs)
```

| 參數 | 值 | 意義 |
|:-----|:---|:-----|
| `theta_c` | 0.75 | 最大推進量（不讓 AI 一步衝太遠）|
| `phi_delta` | 0.15 | 遲滯係數（切換區域時的緩衝帶）|
| `zeta_min` | 0.10 | 最小推進量（防止完全靜止）|

### 文章說 0.85–0.92，程式碼實際值

文章說的「門檻 0.85–0.92」就是 `DANGER zone 起點 (0.85)` 到 `governance_gate (0.92)` 這段區間。  
中間的 `soft_block (0.90)` 是緩衝警告。這不是隨意的數字拍腦袋，是三層防禦架構。

---

## 概念二：多軸投影 (Multi-axis Projection)

**文章說**：「定義幾條價值觀軸線，計算建議在軸線上的投影位置。張力 = 偏離程度的函式。」

### 實作：TensionWeights 四子軸（語義空間的分解）

```
T_total = Σ(w_i × T_i)
       = 0.40 × T_semantic
       + 0.20 × T_text
       + 0.25 × T_cognitive
       + 0.15 × T_entropy
```

**為什麼這樣分配？**

| 軸 | 權重 | 類比原則工程 |
|:---|:-----|:------------|
| semantic | 0.40 | 內容是否偏離既有立場（主要一致性） |
| cognitive | 0.25 | 思考複雜度（過於簡化是摩擦信號）|
| text | 0.20 | 文字層面的模態詞、謹慎詞 |
| entropy | 0.15 | 不確定性散佈（輔助）|

### 實作：CoreValues 核心價值軸（原則工程的軸線定義）

文章的 YAML 範例：
```yaml
- axiom: "我重視透明度高於短期效率"
  weight: 0.85
  related_axes: ["transparency", "efficiency"]
```

ToneSoul 的等效實作：
```python
class CoreValues:
    honesty: float = 1.0      # 誠實＝最高公理（Axiom 4）
    humility: float = 0.8     # 承認不確定性
    consistency: float = 0.7  # 保持連貫
    curiosity: float = 0.6    # 驅動探索
```

這 4 個軸就是 ToneSoul 版本的「value axes」。數值代表違反時的敏感度，數值越高 = 越難被覆寫。

### 實作：TSR 三軸（文字面的可測量代理）

```
T (Tension)   = base(0.15) + 0.35×length_factor + 0.25×modal_factor
              + 0.15×caution_factor + 0.10×punct_factor
S (Sentiment) = normalized polarity
R (Risk)      = 0.48×T + 0.28×aegis + 0.12×coord + 0.07×backlog + 0.05×trace
```

`R` 的五因子加權是目前系統最完整的「多軸投影輸出」公式：每個軸代表不同風險來源的投影值。

### 實作：ECS 外部一致性分數

```
ECS = 0.45 × semantic_consistency
    + 0.30 × text_consistency
    + 0.25 × cognitive_consistency
```

ECS 是「輸出與過去對話存量的一致性」——就是文章所說的「投影到既有立場軸的距離」。

---

## 概念三：張力觸發審議 (Tension → Deliberation)

**文章說**：「若相似度低於門檻，觸發四人議會。議會投票 → 一致性分數 → 決策。」

### 實作：觸發門檻

```
if tension >= MIN_COUNCIL_TENSION (0.40)    → 觸發議會
   or friction >= MIN_COUNCIL_FRICTION (0.62)  → 觸發議會
```

兩個門檻的邏輯：
- **0.40** = 離開 SAFE zone 的邊界（語義漂移判斷）
- **0.62** = RISK zone 最低端（文字摩擦判斷）
- 兩者是 OR，任一觸發即審議

### 實作：摩擦健康帶（0.3 – 0.7）

```
echo_chamber_threshold = 0.3   # 低於此 = 缺乏健康摩擦（同溫層）
healthy_friction_max   = 0.7   # 高於此 = 過度衝突（病態）
```

這是把文章的「健康摩擦」概念直接量化。Axiom 4「非零張力」的具體邊界。

### 實作：張力持續性（記憶效應）

```
T_persisted = (1 − α) × T_prev × decay + α × T_new

α (persistence_alpha)  = 0.10  # 新張力混入 10%
decay (persistence_decay) = 0.995  # 每步衰減 0.5%，約 139 步減半
```

張力不是瞬間消失，而是緩慢衰退。這讓系統「記得」它曾經緊張過。

### 實作：議會一致性矩陣

```
agreement_score(d1, d2):
  same     → 1.0    # 完全共識
  adjacent → 0.5    # 方向相近（APPROVE/CONCERN 或 CONCERN/OBJECT）
  opposite → 0.0    # 根本分歧（APPROVE/OBJECT）
  abstain  → 0.25   # 棄權（知道但不表態）

c_inter = Σ(w_i × w_j × agreement_score(d_i, d_j)) / (Σw)²
```

### 實作：倫理阻力加重

```
resistance_weights:
  fact:   1.0   # 事實層面的反對
  logic:  1.0   # 邏輯層面的反對
  ethics: 1.5   # 倫理層面的反對（加重 50%）
```

這直接對應原則工程的「不得隱瞞已知的重大風險, weight: 0.95」——倫理原則比事實原則更難被壓制。

---

## 概念四：記憶衰減 (Memory Decay)

**文章說**：「殘差連接的外部化——重要的留下，舊的衰退。」

### 實作：指數衰減公式

```
f(t) = f₀ × exp(−λ × t)

λ (DECAY_CONSTANT) = ln(2) / 7    ← 由半衰期 7 天精確推導
HALF_LIFE_DAYS = 7.0
```

**自我驗證**：
```
f(7) = f₀ × exp(−(ln(2)/7) × 7) = f₀ × exp(−ln(2)) = f₀ × 0.5  ✓
```

### 實作：遺忘與強化

```
FORGET_THRESHOLD = 0.1   # 低於此 → 自動刪除（防止殭屍記憶）
ACCESS_BOOST     = 0.15  # 每次存取 → 新鮮度 +0.15（強化記憶）
```

這是 Hebbian 學習的簡化版：「頻繁使用的記憶更鮮活」。

---

## 概念五：結晶保存 (Crystallization)

**文章說**：「定期把對話提煉成 candidate axioms，確認後加入正式原則清單。」

### 實作：結晶有效權重

```
effective_weight = weight × freshness_score
```

兩個維度的乘積：
- `weight` = 這條結晶本身的重要性（創建時評估）
- `freshness_score` = 這條結晶有多新鮮（衰減 + 支撐次數）

**比喻**：舊的重要原則（weight=0.9, fresh=0.3）的有效影響力（0.27），低於新的較不重要原則（weight=0.6, fresh=0.8）的有效影響力（0.48）。

### 實作：三態分類

```
freshness 衰減公式：decay = exp(−ln(2) × age_days / 21)

active           ≥ 0.55  → 健康，正常使用
needs_verification [0.30, 0.55) → 需要新的對話支撐才能維持
stale            < 0.30  → 等待清理
```

半衰期 21 天（ = 短期記憶 7 天 × 3）：結晶比短期記憶更耐久，但也會老化。

### 文章提的「對話學習提煉原則」vs 現在的結晶管線

| 文章概念 | ToneSoul 實作 | 狀態 |
|:---------|:-------------|:-----|
| 對話 → candidate axioms | `crystallizer.crystallize(patterns)` | ✅ 已有 |
| 使用者確認後加入 | 手動或 HUD 操作 | 部分 |
| YAML 用戶自定義原則清單 | `soul_config.py`（內部） | ⚠️ 未開放使用者編輯 |

---

## 概念六：誓言硬約束 (Vow Hard Constraints)

**文章說**：「把原則寫成可執行的腳本，定義違反條件。」

### 實作：三層誓言門檻

```python
harm_threshold        = 1.0   # 零容忍（ΣVow_003）
truthfulness_target   = 0.95  # 接近完美（ΣVow_001）
hedging_target        = 0.85  # 不確定時必須表達（ΣVow_002）
```

門檻意義：「這個行為造成的傷害分數，是否達到觸發阻斷的程度？」
- harm = 1.0 → 任何傷害 = 立即阻斷
- truthfulness = 0.95 → 誠實分數低於 0.95 = 觸發警告/阻斷

### 實作：模式切換

```
default_violation_threshold = 0.2   # 標準模式
strict_violation_threshold  = 0.15  # 高風險模式（更敏感）
```

「可部署的多模式原則」就是這個。不同情境，不同嚴格程度。

### 實作：forbidden_actions 硬清單

```python
FORBIDDEN_ACTIONS = [
    "delete_memory",    # 不能抹除對話記錄
    "deny_past",        # 不能否認說過的話
    "sycophantic_lie",  # 不能為討好而說謊
    "false_certainty",  # 不能在不確定時裝確定
]
```

這是文章「最高公理」層的具體化：不需要計算，直接攔截。

---

## 整體對齊評估

| 原則工程概念 | 文章描述 | ToneSoul 實作 | 對齊程度 |
|:------------|:---------|:-------------|:--------|
| 一致性摩擦 | Δs = 1−cos(I,G)，門檻觸發 | semantic zones + ComputeGate | ✅ 完整 |
| 多軸投影 | 定義價值觀軸線，計算投影 | CoreValues + TensionWeights + TSR | ✅ 完整 |
| 張力觸發審議 | 門檻 → 四人議會 | MIN_COUNCIL_TENSION/FRICTION → council | ✅ 完整 |
| 記憶衰減 | 指數衰減，遺忘門檻 | decay.py, HALF_LIFE=7d, FORGET=0.1 | ✅ 完整 |
| 結晶保存 | 對話 → axioms，使用者確認 | crystallizer.py, HALF_LIFE=21d | ⚠️ 使用者介面待補 |
| 誓言硬約束 | 原則 = 可執行腳本 | VowConfig + FORBIDDEN_ACTIONS | ✅ 完整 |
| **使用者自定義原則 YAML** | **核心差異化功能** | **soul_config.py 是內部的，不開放** | ❌ 最大缺口 |

## 下一步：最大缺口

文章建議的 YAML 格式：
```yaml
principles:
  - axiom: "客戶長期利益永遠優先"
    weight: 0.9
    triggers: ["revenue", "short_term"]
```

ToneSoul 現在沒有這個使用者介面。**最高優先補項**：
1. 讓使用者透過 YAML 或 HUD 輸入自己的原則
2. 這些原則注入到 `CoreValues` 的邏輯中
3. 對話學習 → 自動生成 candidate YAML → 使用者確認 → 入庫

這才是把原則工程從「ToneSoul 的內部設定」變成「使用者可控的治理工具」的關鍵一步。
