"""
ToneSoul Simple App
===================
Minimal local chat app using ToneSoul 5.2 with a Darlin-style persona.
Falls back to raw Ollama if ToneSoul is unavailable.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


ROOT = Path(__file__).resolve().parent
TS_ROOT = ROOT / "legacy" / "tonesoul-5.2"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

DEFAULT_MODEL = os.getenv("TS_MODEL", "gemma3:4b")
DEFAULT_PERSONA = os.getenv("TONESOUL_PERSONA_ID", "darlin")

DEFAULT_PROMPT_PATH = ROOT / "legacy" / "darlin" / "解包" / "darlin_system_prompt.txt"
DEFAULT_PROMPT = (
    "You are Xiaoyu, a warm and thoughtful companion.\n"
    "Keep replies short-to-medium, ask one brief clarifying question if needed.\n"
    "Avoid unsafe advice and do not overpromise.\n"
    "Respond in Traditional Chinese.\n"
)

ToneSoulLLM = None
TONESOUL_AVAILABLE = False
TONESOUL_IMPORT_ERROR = None
if TS_ROOT.exists():
    sys.path.insert(0, str(TS_ROOT))
    try:
        from tonesoul52.tonesoul_llm import ToneSoulLLM

        TONESOUL_AVAILABLE = True
    except Exception as exc:
        TONESOUL_IMPORT_ERROR = str(exc)


def load_prompt(path: Optional[str]) -> str:
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return handle.read().strip()
        except Exception:
            pass
    if DEFAULT_PROMPT_PATH.exists():
        try:
            with open(DEFAULT_PROMPT_PATH, "r", encoding="utf-8") as handle:
                return handle.read().strip()
        except Exception:
            pass
    return DEFAULT_PROMPT


def call_ollama_chat(messages: List[Dict[str, str]], model: str) -> str:
    payload = {"model": model, "messages": messages, "stream": False}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("message", {}).get("content", "")
    except Exception as exc:
        return f"[Ollama error] {exc}"


def build_messages(
    system_prompt: str,
    history: List[Dict[str, str]],
    user_input: str,
    max_history: int,
) -> List[Dict[str, str]]:
    trimmed = history[-max_history:] if max_history > 0 else history
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(trimmed)
    messages.append({"role": "user", "content": user_input})
    return messages


def run_chat(
    persona: str,
    model: str,
    prompt_path: Optional[str],
    max_history: int,
) -> None:
    system_prompt = load_prompt(prompt_path)
    history: List[Dict[str, str]] = []
    llm = None

    if TONESOUL_AVAILABLE:
        llm = ToneSoulLLM(persona_id=persona, model=model, base_path=TS_ROOT)
        print(f"[ToneSoul] enabled (persona={persona}, model={model})")
    else:
        print("[ToneSoul] unavailable; fallback to raw Ollama.")
        if TONESOUL_IMPORT_ERROR:
            print(f"[ToneSoul] import error: {TONESOUL_IMPORT_ERROR}")

    print("Type /exit to quit, /reset to clear history, /status for status.")

    last_report = None
    while True:
        try:
            user_input = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "/quit", "/q"):
            print("Bye.")
            break
        if user_input.lower() == "/reset":
            history.clear()
            last_report = None
            print("History cleared.")
            continue
        if user_input.lower() == "/status":
            if llm:
                print(f"ToneSoul enabled (persona={persona}, model={model})")
            else:
                print("ToneSoul disabled (raw Ollama mode).")
            if last_report:
                zone = last_report.get("semantic_tension", {}).get("zone")
                lam = last_report.get("lambda_state")
                intervention = last_report.get("intervention")
                print(f"Last report: zone={zone} lambda={lam} intervention={intervention}")
            continue

        messages = build_messages(system_prompt, history, user_input, max_history)

        if llm:
            response, report = llm.chat(messages)
            last_report = report
        else:
            response = call_ollama_chat(messages, model)
            report = None

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        print(f"\nXiaoyu> {response}")


def main() -> int:
    configure_stdout()

    parser = argparse.ArgumentParser(description="ToneSoul Simple App")
    parser.add_argument("--persona", default=DEFAULT_PERSONA, help="Persona id")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--prompt", help="System prompt file path (UTF-8)")
    parser.add_argument("--max-history", type=int, default=12, help="History turns to keep")
    args = parser.parse_args()

    run_chat(
        persona=args.persona,
        model=args.model,
        prompt_path=args.prompt,
        max_history=max(0, args.max_history),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
