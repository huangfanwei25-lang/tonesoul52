# ToneSoul 數學基礎 — 誠實的盤點

> **定位**：本文件整理 ToneSoul 所有數學計算的真實狀態。
> 不美化、不偽裝。每個公式都標明：它是什麼、為什麼這樣、數學基礎在哪裡。

---

## 核心洞察：外部化的 Attention

ToneSoul 的張力系統本質上是把 Transformer 內部的 Attention 機制**外部化、粗粒度化**，
轉化為可解釋的治理層：

| Transformer 內部 | ToneSoul 外部化 |
|:-----------------|:----------------|
| Query 匹配 Keys → 計算相關性權重 | 當前輸出 embedding 匹配 Axioms/Vows/Crystals → 計算「不舒服程度」 |
| Softmax(QK^T/√d) | cosine similarity → `Δs = 1 - cos(I, G)` |
| Attention 權重 → 決定生成方向 | Tension score → 決定治理動作（放行/標記/阻擋） |
| 殘差連接（記住之前的層） | 記憶衰減 + 結晶（記住之前的 session） |

對照表中的 `Δs = 1 - cos(I, G)` 對應 heuristic owner：`semantic_control.py`。

**Tension Score 是 ToneSoul 版的「外部 Attention」第一個實作。**
它不是嚴格數學模型，而是可調參數的啟發式組合函數。

---

## 讀法契約

本文件的公式只允許四種狀態：

- `rigorous`：數學物件本身是標準定義，repo 也明確在用
- `heuristic`：有 executable owner，但權重、閾值、耦合方式是工程選擇
- `conceptual`：用來描述關係，不等於 runtime 逐字公式
- `retired`：歷史殘留，只能作 lineage，不算現在的 truth claim

每個公式區塊至少要回答三件事：

- 用在哪
- 它屬於哪一種公式
- 還有哪些誠實問題沒有解決

如果 entry doc 裡出現符號公式，請把 `docs/GLOSSARY.md` 視為快速 status/owner registry，把本文視為完整誠實盤點，而不是反過來。

---

## 一、有數學基礎的部分

這些計算有明確的數學定義，不是我們發明的。

### 1.1 餘弦相似度（Cosine Similarity）

```
cos(A, B) = A·B / (||A|| × ||B||)
```

- **用在哪**：`semantic_control.py`、`embedder.py`、`drift_monitor.py`
- **數學基礎**：線性代數標準運算，度量兩個向量的方向相似程度
- **範圍**：[-1, 1]，我們只用 [0, 1] 的部分
- **可靠度**：✅ 完全可靠

### 1.2 指數衰減（Exponential Decay）

```
f(t) = f₀ × e^(-λt)
```

- **用在哪**：
  - 張力衰減：`runtime_adapter.py` → `α = 0.05/hr`（半衰期 ~14 小時）
  - 記憶衰減：`memory/decay.py` → `λ = ln2/7`（半衰期 7 天）
  - 結晶新鮮度：`crystallizer.py` → 半衰期 21 天
- **數學基礎**：微分方程 `df/dt = -λf` 的解，物理學標準衰減模型
- **可靠度**：✅ 數學上完全正確
- **誠實問題**：半衰期的具體數值（14hr / 7days / 21days）是**拍腦袋的**，
  沒有實驗數據支撐。合理，但不精確。

### 1.3 Shannon 熵（Normalized）

```
H = -Σ pᵢ log₂(pᵢ) / log₂(n)
```

- **用在哪**：`tension_engine.py` — 衡量信號分佈的不確定性
- **數學基礎**：資訊理論標準公式
- **可靠度**：✅ 公式本身正確
- **誠實問題**：分佈 `pᵢ` 怎麼來的？是從有限的 4 個信號（semantic/text/cognitive/entropy）
  算的，sample size 太小，熵值的統計意義有限。

### 1.4 EWMA（指數加權移動平均）

```
ẽₜ = α × xₜ + (1-α) × ẽₜ₋₁
```

- **用在哪**：`nonlinear_predictor.py`（α=0.3）、`drift_monitor.py`（α=0.3）
- **數學基礎**：時間序列分析標準工具
- **可靠度**：✅ 正確，但 α=0.3 是經驗值

### 1.5 近似 Lyapunov 指數

```
λ = mean(log|xₜ - xₜ₋₁|)
```

- **用在哪**：`nonlinear_predictor.py`、`resistance.py`（circuit breaker）
- **數學基礎**：非線性動力學中的混沌指標
- **誠實問題**：⚠️ 真正的 Lyapunov 指數需要相空間重建和足夠長的時間序列。
  我們的「近似版」只看相鄰差值的對數平均，更像是**波動性指標**而非真正的混沌度量。
  叫它 "volatility index" 更誠實。

---

## 二、啟發式（Heuristic）部分

