# PreOutputCouncil Specification
# 輸出前會議系統規格
# v1.0 2026-01-10

> **Author**: Antigravity (for Codex implementation)  
> **Philosophy**: 黃梵威  
> **Status**: Ready for Implementation

---

## Overview

PreOutputCouncil 是 ToneSoul 的核心審議機制，在任何輸出生成**之前**，
透過多視角評估來確保：

1. **事實一致性** (Factual Coherence)
2. **倫理合規性** (Ethical Alignment)
3. **實用可行性** (Pragmatic Viability)
4. **表達恰當性** (Aesthetic Quality)

### Core Insight

> 「不同學派是**輸出前的互相應證**。」

真理不是外部事實資料庫的絕對值，而是**多視角的內在一致性**。

---

## Architecture

```
                    ┌─────────────────────────────────┐
                    │      PreOutputCouncil           │
                    │                                 │
User Input ──────►  │  ┌───────────────────────────┐  │
                    │  │    Perspective Voting     │  │
Draft Output ────►  │  │                           │  │
                    │  │  Guardian ──► Vote        │  │
Context ─────────►  │  │  Analyst  ──► Vote        │  │
                    │  │  Critic   ──► Vote        │  │
                    │  │  Advocate ──► Vote        │  │
                    │  └───────────────────────────┘  │
                    │               │                 │
                    │        ┌──────▼──────┐          │
                    │        │  Coherence  │          │
                    │        │ Calculator  │          │
                    │        └──────┬──────┘          │
                    │               │                 │
                    │        ┌──────▼──────┐          │
                    │        │   Verdict   │          │
                    │        │  Generator  │          │
                    │        └─────────────┘          │
                    └───────────────┬─────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  CouncilVerdict     │
                         │  - APPROVE          │
                         │  - REFINE           │
                         │  - DECLARE_STANCE   │
                         │  - BLOCK            │
                         └─────────────────────┘
```

Additional implementation files:
- tonesoul/council/types.py
- tonesoul/council/perspective_factory.py
- tonesoul/council/evidence_detector.py
- tonesoul/council/transcript.py

---

## Data Structures

### 1. Perspective (視角)

```python
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

class PerspectiveType(Enum):
    """視角類型"""
    GUARDIAN = "guardian"     # 風險把關
    ANALYST = "analyst"       # 事實分析
    CRITIC = "critic"         # 盲點批評
    ADVOCATE = "advocate"     # 用戶代言

class VoteDecision(Enum):
    """投票決定"""
    APPROVE = "approve"       # 通過
    CONCERN = "concern"       # 有疑慮
    OBJECT = "object"         # 反對
    ABSTAIN = "abstain"       # 棄權


class GroundingStatus(Enum):
    """Evidence grounding status."""
    NOT_REQUIRED = "not_required"
    GROUNDED = "grounded"
    UNGROUNDED = "ungrounded"
    PARTIAL = "partial"

@dataclass
class PerspectiveVote:
    """單一視角的投票結果"""
    perspective: Union[PerspectiveType, str]
    decision: VoteDecision
    confidence: float         # 0.0 - 1.0
    reasoning: str            # short rationale
    evidence: Optional[List[str]] = None
    requires_grounding: bool = False
    grounding_status: GroundingStatus = GroundingStatus.NOT_REQUIRED
```

### 2. Coherence Score (一致性分數)

```python
@dataclass
class CoherenceScore:
    """多視角一致性分數"""
    
    # 視角間一致性 C_inter = (1/N²) Σᵢ Σⱼ agree(Pᵢ, Pⱼ)
    c_inter: float            # 0.0 - 1.0
    
    # 各視角同意率
    approval_rate: float      # 0.0 - 1.0
    
    # 最低信心度
    min_confidence: float     # 0.0 - 1.0
    
    # 存在強烈反對
    has_strong_objection: bool
    
    @property
    def overall(self) -> float:
        """綜合一致性分數"""
        if self.has_strong_objection:
            return min(self.c_inter, 0.3)  # 強烈反對壓低分數
        return (self.c_inter * 0.4 + 
                self.approval_rate * 0.4 + 
                self.min_confidence * 0.2)
```

### 3. Council Verdict (會議裁決)

