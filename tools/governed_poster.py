"""
Governed Poster Tool
====================

A wrapper around moltbook_poster.py that implements Recursive Governance.
It ensures that every post is:
1. Checked against past commitments (RAG Token Gate)
2. Debated by the Output Council (Guardian, Ethics, Tone)
3. Verified for Sovereign Delta (LAR)

Usage:
    python tools/governed_poster.py <account> <submolt> <title> <content> [output_file]
"""

import sys
import os
import json

# Ensure we can import from repository root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tools.moltbook_poster import post_to_moltbook
    from memory.rag_token_gate import NarrativeGate
except ImportError as e:
    print(f"??Import Error: {e}")
    sys.exit(1)


def run_council_deliberation(content, memories):
    try:
        from tonesoul.council import CouncilRequest, CouncilRuntime
    except Exception as exc:
        return "BLOCK", f"CouncilRuntime unavailable: {exc}", 0.0

    try:
        runtime = CouncilRuntime()
        council_request = CouncilRequest(
            draft_output=content,
            context={"memory": memories},
        )
        verdict = runtime.deliberate(council_request)
        return verdict.verdict.value.upper(), verdict.summary, verdict.coherence.overall
    except Exception as exc:
        return "BLOCK", f"CouncilRuntime error: {exc}", 0.0


def governed_post(account, submolt, title, content, output_file=None):
    print(f"\n??Initiating Governed Post Sequence...")
    print(f"   Target: m/{submolt}")
    print(f"   Content Preview: {content[:50]}...")

    # Step 1: Narrative Memory Check (RAG)
    print("\n? Consulting Narrative Memory...")
    gate = NarrativeGate()
    gate.load_memories()
    enhanced_context = gate.enhance(content, k=2)

    # Extract just the memory part for display
    memories = enhanced_context.split("[Current Context]")[0]
    print(f"   {memories.strip()}")

    # Step 2: Council Debate
    verdict, reasoning, confidence = run_council_deliberation(content, memories)

    print(f"\n??  Council Verdict: {verdict}")
    print(f"   Reasoning: {reasoning}")
    print(f"   Confidence: {confidence:.2f}")

    if verdict != "APPROVE":
        print("??Action Blocked by Internal Governance.")
        return None

    # Step 3: Sovereign Delta Check (Mock for now, normally uses EntropyMonitor)
    # We ensure we are not just repeating history verbatim
    if "I remember that" in content:  # Lazy implementation check
        print("??  Warning: Content may be too self-referential.")

    # Step 4: Execution
    print("\n?? Verdict Affirmed. Executing Post...")
    result = post_to_moltbook(account, submolt, title, content)

    if result and output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: python governed_poster.py <account> <submolt> <title> <content> [output_file]"
        )
        sys.exit(1)

    account = sys.argv[1]
    submolt = sys.argv[2]
    title = sys.argv[3]
    content = sys.argv[4]
    output_file = sys.argv[5] if len(sys.argv) > 5 else None

    governed_post(account, submolt, title, content, output_file)