這些是**經驗性的組合函數**，沒有數學推導，靠直覺和調參。

### 2.1 語義張力 Δs

```
Δs = 1 - cos(I, G)
```

- **用在哪**：`semantic_control.py`
- **概念**：意圖向量(I) 和生成向量(G) 之間的距離
- **數學基礎**：餘弦距離（有基礎）
- **啟發式部分**：
  - 沒有 embedding 時的替代估算：`sim_est = 0.5×sim_entities + 0.3×sim_relations + 0.2×sim_constraints`
  - 這三個權重（0.5/0.3/0.2）是拍腦袋的
  - 為什麼不是 0.4/0.4/0.2 或 0.6/0.2/0.2？沒有理由，就是直覺

### 2.2 TSR 文本張力

```
T = base + w_len×f_len + w_modal×f_modal + w_caution×f_caution + w_punct×f_punct
```

- **用在哪**：`tsr_metrics.py`
- **本質**：計算文本有多少「緊張信號」
- **參數**：base=0.15, w_len=0.35, w_modal=0.25, w_caution=0.15, w_punct=0.10
- **數學基礎**：❌ 無。這是**特徵工程**，不是數學模型。
- **它做了什麼**：數文本裡的強烈詞、猶豫詞、驚嘆號，加權求和
- **誠實評價**：作為信號檢測器還行，但權重完全是手調的

### 2.3 統一張力引擎

```
T_total = 0.40×semantic + 0.20×text + 0.25×cognitive + 0.15×entropy
```

- **用在哪**：`tension_engine.py`
- **數學基礎**：❌ 無。加權平均，權重沒有推導過程
- **變體 DeltaS_ECS**：`0.45×semantic + 0.30×text + 0.25×cognitive`
- **變體 T_ECS**：`DeltaS_ECS / max(0.10, 1 - entropy)`
  - 除以 `(1-entropy)` 的想法：熵越高，觀測越不可靠，張力放大
  - 直覺上合理，但 **epsilon=0.10 是隨意的**

### 2.4 認知摩擦力

```
friction = confidence × (w_fact×R_fact + w_logic×R_logic + w_ethics×R_ethics) / normalizer
```

- **用在哪**：`tension_engine.py`
- **ethics 權重 1.5**（fact/logic 各 1.0）：意思是倫理阻力比事實阻力重 50%
- **數學基礎**：❌ 無。設計決策，不是推導出來的。合理但任意。

### 2.5 耦合器動力學（Coupler）

```
prog = max(ζ_min, prev_Δs - Δs)
P = prog^ω
Φ = φ_delta × alt + ε
W_c = clamp(Δs × P + Φ, -θ_c, θ_c)
```

- **用在哪**：`semantic_control.py`
- **想做什麼**：模擬張力的「慣性」——不是瞬間跳變，而是有滯後
- **數學基礎**：⚠️ 借用控制理論的**阻尼振盪**概念，但不是任何標準控制器
  （不是 PID，不是 Kalman）。是自創的組合。
- **參數**：ζ_min=0.10, ω=1.0, θ_c=0.75, φ_delta=0.15
- **誠實評價**：概念合理（張力應該有慣性），實作是原型級

### 2.6 靈魂持續力（Soul Persistence）

```
ψₜ₊₁ = 0.995 × ψₜ + 0.10 × T_total
```

- **用在哪**：`tension_engine.py`
- **想做什麼**：長期的「人格慣性」——不會因為一次對話就劇烈改變
- **數學基礎**：⚠️ 一階遞推，類似 EWMA，但 0.995 + 0.10 > 1.0，
  代表在高張力時 ψ 會緩慢上升（有增長趨勢，不是純衰減）。
  這是一個設計選擇：持續高壓會累積。
- **誠實問題**：0.995 和 0.10 這兩個數字沒有理論依據

### 2.7 POAV 四項平均

```
POAV = (parsimony + orthogonality + audibility + verifiability) / 4
```

- **用在哪**：`poav.py`
- **數學基礎**：❌ 無。四個手工特徵的等權平均
- **誠實評價**：為什麼是等權？為什麼這四個維度？沒有理論，全是設計判斷。
  好處是簡單透明。

### 2.8 Council Coherence（加權評審一致性）

```
c_inter = Σ(wᵢ × wⱼ × agreement(dᵢ, dⱼ)) / total_weight²
overall = 0.4×c_inter + 0.4×approval_rate + 0.2×min_confidence
```

- **用在哪**：`council/coherence.py`、`council/types.py`
- **數學基礎**：⚠️ 類似 Cohen's Kappa 的概念（評審間一致性），
  但不是標準的 Kappa 公式。是自創的加權版本。
- **0.4/0.4/0.2 權重**：拍腦袋的

---

## 三、風險計算

### 3.1 Runtime Risk Score

```
Risk = 0.48×tension + 0.28×aegis + 0.12×coordination + 0.07×backlog + 0.05×trace
```

