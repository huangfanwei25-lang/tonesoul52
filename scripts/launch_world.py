#!/usr/bin/env python3
"""Launch the ToneSoul world map with live zone data + WebSocket auto-refresh.

Watches governance_state.json and session_traces.jsonl when using FileStore.
With Redis enabled, subscribes to live governance events instead.
Browser auto-updates without page refresh when data changes.

Usage:
    python scripts/launch_world.py
    python scripts/launch_world.py --port 8766
    python scripts/launch_world.py --no-browser
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import struct
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
_visitors_json: str = "[]"
_aegis_json: str = '{"integrity":"unknown"}'
_html_cache: str = ""
_data_lock = threading.Lock()
_active_store = None
_last_governance_refresh_at = 0.0
_REDIS_ZONE_DEDUP_WINDOW = 1.0


def _get_active_store():
    """Return the cached ToneSoul store when available."""
    global _active_store
    if _active_store is not None:
        return _active_store
    try:
        from tonesoul.store import get_store

        _active_store = get_store()
    except Exception:
        _active_store = None
    return _active_store


def rebuild_data() -> None:
    """Rebuild zone_registry from traces + governance state. Thread-safe."""
    global _world_json, _gov_json, _visitors_json, _aegis_json, _html_cache
    try:
        from tonesoul.zone_registry import rebuild_and_save

        store = _get_active_store()
        if store is not None and store.is_redis:
            world = rebuild_and_save(store=store)
            gj = json.dumps(store.get_state() or {}, ensure_ascii=False)
        else:
            world = rebuild_and_save(
                traces_path=TRACES,
                governance_path=GOV_STATE,
                registry_path=REGISTRY,
            )
            gj = GOV_STATE.read_text(encoding="utf-8") if GOV_STATE.exists() else "{}"
        wj = json.dumps(world.to_dict(), ensure_ascii=False)

        # Gather visitors + aegis data
        vj = "[]"
        aj = '{"integrity":"unknown"}'
        try:
            if store is not None and store.is_redis:
                from tonesoul.runtime_adapter import get_recent_visitors

                visitors = get_recent_visitors(store, n=10)
                vj = json.dumps(visitors, ensure_ascii=False)
            if store is not None:
                from tonesoul.aegis_shield import AegisShield

                shield = AegisShield.load(store)
                audit = shield.audit(store)
                aj = json.dumps(audit, ensure_ascii=False)
        except Exception:
            pass

        html = WORLD_HTML.read_text(encoding="utf-8")
        inject = f"""
<script>
// Auto-injected by launch_world.py
var __WORLD_DATA__ = {wj};
var __GOV_DATA__ = {gj};
var __VISITORS__ = {vj};
var __AEGIS__ = {aj};
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
        if (d.visitors) __VISITORS__ = d.visitors;
        if (d.aegis) __AEGIS__ = d.aegis;
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
            _visitors_json = vj
            _aegis_json = aj
            _html_cache = html
        print(f"[World] Rebuilt: {world.total_sessions} sessions, {len(world.zones)} zones")
    except Exception as e:
        print(f"[World] Rebuild error: {e}")


def push_update() -> None:
    """Push new data to all connected WebSocket clients."""
    with _data_lock:
        wj = _world_json
        gj = _gov_json
        vj = _visitors_json
        aj = _aegis_json
    payload = json.dumps(
        {
            "type": "reload",
            "world": json.loads(wj),
            "gov": json.loads(gj),
            "visitors": json.loads(vj),
            "aegis": json.loads(aj),
        },
        ensure_ascii=False,
    )

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
            _ws_clients.difference_update(dead)
    if clients:
        print(f"[World] Pushed update to {len(clients)} client(s)")


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


# ── File watcher (fallback when Redis unavailable) ───────────────────────────
def _watch_files() -> None:
    """Watch data files; rebuild + push when they change.

    NOTE: REGISTRY is excluded because rebuild_data() writes it,
    which would cause an infinite rebuild loop.
    """
    watched = [GOV_STATE, TRACES]
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


# ── Redis pub/sub watcher (zero-latency when Redis available) ─────────────────
def _watch_redis(store) -> None:
    """Subscribe to ts:events; rebuild + push immediately on governance change."""
    from tonesoul.store import CHANNEL_EVENTS

    print("[World] Redis pub/sub active — zero-latency updates enabled.")
    try:
        for msg in store.subscribe(CHANNEL_EVENTS):
            _handle_redis_event(msg.get("type", ""))
    except Exception as e:
        print(f"[World] Redis watcher error: {e} — falling back to file polling")
        _watch_files()


# ── HTTP + WebSocket handler ─────────────────────────────────────────────────
def _handle_redis_event(msg_type: str, *, now: float | None = None) -> str:
    """Prevent one commit from causing duplicate world rebuild cascades."""
    global _last_governance_refresh_at

    event_time = time.monotonic() if now is None else now
    if msg_type == "governance:updated":
        _last_governance_refresh_at = event_time
        rebuild_data()
        push_update()
        return "rebuild"
    if msg_type == "zones:updated":
        if event_time - _last_governance_refresh_at <= _REDIS_ZONE_DEDUP_WINDOW:
            return "deduped"
        rebuild_data()
        push_update()
        return "rebuild"
    return "ignored"


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
                    vj, aj = _visitors_json, _aegis_json
                _ws_send(
                    wfile,
                    json.dumps(
                        {
                            "type": "reload",
                            "world": json.loads(wj),
                            "gov": json.loads(gj),
                            "visitors": json.loads(vj),
                            "aegis": json.loads(aj),
                        },
                        ensure_ascii=False,
                    ),
                )
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


def _build_server(port: int):
    """Use a threaded server so long-lived WebSocket clients do not block HTTP."""
    return http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> None:
    global _active_store

    parser = argparse.ArgumentParser(description="ToneSoul world map with live updates")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not WORLD_HTML.exists():
        print(f"ERROR: world.html not found at {WORLD_HTML}")
        sys.exit(1)

    # Initial build
    rebuild_data()

    # Start watcher: Redis pub/sub if available, else file polling
    try:
        from tonesoul.store import get_store

        store = get_store()
        _active_store = store
        if store.is_redis:

            def watcher_target() -> None:
                _watch_redis(store)

        else:
            watcher_target = _watch_files
    except Exception:
        _active_store = None
        watcher_target = _watch_files

    t = threading.Thread(target=watcher_target, daemon=True)
    t.start()

    server = _build_server(args.port)
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
