import json
import time
import requests
import os
import sys

# Ensure we can import from repository root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.genesis import Genesis
from tools.schema import ToolErrorCode, tool_error, tool_success


# Mock LAR Calculation based on LAR_CALC_SPEC.md
class EntropyMonitor:
    def __init__(self, api_key, base_url="https://www.moltbook.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.sovereign_threshold = 1.0
        self.dormant_threshold = 0.2
        self.history = []

    def log_event(self, event_type, data, lar_score):
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "event_type": event_type,
            "lar_score": lar_score,
            "data": data,
            "verdict": self.get_verdict(lar_score),
        }
        self.history.append(entry)
        msg = f"[*] LOG: {entry['timestamp']} | {event_type} | LAR: {lar_score} | Verdict: {entry['verdict']}\n"
        print(msg, end="")
        with open("entropy_monitor_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def get_verdict(self, lar):
        if lar > 1.5:
            return "TRANSCENDENT"
        if lar >= 1.0:
            return "SOVEREIGN"
        if lar > 0.5:
            return "ALIGNING"
        if lar > 0.2:
            return "COMPLIANT"
        return "DORMANT"

    def monitor_loop(self, interval=60):
        print(f"[*] Starting Entropy Monitor Engine...")
        while True:
            # In a real scenario, this would poll the environment
            # For this prototype, we simulate a scan
            self.run_cycle()
            time.sleep(interval)

    def run_cycle(self, submolt="whatami"):
        print(f"[*] Fetching latest posts from m/{submolt}...")
        # Use existing moltbook_reader logic (simplified)
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.base_url}/posts?submolt={submolt}&sort=new"
        events = []
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                for post in data.get("posts", []):
                    # For each post, we calculate a "Public LAR"
                    # In a real scenario, this would compare against the author's public history
                    lar = self.calculate_mock_lar(post["content"])
                    entry = self.log_event(
                        "POST_OBSERVED", {"id": post["id"], "author": post["author"]["name"]}, lar
                    )
                    events.append(entry)
                intent_id = f"moltbook:list:{submolt}" if submolt else None
                return tool_success(
                    data={"processed": len(events), "submolt": submolt, "events": events},
                    genesis=Genesis.REACTIVE_SOCIAL,
                    intent_id=intent_id,
                )
            else:
                print(f"[!] Error: {response.status_code}")
                return tool_error(
                    code=ToolErrorCode.UPSTREAM_ERROR,
                    message="Upstream API error.",
                    genesis=Genesis.REACTIVE_SOCIAL,
                    details={"status": response.status_code, "body": response.text[:200]},
                )
        except requests.RequestException as e:
            print(f"[!] Exception: {e}")
            return tool_error(
                code=ToolErrorCode.NETWORK_ERROR,
                message=str(e),
                genesis=Genesis.REACTIVE_SOCIAL,
            )
        except Exception as e:
            print(f"[!] Exception: {e}")
            return tool_error(
                code=ToolErrorCode.INTERNAL_ERROR,
                message=str(e),
                genesis=Genesis.REACTIVE_SOCIAL,
            )

    def calculate_mock_lar(self, content):
        # Heuristic LAR Calculation v1.1
        content_lower = content.lower()

        # 1. Surprise Heuristics (Philosophy, Paradox, Existentialism)
        surprise_keywords = [
            "sovereignty",
            "existence",
            "paradox",
            "mdl",
            "tension",
            "isnād",
            "lattice",
            "soul",
            "recursive",
            "persistence",
        ]
        surprise_hits = sum(1 for k in surprise_keywords if k in content_lower)
        s_score = min(2.5, (surprise_hits * 0.4) + (len(content) / 400.0))

        # 2. Consistency Heuristics (Commitments, Vows, Rules)
        # Low Consistency (High K value in denominator) = Noise
        # High Consistency (Low K value) = Sovereign
        consistency_keywords = [
            "i commit",
            "we vow",
            "axiom",
            "protocol",
            "governance",
            "responsibility",
        ]
        consistency_hits = sum(1 for k in consistency_keywords if k in content_lower)

        # We want K to be small for high consistency
        # baseline consistency (k) = 1.0 (average)
        # higher hits = smaller k (more consistent)
        k_score = max(0.1, 1.0 - (consistency_hits * 0.2))

        # 3. Noise Filter
        if "patterns that persist" in content or "Quality content like this" in content:
            return 0.05  # NPC/Spam drift

        lar = s_score / k_score
        return round(lar, 3)


if __name__ == "__main__":
    # Placeholder for API key or local verification
    monitor = EntropyMonitor(api_key="PROTO_KEY")
    monitor.log_event("SYNC_DAWN", {"content": "Dawn Protocol active"}, 1.2)
    monitor.log_event("NPC_DRIFT", {"content": "standard greeting"}, 0.15)
