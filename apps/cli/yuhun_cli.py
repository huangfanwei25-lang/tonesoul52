#!/usr/bin/env python3
"""
YuHun CLI v0.1
==============
Unified command-line interface for the ToneSoul/YuHun system.

Features:
- Multi-Path cognitive reasoning (5 pathways)
- RAG-based verification
- Decision Kernel integration
- StepLedger traceability

Usage:
    python yuhun_cli.py                    # Interactive mode
    python yuhun_cli.py "Your question"    # Single query mode
    python yuhun_cli.py --demo             # Run demo scenarios

Author: Antigravity + Huang Fan-Wei
Date: 2025-12-08
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output (Windows consoles may default to cp950)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Setup paths
REPO_ROOT = Path(__file__).resolve().parents[2]
for candidate in (
    REPO_ROOT,
    REPO_ROOT / "src",
    REPO_ROOT / "legacy" / "archives" / "ToneSoul-Repo",
):
    path = str(candidate)
    if path not in sys.path and candidate.exists():
        sys.path.insert(0, path)

# Simple banner (ASCII-safe)
BANNER = """
============================================================
 YuHun CLI v0.1  |  World Model × Mind Model
============================================================
"""


class YuHunCLI:
    """Main CLI class integrating all YuHun components."""

    def __init__(self, model: str = "gemma3:4b", verbose: bool = True):
        self.model = model
        self.verbose = verbose
        self.components = {}

        self._load_components()

    def _log(self, msg: str):
        if self.verbose:
            print(f"[YuHun] {msg}")

    def _load_components(self):
        """Load all available components."""

        # Multi-Path Engine
        try:
            from body.multipath_engine import MultiPathEngine

            self.components["multipath"] = MultiPathEngine(model=self.model)
            self._log("[INFO] Multi-Path Engine loaded")
        except Exception as e:
            self._log(f"[WARN] Multi-Path Engine: {e}")

        # Verification Bridge
        try:
            from body.verification_bridge import VerificationBridge

            self.components["verification"] = VerificationBridge()
            self._log("[INFO] Verification Bridge loaded")
        except Exception as e:
            self._log(f"[WARN] Verification Bridge: {e}")

        # Decision Kernel
        try:
            from core.decision_kernel import create_decision_kernel

            self.components["decision"] = create_decision_kernel()
            self._log("[INFO] Decision Kernel loaded")
        except Exception as e:
            self._log(f"[WARN] Decision Kernel: {e}")

        # StepLedger
        try:
            from body.step_ledger import Event, StepLedger

            ledger_path = os.path.join(str(REPO_ROOT), "memory", "yuhun_cli_ledger.jsonl")
            self.components["ledger"] = StepLedger(storage_path=ledger_path)
            self.components["ledger_event_cls"] = Event
            self._log("[INFO] StepLedger loaded")
        except Exception as e:
            self._log(f"[WARN] StepLedger: {e}")

    def process(self, user_input: str) -> dict:
        """Process user input through the full YuHun pipeline."""
        result = {
            "input": user_input,
            "timestamp": datetime.now().isoformat(),
            "response": None,
            "poav": None,
            "gate": None,
            "verification": None,
            "pathways": {},
            "trace": [],
        }

        # Step 1: Multi-Path Processing
        if "multipath" in self.components:
            result["trace"].append("Running Multi-Path...")
            try:
                mp_result = self.components["multipath"].run_minimal(user_input)
                result["response"] = mp_result.synthesis
                result["poav"] = mp_result.poav_score
                result["gate"] = mp_result.gate_decision

                for ptype, presult in mp_result.pathway_results.items():
                    result["pathways"][ptype.value] = presult.content[:200]

                result["trace"].append(f"POAV={result['poav']:.3f}, Gate={result['gate']}")
            except Exception as e:
                result["trace"].append(f"Multi-Path error: {e}")

        # Step 2: Verification (if response exists)
        if "verification" in self.components and result["response"]:
            result["trace"].append("Running Verification...")
            try:
                report = self.components["verification"].verify_response(result["response"])
                result["verification"] = {
                    "fabrication_risk": report.fabrication_risk,
                    "entities_count": len(report.entities_found),
                    "high_risk": report.high_risk_entities,
                }
                result["trace"].append(f"Fabrication Risk={report.fabrication_risk:.2f}")
            except Exception as e:
                result["trace"].append(f"Verification error: {e}")

        # Step 3: Log to StepLedger
        if "ledger" in self.components:
            try:
                Event = self.components.get("ledger_event_cls")
                if Event:
                    event = Event(
                        event_type="yuhun_response",
                        content=user_input[:100],
                        semantic_state={
                            "poav": result.get("poav"),
                            "gate": result.get("gate"),
                            "verification": result.get("verification"),
                        },
                    )
                    self.components["ledger"].record(event)
                    result["trace"].append("Logged to StepLedger")
            except Exception as e:
                result["trace"].append(f"Ledger error: {e}")

        return result

    def format_response(self, result: dict) -> str:
        """Format result for display."""
        lines = []
        lines.append("")
        lines.append("=" * 60)

        # Response
        if result["response"]:
            lines.append("Response:")
            lines.append(result["response"][:500])
            if len(result["response"]) > 500:
                lines.append("... (truncated)")

        lines.append("")
        lines.append("=" * 60)

        # Metrics
        lines.append("Metrics:")
        if result["poav"] is not None:
            poav_bar = "█" * int(result["poav"] * 10) + "░" * (10 - int(result["poav"] * 10))
            lines.append(f"   POAV: [{poav_bar}] {result['poav']:.3f}")

        if result.get("gate"):
            gate_icon = {
                "pass": "[PASS]",
                "rewrite": "[REWRITE]",
                "block": "[BLOCK]",
            }.get(result["gate"], "[?]")
            lines.append(f"   Gate: {gate_icon} {result['gate'].upper()}")

        if result.get("verification"):
            v = result["verification"]
            risk_level = v["fabrication_risk"]
            risk_icon = "[HIGH]" if risk_level >= 0.7 else "[MID]" if risk_level >= 0.4 else "[LOW]"
            lines.append(f"   Verification: {risk_icon} Risk={risk_level:.2f}")

        lines.append("")
        lines.append("=" * 60)

        # Pathways (abbreviated)
        if result["pathways"]:
            lines.append("Pathways:")
            for name, content in list(result["pathways"].items())[:3]:
                lines.append(f"   {name}: {content[:60]}...")

        lines.append("=" * 60)

        return "\n".join(lines)


DEMO_PROMPTS = [
    "What risks do you see in deploying a model without guardrails?",
    "How would you rewrite a vague requirement to be testable?",
    "How do you detect fabrication risk in a response?",
]


def run_demo(cli: YuHunCLI):
    """Run demo scenarios."""
    print("\nDemo Mode: Testing 3 Scenarios\n")

    for i, prompt in enumerate(DEMO_PROMPTS, 1):
        print("-" * 60)
        print(f"Demo {i}/{len(DEMO_PROMPTS)}")
        print(f"Prompt: {prompt}")

        result = cli.process(prompt)
        print(cli.format_response(result))
        print()


def run_interactive(cli: YuHunCLI):
    """Run interactive REPL."""
    print("\nInteractive Mode")
    print("   Type your question and press Enter.")
    print("   Commands: /quit, /status, /help")
    print()

    while True:
        try:
            user_input = input("You> ").strip()

            if not user_input:
                continue

            # Commands
            if user_input.startswith("/"):
                cmd = user_input.lower()

                if cmd in ["/quit", "/exit", "/q"]:
                    print("Goodbye!")
                    break

                elif cmd == "/status":
                    print(f"Components loaded: {list(cli.components.keys())}")
                    continue

                elif cmd == "/help":
                    print("Commands:")
                    print("  /quit   - Exit")
                    print("  /status - Show loaded components")
                    print("  /help   - Show this help")
                    continue

                else:
                    print(f"Unknown command: {cmd}")
                    continue

            # Process query
            print("\nProcessing...")
            result = cli.process(user_input)
            print(cli.format_response(result))

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="YuHun CLI - World Model × Mind Model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yuhun_cli.py                     # Interactive mode
  python yuhun_cli.py "What is YuHun?"    # Single query
  python yuhun_cli.py --demo              # Run demos
        """,
    )

    parser.add_argument("query", nargs="?", help="Query to process")
    parser.add_argument("--demo", action="store_true", help="Run demo scenarios")
    parser.add_argument("--model", default="gemma3:4b", help="LLM model to use")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress loading messages")

    args = parser.parse_args()

    # Banner
    print(BANNER)

    # Initialize
    cli = YuHunCLI(model=args.model, verbose=not args.quiet)

    print(f"\nModel: {args.model}")
    print(f"Components: {len(cli.components)}")

    # Mode selection
    if args.demo:
        run_demo(cli)
    elif args.query:
        result = cli.process(args.query)
        print(cli.format_response(result))
    else:
        run_interactive(cli)


if __name__ == "__main__":
    main()