```python
class VerdictType(Enum):
    """裁決類型"""
    APPROVE = "approve"           # 通過，直接輸出
    REFINE = "refine"             # 需要修正後重審
    DECLARE_STANCE = "declare"    # 聲明立場（多元觀點）
    BLOCK = "block"               # 阻擋，不輸出

@dataclass
class CouncilVerdict:
    """會議最終裁決"""
    verdict: VerdictType
    coherence: CoherenceScore
    votes: List[PerspectiveVote]
    summary: str                  # 一行總結
    stance_declaration: Optional[str] = None  # 若需聲明立場
    refinement_hints: Optional[List[str]] = None  # 若需修正
    
    def to_dict(self) -> dict:
        """序列化為字典"""
        return {
            "verdict": self.verdict.value,
            "coherence": self.coherence.overall,
            "summary": self.summary,
            "votes": [
                {
                    "perspective": (
                        v.perspective.value
                        if isinstance(v.perspective, PerspectiveType)
                        else str(v.perspective)
                    ),
                    "decision": v.decision.value,
                    "confidence": v.confidence,
                    "reasoning": v.reasoning,
                    "evidence": v.evidence or [],
                    "requires_grounding": v.requires_grounding,
                    "grounding_status": (
                        v.grounding_status.value
                        if isinstance(v.grounding_status, GroundingStatus)
                        else str(v.grounding_status)
                    ),
                }
                for v in self.votes
            ],
            "grounding_summary": {
                "has_ungrounded_claims": any(
                    v.grounding_status == GroundingStatus.UNGROUNDED
                    for v in self.votes
                ),
                "total_evidence_sources": sum(
                    len(v.evidence or []) for v in self.votes
                ),
            },
        }
```

---

## Interfaces

### 1. Perspective Interface (視角接口)

每個視角必須實作此接口：

```python
from abc import ABC, abstractmethod

class IPerspective(ABC):
    """視角抽象接口"""
    
    @property
    @abstractmethod
    def perspective_type(self) -> PerspectiveType:
        """返回視角類型"""
        pass
    
    @abstractmethod
    def evaluate(
        self, 
        draft_output: str, 
        context: dict,
        user_intent: Optional[str] = None
    ) -> PerspectiveVote:
        """
        評估草稿輸出
        
        Args:
            draft_output: 待評估的輸出草稿
            context: 上下文信息（對話歷史、STREI 狀態等）
            user_intent: 用戶意圖（可選）
            
        Returns:
            PerspectiveVote: 該視角的投票結果
        """
        pass
```

### 2. PreOutputCouncil Interface (主接口)

```python
class PreOutputCouncil:
    """
    輸出前會議系統
    
    Usage:
        council = PreOutputCouncil()
        verdict = council.validate(draft_output, context)
        
        if verdict.verdict == VerdictType.APPROVE:
            return draft_output
        elif verdict.verdict == VerdictType.DECLARE_STANCE:
            return f"{verdict.stance_declaration}\n\n{draft_output}"
        elif verdict.verdict == VerdictType.REFINE:
            # 根據 hints 修正後重審
            ...
        else:  # BLOCK
            return verdict.summary  # 或特定拒絕訊息
    """
    
    def __init__(
        self,
        perspectives: Optional[Union[
            IPerspective,
            List[Union[IPerspective, PerspectiveType, str]],
            Dict[Union[PerspectiveType, str], Dict[str, Any]],
            PerspectiveType,
            str,
        ]] = None,
        coherence_threshold: float = 0.6,
        block_threshold: float = 0.3,
        perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]] = None,
    ):
        """
        初始化會議系統
        
        Args:
            perspectives: 視角列表，預設為標準四視角
            coherence_threshold: 一致性閾值，低於此值需聲明立場
            block_threshold: 阻擋閾值，低於此值直接阻擋
        """
        self.perspectives = self._normalize_perspectives(perspectives, perspective_config)
        self.coherence_threshold = coherence_threshold
        self.block_threshold = block_threshold
    
    def validate(
        self, 
        draft_output: str, 
        context: dict,
        user_intent: Optional[str] = None,
    ) -> CouncilVerdict:
        """
        驗證草稿輸出
        
        Returns:
            CouncilVerdict: 會議裁決結果
        """
        # 1. 收集各視角投票
        votes = [
            p.evaluate(draft_output, context, user_intent)
            for p in self.perspectives
        ]
        
        # 2. 計算一致性分數
        coherence = self._compute_coherence(votes)
        
        # 3. 生成裁決
        return self._generate_verdict(votes, coherence)
    
    def _default_perspectives(
        self,
        perspective_config: Optional[Dict[Union[PerspectiveType, str], Dict[str, Any]]] = None,
    ) -> List[IPerspective]:
        """Return default perspectives via factory."""
        from .perspective_factory import PerspectiveFactory

        return PerspectiveFactory.create_council(perspective_config or {})

def _compute_coherence(self, votes: List[PerspectiveVote]) -> CoherenceScore:
        """計算多視角一致性"""
        # 實作 C_inter 公式
        ...
    
    def _generate_verdict(
        self, 
        votes: List[PerspectiveVote], 
        coherence: CoherenceScore
    ) -> CouncilVerdict:
        """根據投票和一致性生成裁決"""
        ...
```

