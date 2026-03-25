#!/usr/bin/env python3
"""Launch the ToneSoul world map with live zone data + WebSocket auto-refresh.

Watches governance_state.json and zone_registry.json for changes.
Browser auto-updates without page refresh when data changes.

Usage:
    python scripts/launch_world.py
    python scripts/launch_world.py --port 8766
    python scripts/launch_world.py --no-browser
"""
from __future__ import annotations

import argparse
import http.server
import json
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLD_HTML = ROOT / "apps" / "dashboard" / "world.html"
GOV_STATE = ROOT / "governance_state.json"
TRACES = ROOT / "memory" / "autonomous" / "session_traces.jsonl"
REGISTRY = ROOT / "memory" / "autonomous" / "zone_registry.json"

sys.path.insert(0, str(ROOT))

# ── WebSocket clients (simple set of write-capable sockets) ──────────────────
_ws_clients: set = set()
_ws_lock = threading.Lock()

# ── Current data (rebuilt on file change) ───────────────────────────────────
_world_json: str = "{}"
_gov_json: str = "{}"
_html_cache: str = ""
_data_lock = threading.Lock()


def rebuild_data() -> None:
    """Rebuild zone_registry from traces + governance state. Thread-safe."""
    global _world_json, _gov_json, _html_cache
    try:
        from tonesoul.zone_registry import rebuild_and_save
        world = rebuild_and_save(
            traces_path=TRACES,
            governance_path=GOV_STATE,
            registry_path=REGISTRY,
        )
        wj = json.dumps(world.to_dict(), ensure_ascii=False)
        gj = GOV_STATE.read_text(encoding="utf-8") if GOV_STATE.exists() else "{}"

        html = WORLD_HTML.read_text(encoding="utf-8")
        inject = f"""
<script>
// Auto-injected by launch_world.py
var __WORLD_DATA__ = {wj};
var __GOV_DATA__ = {gj};
</script>
"""
        html = html.replace("</head>", inject + "\n</head>")
        # Inject WebSocket client into HTML
        ws_script = """
<script>
(function() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(proto + '//' + location.host + '/ws');
  ws.onmessage = function(e) {
    try {
      const d = JSON.parse(e.data);
      if (d.type === 'reload' && typeof loadAll === 'function') {
        loadAll(d.world, d.gov);
        console.log('[ToneSoul] World auto-updated.');
      }
    } catch(err) {}
  };
  ws.onclose = function() {
    setTimeout(function() { location.reload(); }, 3000);
  };
})();
</script>
"""
        html = html.replace("</body>", ws_script + "\n</body>")

        with _data_lock:
            _world_json = wj
            _gov_json = gj
            _html_cache = html
        print(f"[World] Rebuilt: {world.total_sessions} sessions, {len(world.zones)} zones")
    except Exception as e:
        print(f"[World] Rebuild error: {e}")


def push_update() -> None:
    """Push new data to all connected WebSocket clients."""
    with _data_lock:
        wj = _world_json
        gj = _gov_json
    payload = json.dumps({
        "type": "reload",
        "world": json.loads(wj),
        "gov": json.loads(gj),
    }, ensure_ascii=False)

    dead = set()
    with _ws_lock:
        clients = set(_ws_clients)
    for client in clients:
        try:
            _ws_send(client, payload)
        except Exception:
            dead.add(client)
    if dead:
        with _ws_lock:
            _ws_clients -= dead
    if clients:
        print(f"[World] Pushed update to {len(clients)} client(s)")


# ── Minimal WebSocket implementation (no external deps) ──────────────────────
import base64, hashlib, struct, socket as _socket

def _ws_handshake(rfile, wfile, headers: dict) -> bool:
    key = headers.get("sec-websocket-key", "")
    if not key:
        return False
    accept = base64.b64encode(
        hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
    ).decode()
    wfile.write(
        b"HTTP/1.1 101 Switching Protocols\r\n"
        b"Upgrade: websocket\r\n"
        b"Connection: Upgrade\r\n"
        b"Sec-WebSocket-Accept: " + accept.encode() + b"\r\n\r\n"
    )
    wfile.flush()
    return True


def _ws_send(wfile, text: str) -> None:
    data = text.encode("utf-8")
    length = len(data)
    if length < 126:
        header = bytes([0x81, length])
    elif length < 65536:
        header = bytes([0x81, 126]) + struct.pack(">H", length)
    else:
        header = bytes([0x81, 127]) + struct.pack(">Q", length)
    wfile.write(header + data)
    wfile.flush()


def _ws_recv(rfile) -> str | None:
    """Read one WebSocket frame, return text or None on close."""
    try:
        b0, b1 = rfile.read(2)
        masked = bool(b1 & 0x80)
        length = b1 & 0x7F
        if length == 126:
            length = struct.unpack(">H", rfile.read(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", rfile.read(8))[0]
        mask = rfile.read(4) if masked else b"\x00\x00\x00\x00"
        payload = bytearray(rfile.read(length))
        if masked:
            for i in range(length):
                payload[i] ^= mask[i % 4]
        opcode = b0 & 0x0F
        if opcode == 0x8:  # close
            return None
        return payload.decode("utf-8", errors="replace")
    except Exception:
        return None


# ── File watcher ─────────────────────────────────────────────────────────────
def _watch_files() -> None:
    """Watch data files; rebuild + push when they change."""
    watched = [GOV_STATE, TRACES, REGISTRY]
    mtimes: dict[Path, float] = {}
    while True:
        changed = False
        for p in watched:
            try:
                mt = p.stat().st_mtime if p.exists() else 0.0
            except OSError:
                mt = 0.0
            if mtimes.get(p) != mt:
                mtimes[p] = mt
                changed = True
        if changed:
            rebuild_data()
            push_update()
        time.sleep(2)


# ── HTTP + WebSocket handler ─────────────────────────────────────────────────
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        # WebSocket upgrade
        if self.headers.get("Upgrade", "").lower() == "websocket":
            hdrs = {k.lower(): v.strip() for k, v in self.headers.items()}
            if not _ws_handshake(self.rfile, self.wfile, hdrs):
                self.send_error(400)
                return
            wfile = self.wfile
            with _ws_lock:
                _ws_clients.add(wfile)
            # Send current state immediately on connect
            try:
                with _data_lock:
                    wj, gj = _world_json, _gov_json
                _ws_send(wfile, json.dumps({
                    "type": "reload",
                    "world": json.loads(wj),
                    "gov": json.loads(gj),
                }, ensure_ascii=False))
            except Exception:
                pass
            # Keep connection alive, handle pings
            try:
                while True:
                    msg = _ws_recv(self.rfile)
                    if msg is None:
                        break
            except Exception:
                pass
            with _ws_lock:
                _ws_clients.discard(wfile)
            return

        # Normal HTTP — serve world map HTML
        with _data_lock:
            html = _html_cache
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, fmt: str, *log_args: object) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="ToneSoul world map with live updates")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not WORLD_HTML.exists():
        print(f"ERROR: world.html not found at {WORLD_HTML}")
        sys.exit(1)

    # Initial build
    rebuild_data()

    # Start file watcher
    t = threading.Thread(target=_watch_files, daemon=True)
    t.start()

    server = http.server.HTTPServer(("127.0.0.1", args.port), Handler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}"

    print(f"[ToneSoul World] {url}")
    print("檔案有變動會自動推送到瀏覽器，不需要重新整理。")
    print("Ctrl+C 停止。\n")

    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[World] 已停止。")
        server.shutdown()


if __name__ == "__main__":
    main()
