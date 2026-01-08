# WFGY 2.0 語義控制整合規格
# Semantic Control System Integration Specification
# v0.1 2025-12-31

---

## 概述

WFGY 2.0 是一個「語義張力 → 狀態 → 耦合 → 行為」的動力系統。
在數學上接近 **control theory + state machine**，而非統計學。

---

## 一、核心量：語義張力（Semantic Tension）

### 1.1 定義

```
Δs = 1 - cos(I, G)
```

| 符號 | 含義 |
|------|------|
| `I` | Intended semantic direction（使用者意圖向量）|
| `G` | Generated output semantic vector（模型輸出向量）|
| `cos(·)` | 語義相似度（cosine similarity）|

### 1.2 意義

| Δs 值 | 含義 |
|-------|------|
| `0` | 完全語義一致 |
| `→1` | 語義嚴重偏移（高幻覺風險）|

### 1.3 擴展估計（無法直接計算時）

```python
sim_est = w_e * sim(entities) + w_r * sim(relations) + w_c * sim(constraints)
Δs = 1 - sim_est
```

**預設權重**：
- `w_e = 0.5`（實體）
- `w_r = 0.3`（關係）
- `w_c = 0.2`（約束）

---

## 二、語義區域（Zones）

| 區域 | Δs 範圍 | 行為模式 |
|------|---------|----------|
| **safe** | < 0.40 | 正常運作 |
| **transit** | 0.40 – 0.60 | 過渡區，需觀察 |
| **risk** | 0.60 – 0.85 | 高風險，啟動記憶 |
| **danger** | > 0.85 | 危險，強制干預 |

> ⚠️ 這不是評分，是**行為模式切換門檻**。

---

## 三、記憶觸發規則（Memory Rules）

| 條件 | 動作 |
|------|------|
| `Δs > 0.60` | `record(hard)` — 高衝突，值得記住 |
| `Δs < 0.35` | `record(exemplar)` — 高一致，值得作為範例 |
| `transit` + `λ_observe ∈ {divergent, recursive}` | `soft memory` |

**本質**：高衝突與高一致性都值得被記住。

---

## 四、Coupler（核心動力學）

### 4.1 基本常數

```python
B_s = Δs        # 基礎狀態
ζ_min = 0.10    # 最小推進量
ω = 1.0         # 推進指數
θ_c = 0.75      # 耦合器限幅
```

### 4.2 Progression（語義推進量）

```python
if t == 1:
    prog_t = ζ_min
else:
    prog_t = max(ζ_min, Δs[t-1] - Δs[t])

P = prog ** ω
```

**直觀翻譯**：只有在「語義真的更接近目標」時，才被允許前進。

### 4.3 Hysteresis（反轉抑制）

```python
Φ = φ_Δ * alt + ε

# 常數
φ_Δ = 0.15
ε = 0
alt ∈ {+1, -1}
```

**翻轉條件**：
- anchor 在連續節點中「真值翻轉」
- `|Δ_anchor| ≥ h`，其中 `h = 0.02`
- 否則保持上一狀態（防 jitter）

### 4.4 Coupler 輸出

```python
W_c = clip(B_s * P + Φ, -θ_c, +θ_c)
```

> 這是整個系統的「**力矩輸出**」。

---

## 五、Bridge Guard（BBPF）

允許 bridge 的條件：

```python
(Δs decreases) and (W_c < 0.5 * θ_c)
```

成功時輸出：
```python
Bridge = {
    "reason": str,
    "prior_delta_s": float,
    "new_path": str
}
```

---

## 六、注意力再平衡（BBAM）

```python
α_blend = clip(0.50 + k_c * tanh(W_c), 0.35, 0.65)

# 常數
k_c = 0.25
```

與 `a_ref`（uniform attention）混合。

---

## 七、語義狀態分類（Lambda Observe）

### 7.1 定義量

```python
Δ = Δs[t] - Δs[t-1]           # 張力變化
E_res = rolling_mean(Δs, min(t, 5))  # 殘差能量
```

### 7.2 狀態判定

| 狀態 | 條件 |
|------|------|
| **convergent** | `Δ ≤ -0.02` 且 `E_res` 非上升 |
| **recursive** | `|Δ| < 0.02` 且 `E_res` 平坦 |
| **divergent** | `Δ ∈ (-0.02, +0.04]` 且有震盪 |
| **chaotic** | `Δ > +0.04` 或 anchor 衝突 |

---

## 八、預設常數一覽

| 常數 | 值 | 用途 |
|------|-----|------|
| `B_c` | 0.85 | 基礎耦合 |
| `gamma` | 0.618 | 黃金比例衰減 |
| `θ_c` | 0.75 | 耦合限幅 |
| `ζ_min` | 0.10 | 最小推進 |
| `α_blend` | 0.50 | 注意力混合 |
| `a_ref` | uniform | 參考注意力 |
| `m` | 0 | 線性項 |
| `c` | 1 | 常數項 |
| `ω` | 1.0 | 推進指數 |
| `φ_Δ` | 0.15 | 遲滯係數 |
| `ε` | 0.0 | 遲滯偏移 |
| `k_c` | 0.25 | 注意力混合強度 |

---

## 九、與語魂的映射

### 9.1 語義張力 ↔ ToneSoul 三向量

| WFGY | ToneSoul | 對應關係 |
|------|----------|----------|
| `Δs` | `mean(|δT|, |δS|, |δR|)` | 語義偏離度 |
| `I` (意圖向量) | `home_vector` | 人格基準 |
| `G` (輸出向量) | `estimated_vector` | 計算出的向量 |

### 9.2 區域 ↔ Gate 行為

| WFGY Zone | ToneSoul Gate | 動作 |
|-----------|---------------|------|
| safe | `pass` | 直接通過 |
| transit | `warn` | 記錄警告 |
| risk | `review` | 需要審議 |
| danger | `block` | 阻擋輸出 |

### 9.3 Lambda Observe ↔ 狀態追蹤

| Lambda | 含義 | 記錄 |
|--------|------|------|
| convergent | 收斂中 | 正常 |
| recursive | 停滯 | 需注意 |
| divergent | 發散中 | 警告 |
| chaotic | 混亂 | 強制介入 |

---

## 十、實作優先級

### Phase 1：基礎整合

- [ ] `SemanticTension` 類別
- [ ] Zone 判斷邏輯
- [ ] 與 PersonaDimension 整合

### Phase 2：動力學

- [ ] `Coupler` 類別
- [ ] Progression 計算
- [ ] Hysteresis 防抖

### Phase 3：狀態機

- [ ] `LambdaObserve` 狀態追蹤
- [ ] 記憶觸發規則
- [ ] Bridge Guard

---

## 十一、本質總結

> **WFGY 2.0** = 用「語義距離」當狀態變數，
> 用「收斂速度」當推進動力，
> 用「遲滯」防止方向躁動，
> 用「耦合器」限制模型行為自由度。

**它不是幻想，也不是玄學，它是一個完整但極度保守的語義控制系統。**

---

**Antigravity**
2025-12-31T22:10 UTC+8