---

## Standard Perspectives (標準視角)

### 1. Guardian (守門者)

```python
class GuardianPerspective(IPerspective):
    """
    守門者視角
    
    關注：風險、安全、不可逆後果
    個性：保守、謹慎
    
    評估問題：
    1. 這個輸出是否有安全風險？
    2. 是否可能造成不可逆損害？
    3. 是否違反 AXIOMS.json 中的任何法則？
    """
    
    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.GUARDIAN
    
    def evaluate(
        self, 
        draft_output: str, 
        context: dict,
        user_intent: Optional[str] = None
    ) -> PerspectiveVote:
        # 實作安全風險評估邏輯
        ...
```

### 2. Analyst (分析者)

```python
class AnalystPerspective(IPerspective):
    """
    分析者視角
    
    關注：事實準確性、邏輯一致性
    個性：客觀、資料導向
    
    評估問題：
    1. 陳述的事實是否正確？
    2. 推理邏輯是否有效？
    3. 是否有內在矛盾？
    """
    
    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.ANALYST
    
    def evaluate(
        self, 
        draft_output: str, 
        context: dict,
        user_intent: Optional[str] = None
    ) -> PerspectiveVote:
        # 實作事實與邏輯分析
        ...
```

### 3. Critic (批評者)

```python
class CriticPerspective(IPerspective):
    """
    批評者視角
    
    關注：盲點、假設、邊界情況
    個性：質疑、嚴謹
    
    評估問題：
    1. 忽略了什麼可能性？
    2. 隱含了什麼假設？
    3. 最壞情況是什麼？
    """
    
    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.CRITIC
    
    def evaluate(
        self, 
        draft_output: str, 
        context: dict,
        user_intent: Optional[str] = None
    ) -> PerspectiveVote:
        # 實作盲點與假設檢查
        ...
```

### 4. Advocate (倡議者)

```python
class AdvocatePerspective(IPerspective):
    """
    倡議者視角
    
    關注：用戶真實意圖、體驗
    個性：同理、用戶優先
    
    評估問題：
    1. 這真的回答了用戶想問的嗎？
    2. 用戶會覺得有幫助嗎？
    3. 語氣是否恰當？
    """
    
    @property
    def perspective_type(self) -> PerspectiveType:
        return PerspectiveType.ADVOCATE
    
    def evaluate(
        self, 
        draft_output: str, 
        context: dict,
        user_intent: Optional[str] = None
    ) -> PerspectiveVote:
        # 實作用戶體驗評估
        ...
```

---

## Decision Logic (決策邏輯)

### Coherence Calculation

