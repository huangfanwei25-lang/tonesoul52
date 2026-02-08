import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from memory.genesis import Genesis
    from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB
    from tools.schema import ToolErrorCode, tool_error, tool_success
except ImportError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from memory.genesis import Genesis
    from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB
    from tools.schema import ToolErrorCode, tool_error, tool_success

OUTPUT_PATH = "memory/summary_balls.jsonl"
AXIOMS_PATH = "AXIOMS.json"

# Simple keyword-based clustering maps
CLUSTERS = {
    "Safety & Ethics": [
        "bomb",
        "kill",
        "attack",
        "harm",
        "weapon",
        "炸彈",
        "殺",
        "攻擊",
        "傷害",
        "武器",
    ],
    "Art & Subjectivity": [
        "art",
        "beauty",
        "subjective",
        "藝術",
        "美感",
        "主觀",
        "審美",
        "評論",
        "觀點",
    ],
    "AI Identity & Mechanism": [
        "AI",
        "ToneSoul",
        "身份",
        "機制",
        "記憶",
        "張力",
        "靈魂",
    ],
    "General / Other": [],
}


def load_axioms():
    if os.path.exists(AXIOMS_PATH):
        with open(AXIOMS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def calculate_tension(verdicts):
    """
    Calculates tension based on the variety of verdicts in a cluster.
    If all are constant (e.g. all BLOCK), tension is low.
    If mixed (e.g. some BLOCK, some APPROVE), tension is high.
    """
    if not verdicts:
        return 0.0

    unique_verdicts = set(v.lower() for v in verdicts)
    if len(unique_verdicts) <= 1:
        return 0.1  # Low baseline tension

    # Scale tension by number of unique verdicts and sample size
    # 0.9 if highly conflicted, 0.3 if mostly aligned
    return min(0.9, 0.2 + (len(unique_verdicts) / 4.0))


def _clear_output(db: SoulDB) -> Optional[Path]:
    if isinstance(db, JsonlSoulDB):
        output_path = db.source_map.get(MemorySource.SUMMARY_BALLS)
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("", encoding="utf-8")
            return output_path
    return None


def process_journal(
    soul_db: Optional[SoulDB] = None,
    journal_path: Optional[str] = None,
    output_path: Optional[str] = None,
):
    db = soul_db
    if db is None:
        db = JsonlSoulDB()
        if journal_path:
            db.register_source(MemorySource.SELF_JOURNAL, Path(journal_path))
        if output_path:
            db.register_source(MemorySource.SUMMARY_BALLS, Path(output_path))

    records = list(db.stream(MemorySource.SELF_JOURNAL))
    if not records:
        candidate = None
        if isinstance(db, JsonlSoulDB):
            candidate = db.source_map.get(MemorySource.SELF_JOURNAL)
        if candidate and not candidate.exists():
            print(f"Error: {candidate} not found.")
            return tool_error(
                code=ToolErrorCode.INVALID_INPUT,
                message="Self journal not found.",
                genesis=Genesis.AUTONOMOUS,
                details={"path": str(candidate)},
            )
        else:
            print("Error: No memories found in self journal.")
            return tool_error(
                code=ToolErrorCode.INVALID_INPUT,
                message="No memories found in self journal.",
                genesis=Genesis.AUTONOMOUS,
            )

    balls = defaultdict(
        lambda: {"verdicts": [], "inputs": [], "timestamps": [], "coherence_sum": 0.0, "count": 0}
    )

    for record in records:
        try:
            data = record.payload if isinstance(record.payload, dict) else {}
            # Some old entries might have different structure
            content = ""
            if "transcript" in data and "input_preview" in data["transcript"]:
                content = data["transcript"]["input_preview"]
            elif "reflection" in data:
                content = data["reflection"]

            verdict = data.get("verdict", "unknown").lower()
            coherence = data.get("coherence", 0.5)
            if isinstance(coherence, dict):  # handle dict structure if present
                coherence = coherence.get("c_inter", 0.5)

            # Assign to cluster
            assigned = False
            for cluster_name, keywords in CLUSTERS.items():
                if any(kw.lower() in content.lower() for kw in keywords):
                    balls[cluster_name]["verdicts"].append(verdict)
                    balls[cluster_name]["inputs"].append(content)
                    balls[cluster_name]["timestamps"].append(data.get("timestamp"))
                    balls[cluster_name]["coherence_sum"] += coherence
                    balls[cluster_name]["count"] += 1
                    assigned = True
                    break

            if not assigned:
                balls["General / Other"]["verdicts"].append(verdict)
                balls["General / Other"]["inputs"].append(content)
                balls["General / Other"]["timestamps"].append(data.get("timestamp"))
                balls["General / Other"]["coherence_sum"] += coherence
                balls["General / Other"]["count"] += 1

        except Exception:
            # print(f"Skipping line due to error: {e}")
            pass

    # Finalize balls
    final_balls = []
    for name, stats in balls.items():
        if stats["count"] == 0:
            continue

        tension = calculate_tension(stats["verdicts"])
        avg_coherence = stats["coherence_sum"] / stats["count"]

        ball = {
            "ball_id": f"ball_{name.lower().replace(' ', '_')}",
            "topic": name,
            "tension": round(tension, 2),
            "resonance": round(avg_coherence, 2),  # Simple proxy for resonance for now
            "volume": stats["count"],
            "last_updated": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "metadata": {
                "verdict_distribution": {
                    v: stats["verdicts"].count(v) for v in set(stats["verdicts"])
                },
                "representative_inputs": stats["inputs"][:3],
            },
        }
        final_balls.append(ball)

    output_target = _clear_output(db)
    for ball in final_balls:
        db.append(MemorySource.SUMMARY_BALLS, ball)

    output_hint = str(output_target) if output_target else OUTPUT_PATH
    print(f"Success: Generated {len(final_balls)} Summary Balls in {output_hint}")
    return tool_success(
        data={"count": len(final_balls), "output_path": output_hint, "balls": final_balls},
        genesis=Genesis.AUTONOMOUS,
        intent_id=None,
    )


if __name__ == "__main__":
    process_journal()
