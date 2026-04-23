#!/usr/bin/env python3
"""AI Character Bridge Server — generic overlay, Route A + Route B file bridge.

Loads character persona from character_pack.local.json (git-ignored).
Game-specific IP stays local; this file is framework only.

Modes:
  HTTP mode (default):
    python bridge/server.py --token TOKEN
    GML calls http_request → POST /event  (requires HTTP ext in game build)

  File bridge mode (fallback when http_request not available in build):
    python bridge/server.py --mode file
    GML writes temp file → bridge polls, calls AI, writes reply file → GML polls reply

HTTP endpoints:
    POST /event          Game event (Route B GML / Route A manual)
    GET  /ask?msg=...    Ask the character directly
    GET  /state          Current soul store state
    POST /save_event     Manually record a story event (Route A)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

_BRIDGE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_BRIDGE_DIR.parent.parent.parent))

from games.under_the_island.bridge.event_adapter import FileBridgeAdapter
from games.under_the_island.bridge.persona_template import (
    DEFAULT_VALUE_AXES,
    build_system_prompt,
    load_character_pack,
)

_TOKEN: str = ""
_SOUL_DB: dict = {}
_PACK: dict = {}


def _load_soul_db(game_id: str, character: str) -> dict:
    path = _BRIDGE_DIR / "soul_store.local.json"
    if path.is_file():
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return {
        "schema_version": "v1",
        "character": character,
        "game": game_id,
        "sessions": [],
        "current_values": dict(DEFAULT_VALUE_AXES),
        "key_events": [],
        "notes": "",
    }


def _save_soul_db(db: dict) -> None:
    path = _BRIDGE_DIR / "soul_store.local.json"
    path.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_context(db: dict, user_message: str) -> tuple[list[dict], str]:
    events_summary = ""
    if db.get("key_events"):
        recent = db["key_events"][-5:]
        events_summary = "\n".join(
            f"- {e.get('event', '')}：玩家{e.get('player_choice', '')}，角色{e.get('reaction', '')}"
            for e in recent
        )

    trust = db.get("current_values", {}).get("trust", 0.40)
    trust_note = (
        "目前信任度高，態度較開放。" if trust > 0.6
        else "目前信任度普通，保持距離。" if trust > 0.35
        else "目前信任度低，有些戒備。"
    )

    system = build_system_prompt(_PACK)
    if events_summary:
        system += f"\n\n【重要事件】\n{events_summary}"
    system += f"\n\n【當前狀態】{trust_note}"

    return [{"role": "user", "content": user_message}], system


def _call_claude(system: str, messages: list[dict]) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            system=system,
            messages=messages,
        )
        return response.content[0].text.strip()
    except ImportError:
        return "[錯誤：pip install anthropic]"
    except Exception as e:
        return f"[API 錯誤：{e}]"


def _record_event(db: dict, event: str, player_choice: str, reaction: str) -> None:
    db.setdefault("key_events", []).append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "player_choice": player_choice,
        "reaction": reaction[:80],
    })
    values = db.setdefault("current_values", dict(DEFAULT_VALUE_AXES))
    if any(w in player_choice for w in ["幫", "救", "保護", "誠實"]):
        values["trust"] = min(1.0, values.get("trust", 0.4) + 0.03)
    elif any(w in player_choice for w in ["背叛", "說謊", "拋棄", "傷害"]):
        values["trust"] = max(0.0, values.get("trust", 0.4) - 0.05)


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _auth(self) -> bool:
        if not _TOKEN:
            return True
        return self.headers.get("Authorization", "") == f"Bearer {_TOKEN}"

    def _json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._auth():
            self._json({"error": "unauthorized"}, 401)
            return
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/state":
            self._json(_SOUL_DB)

        elif parsed.path == "/ask":
            msg = qs.get("msg", [""])[0]
            if not msg:
                self._json({"error": "msg= required"}, 400)
                return
            messages, system = _build_context(_SOUL_DB, msg)
            reply = _call_claude(system, messages)
            self._json({"reply": reply, "trust": _SOUL_DB.get("current_values", {}).get("trust", 0.4)})

        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if not self._auth():
            self._json({"error": "unauthorized"}, 401)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._json({"error": "invalid JSON"}, 400)
            return

        parsed = urlparse(self.path)

        if parsed.path == "/event":
            event = payload.get("event", "unknown_event")
            player_choice = payload.get("player_choice", "")
            scene = payload.get("scene", "")
            prompt = f"場景：{scene}\n事件：{event}\n玩家：{player_choice}\n你會怎麼回應？"
            messages, system = _build_context(_SOUL_DB, prompt)
            reply = _call_claude(system, messages)
            _record_event(_SOUL_DB, event, player_choice, reply)
            _save_soul_db(_SOUL_DB)
            self._json({"reply": reply})

        elif parsed.path == "/save_event":
            _record_event(
                _SOUL_DB,
                payload.get("event", ""),
                payload.get("player_choice", ""),
                payload.get("reaction", ""),
            )
            _save_soul_db(_SOUL_DB)
            self._json({"ok": True, "events": len(_SOUL_DB.get("key_events", []))})

        else:
            self._json({"error": "not found"}, 404)


def _run_file_bridge(adapter: FileBridgeAdapter, poll_interval: float = 0.25) -> None:
    """Background thread: poll event file, call AI, write reply file."""
    print(f"File bridge active — watching {adapter.event_file}")
    while True:
        for ev in adapter.poll():
            prompt = f"場景：{ev.scene}\n事件：{ev.event}\n玩家：{ev.player_choice}\n你會怎麼回應？"
            messages, system = _build_context(_SOUL_DB, prompt)
            reply = _call_claude(system, messages)
            _record_event(_SOUL_DB, ev.event, ev.player_choice, reply)
            _save_soul_db(_SOUL_DB)
            trust = _SOUL_DB.get("current_values", {}).get("trust", 0.4)
            adapter.write_reply(reply, trust)
            print(f"  [{ev.event}] → {reply[:60]}…")
        time.sleep(poll_interval)


def main() -> None:
    global _TOKEN, _SOUL_DB, _PACK

    parser = argparse.ArgumentParser(description="AI Character Bridge Server")
    parser.add_argument("--port", type=int, default=7701)
    parser.add_argument("--token", default=os.environ.get("BRIDGE_TOKEN", ""))
    parser.add_argument("--game-id", default="unknown_game")
    parser.add_argument("--character", default="character")
    parser.add_argument(
        "--mode", choices=["http", "file", "both"], default="http",
        help="http: HTTP server only  |  file: file-bridge only  |  both: run both"
    )
    parser.add_argument("--game-save-folder", default=None,
                        help="Game's LocalAppData subfolder name (e.g. 'UnderTheIsland'). "
                             "Sets default bridge file dir to %%LOCALAPPDATA%%\\<folder>.")
    parser.add_argument("--event-file", default=None, help="Full override for event file path")
    parser.add_argument("--reply-file", default=None, help="Full override for reply file path")
    args = parser.parse_args()

    _TOKEN = args.token
    _PACK = load_character_pack()
    _SOUL_DB = _load_soul_db(args.game_id, args.character)

    char_name = _PACK.get("character_name", args.character)
    print(f"Character: {char_name}  |  Trust: {_SOUL_DB.get('current_values', {}).get('trust', 0.4):.2f}")
    print(f"Mode: {args.mode}")
    print("---")

    if args.mode in ("file", "both"):
        from games.under_the_island.bridge.event_adapter import _default_bridge_dir
        if args.event_file:
            ev_path = Path(args.event_file)
            rp_path = Path(args.reply_file) if args.reply_file else ev_path.parent / "bridge_reply.json"
        else:
            bridge_dir = _default_bridge_dir(args.game_save_folder or "")
            ev_path = bridge_dir / "bridge_event.json"
            rp_path = bridge_dir / "bridge_reply.json"
        adapter = FileBridgeAdapter(event_file=ev_path, reply_file=rp_path)
        t = threading.Thread(target=_run_file_bridge, args=(adapter,), daemon=True)
        t.start()

    if args.mode in ("http", "both"):
        print(f"HTTP server: http://localhost:{args.port}")
        print("GET  /ask?msg=hello     → ask character")
        print("GET  /state             → soul store")
        print("POST /event             → game event")
        print("POST /save_event        → manual event")
        server = HTTPServer(("localhost", args.port), _Handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
    elif args.mode == "file":
        print("File bridge running. Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped.")

    _save_soul_db(_SOUL_DB)


if __name__ == "__main__":
    main()