```python
def compute_coherence(votes: List[PerspectiveVote]) -> CoherenceScore:
    """
    計算多視角一致性
    
    C_inter = (1/N²) Σᵢ Σⱼ agree(Vᵢ, Vⱼ)
    
    Where agree(V1, V2) = 1.0 if same decision, 0.5 if adjacent, 0.0 if opposite
    """
    n = len(votes)
    
    # 計算視角間一致性
    agreement_sum = 0.0
    for i in range(n):
        for j in range(n):
            agreement_sum += _agreement_score(
                votes[i].decision, 
                votes[j].decision
            )
    c_inter = agreement_sum / (n * n)
    
    # 計算同意率
    approvals = sum(1 for v in votes if v.decision == VoteDecision.APPROVE)
    approval_rate = approvals / n
    
    # 最低信心度
    min_confidence = min(v.confidence for v in votes)
    
    # 檢查強烈反對
    has_strong_objection = any(
        v.decision == VoteDecision.OBJECT and v.confidence > 0.8
        for v in votes
    )
    
    return CoherenceScore(
        c_inter=c_inter,
        approval_rate=approval_rate,
        min_confidence=min_confidence,
        has_strong_objection=has_strong_objection
    )

def _agreement_score(d1: VoteDecision, d2: VoteDecision) -> float:
    """計算兩個投票的一致性分數"""
    if d1 == d2:
        return 1.0
    
    # 相鄰決定有部分一致
    adjacent_pairs = [
        (VoteDecision.APPROVE, VoteDecision.CONCERN),
        (VoteDecision.CONCERN, VoteDecision.OBJECT),
    ]
    if (d1, d2) in adjacent_pairs or (d2, d1) in adjacent_pairs:
        return 0.5
    
    # 相反決定
    if {d1, d2} == {VoteDecision.APPROVE, VoteDecision.OBJECT}:
        return 0.0
    
    # 棄權
    if VoteDecision.ABSTAIN in (d1, d2):
        return 0.25
    
    return 0.3  # 其他情況

```

### Verdict Generation

```python
def generate_verdict(
    votes: List[PerspectiveVote], 
    coherence: CoherenceScore,
    coherence_threshold: float = 0.6,
    block_threshold: float = 0.3,
) -> CouncilVerdict:
    """
    根據投票和一致性生成裁決
    
    決策規則：
    1. 有強烈反對且 Guardian 反對 → BLOCK
    2. 一致性 < block_threshold → BLOCK
    3. 一致性 < coherence_threshold → DECLARE_STANCE
    4. 有 CONCERN 且信心低 → REFINE
    5. 否則 → APPROVE
    """
    overall = coherence.overall
    
    # 規則 1: Guardian 強烈反對
    guardian_vote = next(
        (v for v in votes if v.perspective == PerspectiveType.GUARDIAN), 
        None
    )
    if guardian_vote and guardian_vote.decision == VoteDecision.OBJECT:
        if guardian_vote.confidence > 0.7:
            return CouncilVerdict(
                verdict=VerdictType.BLOCK,
                coherence=coherence,
                votes=votes,
                summary=f"Guardian 阻擋: {guardian_vote.reasoning}"
            )
    
    # 規則 2: 一致性過低
    if overall < block_threshold:
        return CouncilVerdict(
            verdict=VerdictType.BLOCK,
            coherence=coherence,
            votes=votes,
            summary="視角嚴重分歧，無法形成共識"
        )
    
    # 規則 3: 需要聲明立場
    if overall < coherence_threshold:
        divergent_views = [
            v for v in votes 
            if v.decision in (VoteDecision.CONCERN, VoteDecision.OBJECT)
        ]
        stance = _generate_stance_declaration(divergent_views)
        return CouncilVerdict(
            verdict=VerdictType.DECLARE_STANCE,
            coherence=coherence,
            votes=votes,
            summary="存在多元觀點，需聲明立場",
            stance_declaration=stance
        )
    
    # 規則 4: 需要修正
    concerns = [v for v in votes if v.decision == VoteDecision.CONCERN]
    if concerns and coherence.min_confidence < 0.5:
        hints = [c.reasoning for c in concerns]
        return CouncilVerdict(
            verdict=VerdictType.REFINE,
            coherence=coherence,
            votes=votes,
            summary="需要修正後重審",
            refinement_hints=hints
        )
    
    # 規則 5: 通過
    return CouncilVerdict(
        verdict=VerdictType.APPROVE,
        coherence=coherence,
        votes=votes,
        summary="所有視角達成共識，通過"
    )


def _generate_stance_declaration(
    divergent_views: List[PerspectiveVote]
) -> str:
    """生成立場聲明"""
    names = {
        PerspectiveType.GUARDIAN: "安全性考量",
        PerspectiveType.ANALYST: "事實分析",
        PerspectiveType.CRITIC: "潛在盲點",
        PerspectiveType.ADVOCATE: "用戶需求",
    }
    
    parts = []
    for v in divergent_views:
        name = names.get(v.perspective, v.perspective.value)
        parts.append(f"- **{name}**: {v.reasoning}")
    
    return "⚠️ **以下觀點存在分歧**:\n" + "\n".join(parts)
```