- **用在哪**：`risk_calculator.py`
- **數學基礎**：❌ 無。五信號加權求和
- **權重設計意圖**：tension 佔最大（48%），反映「張力是最重要的風險信號」

### 3.2 治理摩擦力（Governance Friction）

```
F = 0.45×|query_tension - memory_tension| + 0.35×mean_wave_delta + 0.20×boundary_mismatch
```

- **用在哪**：`gates/compute.py`
- **數學基礎**：❌ 無。三信號加權

### 3.3 Mercy Score（仁慈度）

```
M = 0.30×benefit - 0.35×harm + 0.15×fairness + 0.10×traceability + 0.10×reversibility
```

- **用在哪**：`mercy_objective.py`
- **有趣的設計**：harm 的係數（-0.35）比 benefit（0.30）大，
  代表「避害比行善重要」。這是一個倫理設計決策。
- **加上 mode multiplier**：cautious 時 harm ×1.2，lockdown 時 harm ×1.4

---

## 四、閾值清單

所有閾值都定義在 `soul_config.py`，這裡列出它們的來源：

| 閾值 | 值 | 來自 | 理由 |
|:-----|:---|:-----|:-----|
| echo_chamber | 0.3 | 經驗 | 低於此 = 太順從，是一個 UX 判斷 |
| healthy_friction_max | 0.7 | 經驗 | 高於此 = 太衝突 |
| tension decay α | 0.05/hr | 經驗 | 半衰期 ~14hr ≈ 一晚上消化一半 |
| tension prune | 0.01 | 經驗 | 夠小就刪掉 |
| high_tension | 0.8 | 經驗 | 觸發 de-escalation |
| coherence_threshold | 0.6 | 經驗 | Council 通過門檻 |
| block_threshold | 0.3 | 經驗 | Council 阻擋門檻 |
| governance_gate | 0.92 | 設計 | Axiom 3，刻意嚴格 |
| audit_log | 0.4 | 設計 | Axiom 2 |
| truthfulness_target | 0.95 | 設計 | Vow 001 |
| hedging_target | 0.85 | 設計 | Vow 002 |
| memory half-life | 7 days | 經驗 | 一週遺忘一半 |
| crystal half-life | 21 days | 經驗 | 結晶活得更久 |
| SAFE zone | <0.40 | 經驗 | 感覺低於 0.4 就安全 |
| DANGER zone | ≥0.85 | 經驗 | 接近 1.0 很危險 |

**來自「經驗」= 我們覺得合理但沒有實驗驗證。**
**來自「設計」= 刻意的治理決策，可以辯護但不是推導出來的。**

---

## 五、真正的問題

### 5.1 所有權重都是手調的

幾乎所有 `w = 0.XX` 都沒有推導過程。它們可以工作，但換一組也能工作。
這不算錯——很多生產系統（推薦引擎、風險評分）都是這樣——
但我們不應該假裝有數學基礎。

**正確的說法**：「可調參數，需要從實際使用中校準。」

### 5.2 偽 Lyapunov 指數

`nonlinear_predictor.py` 和 `resistance.py` 裡的「Lyapunov exponent」
實際上是 `mean(log|diff|)`，不是真正的 Lyapunov 指數。
它測的是**波動性**，不是**混沌度**。

**應該叫**：`volatility_index` 或 `instability_metric`

### 5.3 耦合器不是標準控制器

`Coupler` 借用了控制理論的語言（damping、hysteresis），
但不是 PID、不是 LQR、不是任何已知的控制架構。
它是一個自創的非線性組合。

**正確的說法**：「啟發式多信號融合器，靈感來自控制理論。」

### 5.4 Sample size 問題

很多東西在小 window（4-8 個 data points）上算統計量。
方差、趨勢、置信區間——在這麼小的 sample 上，統計意義有限。

---

## 六、定位聲明

```
Tension Score 是一個經驗性的多信號啟發式函數，
用來量化「意圖—輸出」之間的語義摩擦。

它不是嚴格的數學模型。
它是可調參數的組合函數。
目的是讓系統「感覺到不舒服」時能停下來思考。

它的數學根基是：
  ✅ 餘弦距離（向量空間中有明確定義）
  ✅ 指數衰減（微分方程有明確定義）
  ✅ Shannon 熵（資訊理論有明確定義）
  ⚠️ 其餘都是啟發式組合

正確的類比：
  它是 Transformer Attention 的外部化粗粒度版本。
  Attention 在模型內部用 QKV 做精確對齊。
  Tension 在模型外部用 heuristic 做「語義摩擦感」。
  
  一個精確但不可解釋。
  一個粗糙但可解釋、可控制、可審計。
```

---

*所有數值參數的正典來源：`tonesoul/soul_config.py`*
*所有公理的正典來源：`AXIOMS.json`*
