#!/usr/bin/env python3
"""妮婭 AI 橋接伺服器 — Route A（外掛覆蓋層）

Route A：不修改遊戲，在外部執行。
Route B：GML 注入版本直接呼叫此 server，行為相同。

啟動：
    python games/under_the_island/overlay/server.py --token YOUR_TOKEN

端點：
    POST /event          接收遊戲事件（Route B GML 呼叫 / Route A 手動觸發）
    GET  /nia?msg=...    快速問妮婭一句話
    GET  /state          查看目前靈魂狀態
    POST /save_event     手動記錄一個劇情事件
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_DIR = Path(__file__).resolve().parent.parent / "shared"
SOUL_DB_PATH = SHARED_DIR / "soul_db.json"

sys.path.insert(0, str(REPO_ROOT))

from games.under_the_island.shared.nia_soul import (
    MEMORY_SCHEMA,
    NIA_SYSTEM_PROMPT,
    NIA_VALUE_AXES,
)

_TOKEN: str = ""
_SOUL_DB: dict = {}


def _load_soul_db() -> dict:
    if SOUL_DB_PATH.is_file():
        with SOUL_DB_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return json.loads(json.dumps({"schema_version": "v1", "character": "nia",
                                   "game": "under_the_island", "sessions": [],
                                   "current_values": dict(NIA_VALUE_AXES),
                                   "key_events": [], "notes": ""}))


def _save_soul_db(db: dict) -> None:
    SOUL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SOUL_DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_context(db: dict, user_message: str) -> list[dict]:
    """組合給 Claude 的 messages。"""
    events_summary = ""
    if db.get("key_events"):
        recent = db["key_events"][-5:]
        events_summary = "\n".join(
            f"- {e.get('event', '')}：玩家{e.get('player_choice', '')}，妮婭{e.get('nia_reaction', '')}"
            for e in recent
        )

    trust = db.get("current_values", {}).get("trust", 0.40)
    trust_note = (
        "目前對玩家信任度高，態度較開放。" if trust > 0.6
        else "目前對玩家信任度普通，保持一定距離。" if trust > 0.35
        else "目前對玩家信任度低，有些戒備。"
    )

    system = NIA_SYSTEM_PROMPT
    if events_summary:
        system += f"\n\n【這次冒險的重要事件】\n{events_summary}"
    system += f"\n\n【當前狀態】{trust_note}"

    return [
        {"role": "user", "content": user_message}
    ], system


def _call_claude(system: str, messages: list[dict]) -> str:
    """呼叫 Claude API。需要 ANTHROPIC_API_KEY 環境變數。"""
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
        return "[錯誤：請安裝 anthropic 套件：pip install anthropic]"
    except Exception as e:
        return f"[API 錯誤：{e}]"


def _record_event(db: dict, event: str, player_choice: str, nia_response: str) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "player_choice": player_choice,
        "nia_reaction": nia_response[:80],
    }
    db.setdefault("key_events", []).append(entry)
    # 信任度根據事件類型微調（簡單版本）
    values = db.setdefault("current_values", dict(NIA_VALUE_AXES))
    if any(w in player_choice for w in ["幫", "救", "保護", "誠實"]):
        values["trust"] = min(1.0, values.get("trust", 0.4) + 0.03)
    elif any(w in player_choice for w in ["背叛", "說謊", "拋棄", "傷害"]):
        values["trust"] = max(0.0, values.get("trust", 0.4) - 0.05)


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 靜默 HTTP log

    def _auth(self) -> bool:
        if not _TOKEN:
            return True
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {_TOKEN}"

    def _json_response(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._auth():
            self._json_response({"error": "unauthorized"}, 401)
            return

        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/state":
            self._json_response(_SOUL_DB)

        elif parsed.path == "/nia":
            msg = qs.get("msg", [""])[0]
            if not msg:
                self._json_response({"error": "msg= 參數必填"}, 400)
                return
            messages, system = _build_context(_SOUL_DB, msg)
            reply = _call_claude(system, messages)
            self._json_response({"reply": reply, "trust": _SOUL_DB.get("current_values", {}).get("trust", 0.4)})

        else:
            self._json_response({"error": "not found"}, 404)

    def do_POST(self):
        if not self._auth():
            self._json_response({"error": "unauthorized"}, 401)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._json_response({"error": "invalid JSON"}, 400)
            return

        parsed = urlparse(self.path)

        if parsed.path == "/event":
            # Route B GML 呼叫這個端點
            # payload: {event, player_choice, scene}
            event = payload.get("event", "unknown_event")
            player_choice = payload.get("player_choice", "")
            scene = payload.get("scene", "")
            prompt = f"場景：{scene}\n事件：{event}\n玩家：{player_choice}\n妮婭你會怎麼回應？"
            messages, system = _build_context(_SOUL_DB, prompt)
            reply = _call_claude(system, messages)
            _record_event(_SOUL_DB, event, player_choice, reply)
            _save_soul_db(_SOUL_DB)
            self._json_response({"reply": reply})

        elif parsed.path == "/save_event":
            # 手動記錄劇情事件（Route A 用）
            _record_event(
                _SOUL_DB,
                payload.get("event", ""),
                payload.get("player_choice", ""),
                payload.get("nia_reaction", ""),
            )
            _save_soul_db(_SOUL_DB)
            self._json_response({"ok": True, "events": len(_SOUL_DB.get("key_events", []))})

        else:
            self._json_response({"error": "not found"}, 404)


def main() -> None:
    global _TOKEN, _SOUL_DB

    parser = argparse.ArgumentParser(description="妮婭 AI 橋接伺服器")
    parser.add_argument("--port", type=int, default=7701)
    parser.add_argument("--token", default=os.environ.get("NIA_TOKEN", ""))
    args = parser.parse_args()

    _TOKEN = args.token
    _SOUL_DB = _load_soul_db()

    print(f"妮婭橋接伺服器啟動 http://localhost:{args.port}")
    print(f"Token: {'已設定' if _TOKEN else '未設定（開放存取）'}")
    print(f"靈魂狀態：信任度 {_SOUL_DB.get('current_values', {}).get('trust', 0.4):.2f}")
    print("---")
    print("GET  /nia?msg=你好         → 直接問妮婭")
    print("GET  /state                → 查看靈魂狀態")
    print("POST /event                → 傳入遊戲事件（Route B）")
    print("POST /save_event           → 手動記錄劇情事件（Route A）")

    server = HTTPServer(("localhost", args.port), _Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已關閉，記憶已儲存。")
        _save_soul_db(_SOUL_DB)


if __name__ == "__main__":
    main()