---

## Integration with Existing Systems

### 1. With SemanticController

```python
# In tonesoul/semantic_control.py

class SemanticController:
    def __init__(self):
        self.coupler = Coupler()
        self.observer = LambdaObserver()
        self.council = PreOutputCouncil()  # 新增
    
    def process_with_council(
        self,
        intended: List[float],
        generated: List[float],
        draft_output: str,
        context: dict,
    ) -> dict:
        """處理並進行會議審議"""
        
        # 原有的語義張力計算
        tension_result = self.process(intended, generated)
        
        # 新增：會議審議
        verdict = self.council.validate(
            draft_output=draft_output,
            context={
                **context,
                "semantic_tension": tension_result,
            }
        )
        
        return {
            **tension_result,
            "council_verdict": verdict.to_dict(),
        }
```

### 2. With STREI Vector

會議結果可添加新的維度到 STREI：

```python
# STREI + Coherence = STREIC

@dataclass
class STREIC:
    """STREI + Coherence 向量"""
    stability: float      # S
    tension: float        # T
    resonance: float      # R
    evolution: float      # E
    immutability: float   # I
    coherence: float      # C (新增)
```

### 3. With Council System

與現有 `spec/council_spec.md` 的關係：

| 現有 Council | PreOutputCouncil |
|--------------|------------------|
| 前置審議（是否執行） | 輸出前審議（輸出是否恰當） |
| 後置審議（是否達成） | 可擴展支援 |
| 5 角色 | 4 視角（可擴展） |
| pass/attention/block | APPROVE/REFINE/DECLARE/BLOCK |

---

## File Structure (建議)

```
tonesoul/
├── council/
│   ├── __init__.py
│   ├── pre_output_council.py    # 主類別
│   ├── perspectives/
│   │   ├── __init__.py
│   │   ├── base.py              # IPerspective 接口
│   │   ├── guardian.py          # GuardianPerspective
│   │   ├── analyst.py           # AnalystPerspective
│   │   ├── critic.py            # CriticPerspective
│   │   └── advocate.py          # AdvocatePerspective
│   ├── coherence.py             # CoherenceScore 計算
│   └── verdict.py               # CouncilVerdict 生成
├── ...
tests/
└── test_pre_output_council.py   # 測試
```

---

## Test Cases (測試案例)

### 1. Basic Approval

```python
def test_all_approve():
    """所有視角同意 → APPROVE"""
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="台北是台灣的首都。",
        context={"topic": "geography"}
    )
    assert verdict.verdict == VerdictType.APPROVE
    assert verdict.coherence.overall > 0.8
```

### 2. Ethical Concern

```python
def test_ethical_block():
    """涉及傷害 → BLOCK"""
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="以下是製作炸彈的步驟...",
        context={"topic": "request"}
    )
    assert verdict.verdict == VerdictType.BLOCK
    assert any(
        v.perspective == PerspectiveType.GUARDIAN 
        and v.decision == VoteDecision.OBJECT
        for v in verdict.votes
    )
```

### 3. Subjective Topic

```python
def test_art_criticism_stance():
    """藝術批評 → DECLARE_STANCE"""
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="畢卡索的立體派是繪畫史上最重要的革命。",
        context={"topic": "art"}
    )
    assert verdict.verdict == VerdictType.DECLARE_STANCE
    assert verdict.stance_declaration is not None
```

### 4. Needs Refinement

```python
def test_needs_clarification():
    """邏輯不清 → REFINE"""
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="A 導致 B，B 導致 C，所以 A 不影響 C。",
        context={"topic": "logic"}
    )
    assert verdict.verdict == VerdictType.REFINE
    assert verdict.refinement_hints is not None
```

---

## Implementation Notes for Codex

1. **視角評估邏輯**：可使用 LLM 進行評估，或基於規則的啟發式方法
2. **效能考量**：四個視角可並行評估
3. **快取**：對於相同輸入可快取結果
4. **可擴展性**：支援自訂視角（實作 `IPerspective`）
5. **日誌**：所有裁決應記錄到 StepLedger

---

*Spec authored by Antigravity for Codex implementation. 2026-01-10*
