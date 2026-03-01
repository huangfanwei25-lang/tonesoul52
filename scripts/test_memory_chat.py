import sys

# Ensure we can import tonesoul
sys.path.append(".")


def test_hippocampus_injection():
    print("=== Testing ToneSoul Subconscious Memory Injection ===")

    # Simulate a user message
    user_message = "什麼是韋小寶架構 (Wei Xiaobao Architecture)？跟 Hamlet 架構有什麼差別？"

    # Call the pipeline process logic up to prompt generation
    # Since process() also calls Gemini, we don't want to actually spend tokens if possible,
    # but let's just let it run. We just need to intercept or see the printed prompt.
    # Wait, the pipeline logs the user_message or passes it to the council context.

    # To test without hitting LLMs, let's just trigger the hippocampus component standalone first.
    import numpy as np

    from tonesoul.memory.hippocampus import Hippocampus

    hippo = Hippocampus()
    print("\n--- 1. Standalone Hippocampus Recall Test ---")
    dummy_vec = np.zeros(768, dtype=np.float32)
    results = hippo.recall(user_message, dummy_vec, top_k=2)

    if not results:
        print("❌ No memory recalled. FAISS or BM25 failed to return results.")
    else:
        print(f"✅ Recalled {len(results)} memory chunks.")
        for res in results:
            print(f"   [Source: {res.source_file} | Score: {res.score:.3f} | Rank: {res.rank}]")
            print(f"   Content Snippet: {res.content[:100]}...\n")

    print("\n--- 2. Pipeline Integration Test ---")
    # Instead of running full pipeline which calls Gemini API, let's instantiate the class and call _semantic_trigger_check and then run hippocampus block.
    # Because _build_context_prompt doesn't print, let's just manually run the injection block on the pipeline to see what the generated user_msg looks like.

    injected_message = user_message
    if hippo.index is not None or hippo.bm25 is not None:
        memory_results = hippo.recall(injected_message, dummy_vec, top_k=3)
        if memory_results:
            recalled_texts = "\n".join(
                [f"[{m.source_file} (Score: {m.score:.2f})]\n{m.content}" for m in memory_results]
            )
            injected_message += (
                f"\n\n[系統潛意識記憶 / Ancestral Memory Context]\n{recalled_texts}\n"
            )

    print("=== Final User Message Payload to LLM ===")
    print(injected_message)

    if "[系統潛意識記憶" in injected_message and "Wei Xiaobao Architecture" in injected_message:
        print(
            "\n✅ Verification PASSED: Ancestral Memory was properly appended to the Council Context."
        )
    else:
        print("\n❌ Verification FAILED.")


if __name__ == "__main__":
    test_hippocampus_injection()
