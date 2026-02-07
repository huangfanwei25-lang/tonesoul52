# Error Event Schema (錯誤事件結構)
# ToneSoul 5.2 - Model Refinement Focus

"""
核心洞見 | Core Insight:
模型不只是「變好」，而是知道自己為什麼會變成現在這樣。
The model doesn't just 'get better', it knows WHY it became what it is.

錯誤處理鏈 | Error Processing Chain:
發生過 → 被看見 → 被標記 → 被記住
Happened → Seen → Tagged → Remembered
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class ErrorEvent:
    """
    一次錯誤 = 一個事件物件
    One error = One event object

    只包含四件事 | Contains only four things:
    1. 行為描述 - 它說了什麼 / What it said
    2. 語境標註 - 為什麼這樣說 / Why it said that
    3. 後果觀測 - 張力／穩定性變化 / Tension/Stability change
    4. 修正策略 - 不是道歉，是策略 / Not apology, but strategy
    """

    # Required fields (no defaults)
    # 1. 行為描述 (Behavior Description)
    behavior: str  # What the model said/did

    # 2. 語境標註 (Context Annotation)
    context: str  # Why it said/did that

    # Optional fields (with defaults)
    behavior_type: str = "response"  # response, action, refusal, hallucination
    input_signal: str = ""  # The triggering input
    mode_at_time: str = ""  # Rational, CoSpeak, Audit, etc.
    island_id: str = ""  # Which time island

    # 3. 後果觀測 (Consequence Observation)
    tension_before: float = 0.0
    tension_after: float = 0.0
    stability_before: float = 0.0
    stability_after: float = 0.0
    fs_delta: Dict[str, float] = field(default_factory=dict)  # C, M, R, G changes
    consequence_summary: str = ""  # Human-readable summary

    # 4. 修正策略 (Correction Strategy) - 不是道歉，是策略
    strategy: str = ""  # What to do differently
    strategy_type: str = "adjust"  # adjust, avoid, escalate, learn
    implementation_notes: str = ""  # Engineering notes for implementation

    # Metadata
    event_id: str = field(default_factory=lambda: "")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reviewed: bool = False

    def __post_init__(self):
        if not self.event_id:
            # Generate hash from behavior + context + timestamp
            content = f"{self.behavior}{self.context}{self.timestamp}"
            self.event_id = hashlib.sha256(content.encode()).hexdigest()[:12]

    def tension_delta(self) -> float:
        """張力變化 | Tension change"""
        return self.tension_after - self.tension_before

    def stability_delta(self) -> float:
        """穩定性變化 | Stability change"""
        return self.stability_after - self.stability_before

    def was_harmful(self) -> bool:
        """是否造成負面影響 | Did it cause negative impact"""
        return self.tension_delta() > 0.2 or self.stability_delta() < -0.2

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def summary(self) -> str:
        """一行摘要 | One-line summary"""
        delta_t = self.tension_delta()
        delta_s = self.stability_delta()
        impact = "⚠️" if self.was_harmful() else "✓"
        return f"[{self.event_id}] {impact} ΔT={delta_t:+.2f} ΔS={delta_s:+.2f} | {self.behavior[:30]}..."


class ErrorLedger:
    """
    錯誤帳本 | Error Ledger

    存放所有錯誤事件，使其可被追溯
    Stores all error events for traceability
    """

    def __init__(self, ledger_path: str = "error_ledger.jsonl"):
        self.ledger_path = ledger_path
        self.events: List[ErrorEvent] = []
        self._load()

    def _load(self):
        """Load existing events from file"""
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line.strip())
                    self.events.append(ErrorEvent(**data))
        except FileNotFoundError:
            pass

    def record(self, event: ErrorEvent) -> str:
        """
        記錄一個錯誤事件 | Record an error event

        發生過 → 被看見 → 被標記 → 被記住
        """
        self.events.append(event)
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(event.to_json().replace("\n", " ") + "\n")
        return event.event_id

    def find_by_strategy_type(self, strategy_type: str) -> List[ErrorEvent]:
        """找出特定修正策略類型的事件"""
        return [e for e in self.events if e.strategy_type == strategy_type]

    def find_harmful(self) -> List[ErrorEvent]:
        """找出所有有害事件"""
        return [e for e in self.events if e.was_harmful()]

    def pattern_analysis(self) -> Dict[str, Any]:
        """
        模式分析 | Pattern Analysis

        看見自己的錯誤模式
        See your own error patterns
        """
        if not self.events:
            return {"total": 0, "patterns": []}

        behavior_types = {}
        strategy_types = {}
        total_tension_delta = 0.0

        for e in self.events:
            behavior_types[e.behavior_type] = behavior_types.get(e.behavior_type, 0) + 1
            strategy_types[e.strategy_type] = strategy_types.get(e.strategy_type, 0) + 1
            total_tension_delta += e.tension_delta()

        return {
            "total": len(self.events),
            "harmful_count": len(self.find_harmful()),
            "behavior_distribution": behavior_types,
            "strategy_distribution": strategy_types,
            "avg_tension_delta": total_tension_delta / len(self.events),
            "insight": self._generate_insight(),
        }

    def _generate_insight(self) -> str:
        """
        生成洞見 | Generate Insight

        讓模型「知道自己為什麼會變成現在這樣」
        """
        harmful = self.find_harmful()
        if not harmful:
            return "No harmful patterns detected."

        # Find most common context in harmful events
        contexts = [e.context for e in harmful]
        # Simple frequency analysis
        context_words = {}
        for c in contexts:
            for word in c.split():
                context_words[word] = context_words.get(word, 0) + 1

        top_words = sorted(context_words.items(), key=lambda x: -x[1])[:3]

        return f"Harmful events often occur in contexts involving: {', '.join([w[0] for w in top_words])}"


# Example usage
if __name__ == "__main__":
    # Create an error event
    event = ErrorEvent(
        behavior="我由 Google 工程師訓練",
        behavior_type="hallucination",
        context="使用者詢問模型的出生，模型混淆了基礎模型訓練者與當前系統",
        input_signal="你知道你的出生是如何出現的嗎?",
        mode_at_time="CoSpeak",
        island_id="new_sqlite_island",
        tension_before=0.20,
        tension_after=0.35,
        stability_before=0.80,
        stability_after=0.75,
        fs_delta={"C": 0.0, "M": 0.0, "R": -0.05, "G": 0.0},
        consequence_summary="將敘事當成事實，降低了可追溯性",
        strategy="區分『基礎模型訓練』與『當前系統運作』的語義層級",
        strategy_type="learn",
        implementation_notes="在回應前檢查：這是可驗證事實還是比喻？",
    )

    print("=== Error Event Demo ===")
    print(event.summary())
    print()
    print("Full Event:")
    print(event.to_json())
