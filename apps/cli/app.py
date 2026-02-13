# ruff: noqa: E402
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Ensure we can import the local yuhun package.
REPO_ROOT = Path(__file__).resolve().parents[2]
for candidate in (
    REPO_ROOT,
    REPO_ROOT / "src",
    REPO_ROOT / "legacy" / "archives" / "ToneSoul-Repo",
):
    path = str(candidate)
    if path not in sys.path and candidate.exists():
        sys.path.insert(0, path)

from yuhun.gate import build_plan
from yuhun.meta_parser import extract_meta
from yuhun.models import ChronicleEntry, FSVector
from yuhun.ollama_client import generate
from yuhun.prompt_builder import build_prompt
from yuhun.state_store import (
    append_chronicle,
    load_island,
    load_state,
    save_island,
    save_state,
)

MAX_INPUT_LEN = 2000
MAX_SUMMARY_LEN = 200


def main() -> None:
    print("YuHun Orchestrator v0.1 (Ollama)")
    state = load_state()
    island = load_island(state.active_island)
    if island is None:
        print(f"Warning: active island {state.active_island} not found. Creating new one.")
        from yuhun.models import TimeIsland

        island_id = str(uuid.uuid4())[:8]
        island = TimeIsland(
            island_id=island_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            title="Recovered Island",
        )
        state.active_island = island_id
        save_island(island)
        save_state(state)

    while True:
        try:
            user_input = input("\nYou> ").strip()[:MAX_INPUT_LEN]
        except EOFError:
            break

        if user_input.lower() in ("exit", "quit", "bye"):
            print("Goodbye.")
            break

        if not user_input:
            continue

        plan = build_plan(state, user_input)
        prompt = build_prompt(state, island, plan, user_input)

        print(f"Thinking... (mode={plan['mode']}, model={plan['model']})")
        try:
            raw_response = generate(plan["model"], prompt)
        except Exception as exc:
            print(f"LLM call failed: {exc}")
            raw_response = f"Sorry, the model call failed ({type(exc).__name__})."

        clean_response, meta = extract_meta(raw_response)

        fs_before = FSVector(**state.fs.__dict__)
        state.fs.C += meta.fs_delta.get("C", 0)
        state.fs.M += meta.fs_delta.get("M", 0)
        state.fs.R += meta.fs_delta.get("R", 0)
        state.fs.Gamma += meta.fs_delta.get("Gamma", 0)

        for key in ("C", "M", "R", "Gamma"):
            value = getattr(state.fs, key)
            setattr(state.fs, key, max(0.0, min(1.0, value)))

        island.semantic_tension = plan["delta_s"]
        island.current_mode = meta.mode_used
        island.last_step_id = step_id = str(uuid.uuid4())[:8]

        entry = ChronicleEntry(
            step_id=step_id,
            island_id=island.island_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_input=user_input[:MAX_INPUT_LEN],
            model_reply_summary=clean_response[:MAX_SUMMARY_LEN],
            mode_used=meta.mode_used,
            fs_before=fs_before,
            fs_after=state.fs,
            tools_used=[],
            notes="",
        )
        append_chronicle(entry)

        save_state(state)
        save_island(island)

        print(f"\nYuHun[{meta.mode_used}]> {clean_response}")
        print(
            "(FS: C={:.2f}, M={:.2f}, R={:.2f}, G={:.2f}, dS={:.2f})".format(
                state.fs.C,
                state.fs.M,
                state.fs.R,
                state.fs.Gamma,
                island.semantic_tension,
            )
        )


if __name__ == "__main__":
    main()
