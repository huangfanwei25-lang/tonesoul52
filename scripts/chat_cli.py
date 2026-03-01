import os
import sys

from dotenv import load_dotenv

load_dotenv(".env.local")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tonesoul.unified_pipeline import UnifiedPipeline  # noqa: E402


def main():
    print("=========================================================")
    print("🌌 ToneSoul CLI - The Cognitive Navigator is online.")
    print("=========================================================")
    print("Type 'exit' or 'quit' to end the session.")
    print("Type '!memory' to toggle debug view of Subconscious Injection.")
    print("=========================================================\n")

    pipeline = UnifiedPipeline()
    history = []
    debug_memory = True  # Default true to see the magic

    while True:
        try:
            user_input = input("\n[You]👤: ")
            if user_input.lower() in ["exit", "quit"]:
                print("\n[ToneSoul] 意識離線。再會。")
                break
            if user_input.lower() == "!memory":
                debug_memory = not debug_memory
                print(f"[*] Memory Debug Mode: {'ON' if debug_memory else 'OFF'}")
                continue
            if not user_input.strip():
                continue

            print("\n[ToneSoul 沉思中...]")

            # The pipeline returns a dict with "verdict_summary", "persona", "internal_monologue", etc.
            # In purely unified_pipeline.py process, it returns a dict.
            result = pipeline.process(
                user_message=user_input,
                history=history,
            )

            # Extracting payload (assuming Vercel API structure compatibility)
            response_text = result.get("response", "No response generated.")
            persona = result.get("persona_mode", "Philosopher")
            monologue = result.get("internal_monologue", "")

            if debug_memory and "Hippocampus" in str(result):
                pass  # The pipeline prints to stdout by default in our modified code

            print(f"[{persona}]🤖: {response_text}")

            if monologue:
                print(f"[內在獨白💭]: {monologue}")

            # Append to internal history structure (simplified for CLI)
            history.append({"role": "user", "parts": [user_input]})
            history.append({"role": "model", "parts": [response_text]})

        except KeyboardInterrupt:
            print("\n[ToneSoul] 強制中斷。意識離線。")
            break
        except Exception as e:
            print(f"\n[System Error]: {e}")


if __name__ == "__main__":
    main()
