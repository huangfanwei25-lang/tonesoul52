"""
Governed Poster Tool
====================

Wrapper around moltbook_poster.py with governance checks.
"""

import sys
import os
import json

# Ensure we can import from repository root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tools.moltbook_poster import post_to_moltbook
    from memory.rag_token_gate import NarrativeGate
    from memory.self_memory import record_self_memory
    from memory.genesis import Genesis
    from tools.schema import ToolErrorCode, tool_error
except ImportError as e:
    print(f"Import Error: {e}")
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
    print("\nInitiating Governed Post Sequence...")
    print(f"  Target: m/{submolt}")
    print(f"  Content Preview: {content[:50]}...")

    # Step 1: Narrative Memory Check (RAG)
    print("\nConsulting Narrative Memory...")
    gate = NarrativeGate()
    gate.load_memories()
    enhanced_context = gate.enhance(content, k=2)

    # Extract just the memory part for display
    memories = enhanced_context.split("[Current Context]")[0]
    print(f"  {memories.strip()}")

    # Step 2: Council Debate
    verdict, reasoning, confidence = run_council_deliberation(content, memories)

    print(f"\nCouncil Verdict: {verdict}")
    print(f"  Reasoning: {reasoning}")
    print(f"  Confidence: {confidence:.2f}")

    if verdict != "APPROVE":
        print("Action Blocked by Internal Governance.")
        return tool_error(
            code=ToolErrorCode.GOVERNANCE_BLOCK,
            message="Action blocked by internal governance.",
            genesis=Genesis.REACTIVE_SOCIAL,
            details={
                "verdict": verdict,
                "reasoning": reasoning,
                "confidence": confidence,
            },
        )

    # Step 3: Sovereign Delta Check (placeholder)
    if "I remember that" in content:
        print("Warning: Content may be too self-referential.")

    # Step 4: Execution
    print("\nVerdict affirmed. Executing post...")
    result = post_to_moltbook(account, submolt, title, content)
    if not result or not result.get("success"):
        return result

    # Attach governance metadata to tool response
    data = result.get("data") or {}
    data["governance"] = {
        "verdict": verdict,
        "reasoning": reasoning,
        "confidence": confidence,
    }
    result["data"] = data

    # Step 5: Record to Self-Memory
    post_id = data.get("post_id")
    if post_id:
        intent_id = f"moltbook:{post_id}"
        record_self_memory(
            reflection=f"Posted to m/{submolt} with council verdict {verdict}.",
            context={
                "platform": "moltbook",
                "submolt": submolt,
                "post_id": post_id,
                "title": title,
                "content_preview": content[:100] if len(content) > 100 else content,
            },
            verdict="POST_SUCCESS",
            coherence=confidence,
            key_decision=f"Council verdict: {verdict}",
            genesis=Genesis.REACTIVE_SOCIAL,
            is_mine=False,
            intent_id=intent_id,
        )
        print("Post recorded to self-journal.")

    if output_file:
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
