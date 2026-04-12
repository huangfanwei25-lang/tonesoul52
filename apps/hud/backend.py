"""ToneSoul HUD — reflexive governance monitor.

Pure mirror: reads tier 0/1/2 from the governance runtime,
pushes JSON over WebSocket. No logic, no decisions, no re-computation.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="ToneSoul HUD")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Keep connected clients
_clients: set[WebSocket] = set()


def _read_tier(tier: int = 0) -> dict:
    """Read governance state via the session-start bundle. Pure read, no side effects."""
    try:
        from scripts.start_agent_session import run_session_start_bundle

        return run_session_start_bundle(
            agent_id="hud-monitor",
            tier=tier,
            no_ack=True,
        )
    except Exception as exc:
        return {"error": str(exc), "tier": tier}


def _read_observer() -> dict:
    """Read observer window — stable/contested/stale."""
    try:
        from tonesoul.observer_window import build_low_drift_anchor
        from tonesoul.runtime_adapter import load, r_memory_packet
        from tonesoul.store import get_store

        store = get_store()
        posture = load(agent_id="hud-monitor", source="hud")
        packet = r_memory_packet(posture=posture, store=store, observer_id="hud-monitor")

        # Minimal inputs for observer
        return build_low_drift_anchor(
            packet=packet,
            import_posture={},
            readiness={"status": "pass"},
            canonical_center={},
            subsystem_parity={},
            mutation_preflight={},
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/tier/{tier}")
async def api_tier(tier: int = 0):
    """REST fallback for one-shot reads."""
    return _read_tier(tier=min(tier, 2))


@app.get("/api/observer")
async def api_observer():
    return _read_observer()


@app.get("/api/crystals")
async def api_crystals():
    """Crystal freshness summary + top rules for HUD."""
    try:
        from tonesoul.memory.crystallizer import MemoryCrystallizer

        crystallizer = MemoryCrystallizer()
        summary = crystallizer.freshness_summary()
        top = crystallizer.top_crystals(n=5)
        return {
            **summary,
            "top_rules": [
                {
                    "rule": c.rule,
                    "weight": round(c.weight, 2),
                    "freshness": round(c.freshness_score, 2),
                    "phase": c.phase,
                    "stage": c.stage,
                }
                for c in top
            ],
        }
    except Exception as exc:
        return {"error": str(exc)}


@app.get("/api/pipeline")
async def api_pipeline():
    """Pipeline status: digest count + crystal summary."""
    try:
        from tonesoul.memory.crystallizer import MemoryCrystallizer

        crystallizer = MemoryCrystallizer()
        summary = crystallizer.freshness_summary()

        journal_path = REPO_ROOT / "memory" / "self_journal.jsonl"
        digest_count = 0
        total_journal = 0
        if journal_path.exists():
            with journal_path.open("r", encoding="utf-8") as f:
                for line in f:
                    total_journal += 1
                    if '"session_digest"' in line:
                        digest_count += 1

        return {
            "digest_count": digest_count,
            "journal_entries": total_journal,
            "crystal_summary": summary,
        }
    except Exception as exc:
        return {"error": str(exc)}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _clients.add(ws)
    try:
        # Send initial state immediately
        data = _read_tier(tier=0)
        await ws.send_json({"type": "tier0", "ts": time.time(), "data": data})

        # Then push updates every 10 seconds
        while True:
            await asyncio.sleep(10)
            data = _read_tier(tier=0)
            await ws.send_json({"type": "tier0", "ts": time.time(), "data": data})
    except WebSocketDisconnect:
        pass
    finally:
        _clients.discard(ws)


def main():
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="ToneSoul HUD server")
    parser.add_argument("--port", type=int, default=3001)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    print(f"ToneSoul HUD: http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
