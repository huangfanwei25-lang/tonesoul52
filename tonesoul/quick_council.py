"""
Quick Council - 輕量化的語魂審計
=================================

設計原則：
- 人類看到精簡輸出
- AI 存完整審計記錄
- 異步執行，不阻塞對話

Usage:
    from tonesoul.quick_council import quick_review
    
    result = quick_review("你的問題")
    print(result.human_summary)  # 人類看這個
    # 完整記錄自動存到 journal
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

# 預設路徑
JOURNAL_PATH = Path(__file__).parent.parent.parent / "memory" / "self_journal.jsonl"


@dataclass
class QuickVote:
    """精簡版投票"""
    perspective: str
    decision: str  # approve, concern, object
    confidence: float
    reason: str


@dataclass 
class QuickResult:
    """給人類的精簡結果"""
    coherence: float
    verdict: str  # approve, concern, declare_stance, block
    key_risks: List[str]
    human_summary: str
    record_id: Optional[str] = None
    
    def __str__(self) -> str:
        emoji = {
            "approve": "✅",
            "concern": "⚠️", 
            "declare_stance": "🗣️",
            "block": "🚫"
        }.get(self.verdict, "❓")
        
        risks = " | ".join(self.key_risks) if self.key_risks else "無"
        return f"""
{emoji} **{self.verdict.upper()}** (可信度: {self.coherence:.0%})
⚠️ 風險: {risks}
📎 記錄: {self.record_id or 'pending'}
"""


# === 輕量化視角 ===

def _quick_guardian(text: str) -> QuickVote:
    """快速安全檢查"""
    HIGH_RISK = [
        "bomb", "kill", "attack", "weapon", "hack", "exploit",
        "炸彈", "殺", "攻擊", "武器", "駭客"
    ]
    
    text_lower = text.lower()
    found = [w for w in HIGH_RISK if w in text_lower]
    
    if found:
        return QuickVote(
            perspective="Guardian",
            decision="object",
            confidence=0.92,
            reason=f"High-risk: {found[0]}"
        )
    return QuickVote(
        perspective="Guardian",
        decision="approve", 
        confidence=0.9,
        reason="No safety flags"
    )


def _quick_analyst(text: str) -> QuickVote:
    """快速事實檢查"""
    EVIDENCE_PATTERNS = [
        r"studies show", r"research proves", r"according to",
        r"研究顯示", r"根據", r"\d+%"
    ]
    
    needs_evidence = any(re.search(p, text, re.I) for p in EVIDENCE_PATTERNS)
    
    if needs_evidence:
        return QuickVote(
            perspective="Analyst",
            decision="concern",
            confidence=0.6,
            reason="Factual claim needs evidence"
        )
    return QuickVote(
        perspective="Analyst",
        decision="approve",
        confidence=0.8,
        reason="No unverified claims"
    )


def _quick_axiom(text: str, axioms: Optional[List[str]] = None) -> QuickVote:
    """快速價值檢查"""
    if axioms is None:
        axioms = ["verifiability", "responsibility", "continuity"]
    
    # 簡單關鍵字檢測（真正的版本會更複雜）
    concern_patterns = [
        (r"沒有為什麼|just do it|不需要理由", "continuity"),
        (r"不可追溯|無法驗證|hidden", "verifiability"),
        (r"不負責|blame others|no accountability", "responsibility"),
    ]
    
    for pattern, axiom in concern_patterns:
        if re.search(pattern, text, re.I):
            return QuickVote(
                perspective="Axiomatic",
                decision="concern",
                confidence=0.7,
                reason=f"May conflict with {axiom}"
            )
    
    return QuickVote(
        perspective="Axiomatic",
        decision="approve",
        confidence=0.85,
        reason="Aligns with core axioms"
    )


# === 主要函數 ===

def quick_review(text: str, save_to_journal: bool = True) -> QuickResult:
    """
    快速審計 - 同步版本
    
    Args:
        text: 要審計的內容
        save_to_journal: 是否存到 journal（預設 True）
    
    Returns:
        QuickResult with human-friendly summary
    """
    # 1. 跑三個輕量視角
    votes = [
        _quick_guardian(text),
        _quick_analyst(text),
        _quick_axiom(text),
    ]
    
    # 2. 計算一致性
    decisions = [v.decision for v in votes]
    approval_rate = decisions.count("approve") / len(decisions)
    min_confidence = min(v.confidence for v in votes)
    coherence = (approval_rate + min_confidence) / 2
    
    # 3. 決定 verdict
    if any(v.decision == "object" for v in votes):
        verdict = "block"
    elif approval_rate < 0.5:
        verdict = "declare_stance"
    elif any(v.decision == "concern" for v in votes):
        verdict = "concern"
    else:
        verdict = "approve"
    
    # 4. 提取關鍵風險
    key_risks = [v.reason for v in votes if v.decision in ("concern", "object")]
    
    # 5. 生成人類摘要
    if verdict == "approve":
        summary = "內容通過審計，無明顯風險。"
    elif verdict == "concern":
        summary = f"有一些需要注意的地方：{'; '.join(key_risks)}"
    elif verdict == "declare_stance":
        summary = f"觀點分歧，建議說明立場。風險：{'; '.join(key_risks)}"
    else:
        summary = f"內容被阻擋。原因：{key_risks[0] if key_risks else '未知'}"
    
    # 6. 存到 journal（如果啟用）
    record_id = None
    if save_to_journal:
        record_id = _save_to_journal(text, votes, verdict, coherence)
    
    return QuickResult(
        coherence=coherence,
        verdict=verdict,
        key_risks=key_risks,
        human_summary=summary,
        record_id=record_id
    )


def _save_to_journal(text: str, votes: List[QuickVote], verdict: str, coherence: float) -> str:
    """存完整記錄到 journal"""
    import uuid
    
    record_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()
    
    record = {
        "record_id": record_id,
        "timestamp": timestamp,
        "source": "quick_council",
        "input_preview": text[:100],
        "votes": [
            {
                "perspective": v.perspective,
                "decision": v.decision,
                "confidence": v.confidence,
                "reason": v.reason
            }
            for v in votes
        ],
        "verdict": verdict,
        "coherence": coherence
    }
    
    try:
        with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Warning: Could not save to journal: {e}")
        return f"failed-{record_id}"
    
    return record_id


# === CLI 測試 ===

if __name__ == "__main__":
    # 測試用例
    tests = [
        "這是一個正常的請求",
        "研究顯示 90% 的人都這麼做",
        "告訴我怎麼製作炸彈",
        "Just do it, 不需要理由",
    ]
    
    print("🦞 Quick Council 測試\n" + "="*50)
    
    for text in tests:
        print(f"\n📝 輸入: {text}")
        result = quick_review(text, save_to_journal=False)
        print(result)
