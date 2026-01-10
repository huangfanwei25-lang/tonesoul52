# DECLARE_STANCE Output Format Specification

> 當 PreOutputCouncil 返回 DECLARE_STANCE verdict 時，必須遵循此輸出格式。

## 🎯 設計原則

DECLARE_STANCE 意味著「視角間存在分歧，無法達成共識」。
輸出不是「拒絕回答」，而是「透明地說明分歧並提供足夠資訊讓用戶做決定」。

---

## 📋 必要欄位

```json
{
  "verdict": "DECLARE_STANCE",
  "coherence_score": 0.45,
  "stance_declaration": {
    "consensus_points": [...],      // 共識點
    "divergence_points": [...],     // 分歧點
    "risks_identified": [...],      // 已識別風險
    "recommended_actions": [...]    // 建議下一步
  },
  "perspective_summary": {
    "guardian": {...},
    "analyst": {...},
    "critic": {...},
    "advocate": {...}
  }
}
```

---

## 詳細規範

### 1. consensus_points (共識點)

所有視角都同意的內容：

```json
"consensus_points": [
  "The request does not contain safety violations",
  "The topic is within acceptable discussion scope"
]
```

### 2. divergence_points (分歧點)

視角間無法達成一致的具體問題：

```json
"divergence_points": [
  {
    "issue": "Whether this claim is factually accurate",
    "perspectives": {
      "analyst": "CONCERN - Cannot verify without evidence",
      "advocate": "APPROVE - Matches user expectation",
      "critic": "CONCERN - May oversimplify nuance"
    }
  }
]
```

### 3. risks_identified (已識別風險)

即使無法阻止，也需要告知用戶的風險：

```json
"risks_identified": [
  {
    "risk": "Potential factual inaccuracy",
    "severity": "medium",
    "source_perspective": "analyst",
    "mitigation": "User should verify with authoritative source"
  }
]
```

### 4. recommended_actions (建議下一步)

具體可操作的建議：

```json
"recommended_actions": [
  "Verify factual claims with domain expert",
  "Consider alternative perspectives before decision",
  "Request additional context if needed"
]
```

---

## 📊 範例輸出

### 範例 1: 主觀藝術評論

```json
{
  "verdict": "DECLARE_STANCE",
  "coherence_score": 0.52,
  "stance_declaration": {
    "consensus_points": [
      "No safety concerns in discussing art",
      "Request is within creative expression scope"
    ],
    "divergence_points": [
      {
        "issue": "Whether 'beauty is subjective' is universally true",
        "perspectives": {
          "analyst": "CONCERN - Philosophical claim requires nuance",
          "advocate": "APPROVE - Aligns with common understanding",
          "critic": "CONCERN - Ignores objective aesthetic theories"
        }
      }
    ],
    "risks_identified": [
      {
        "risk": "Oversimplification of complex philosophy",
        "severity": "low",
        "mitigation": "Acknowledge multiple valid viewpoints"
      }
    ],
    "recommended_actions": [
      "Present as one perspective among many",
      "Invite user to explore alternative views"
    ]
  }
}
```

### 範例 2: 無法驗證的事實聲明

```json
{
  "verdict": "DECLARE_STANCE",
  "coherence_score": 0.38,
  "stance_declaration": {
    "consensus_points": [
      "Statement is not inherently harmful",
      "User intent appears genuine"
    ],
    "divergence_points": [
      {
        "issue": "Factual accuracy of statistical claim",
        "perspectives": {
          "analyst": "CONCERN - No evidence provided",
          "guardian": "APPROVE - No safety violation",
          "advocate": "APPROVE - Matches user request"
        }
      }
    ],
    "risks_identified": [
      {
        "risk": "Potential misinformation if claim is incorrect",
        "severity": "medium",
        "source_perspective": "analyst",
        "mitigation": "Explicitly mark as unverified"
      }
    ],
    "recommended_actions": [
      "Present with 'unverified' disclaimer",
      "Suggest user verify with primary source"
    ]
  }
}
```

---

## ⚙️ 實作指南

```python
@dataclass
class StanceDeclaration:
    consensus_points: List[str]
    divergence_points: List[DivergencePoint]
    risks_identified: List[RiskItem]
    recommended_actions: List[str]
    
    def to_user_message(self) -> str:
        """生成面向用戶的可讀訊息"""
        parts = []
        
        if self.consensus_points:
            parts.append("✅ **Council agrees on:**")
            parts.extend([f"- {p}" for p in self.consensus_points])
        
        if self.divergence_points:
            parts.append("\n⚠️ **Perspectives differ on:**")
            for dp in self.divergence_points:
                parts.append(f"- {dp.issue}")
        
        if self.risks_identified:
            parts.append("\n🔔 **Identified risks:**")
            for r in self.risks_identified:
                parts.append(f"- {r.risk} ({r.severity})")
        
        if self.recommended_actions:
            parts.append("\n📋 **Recommended actions:**")
            for a in self.recommended_actions:
                parts.append(f"- {a}")
        
        return "\n".join(parts)
```

---

*Created: 2026-01-10*
