# Game Structure Recon — Redacted

Engine confirmed: **GameMaker Studio 2**

Recon performed locally via string-level analysis of game binary.
Note: Full decompile via UndertaleModTool CLI was incomplete (AGRP chunk
error in v0.8.4.1); findings below are from printable string extraction,
not verified GML source.

Specific object names, script contents, dialogue text, and hook details
are kept local (never committed).

---

## confirmed engine capabilities

| capability | status |
|---|---|
| `file_text_open_write` / file I/O | assumed present (GMS2 built-in) |
| `http_request` / `http_get` / `http_post` | **not found in strings — unconfirmed** |
| `async_load` HTTP event | unconfirmed (depends on http_request) |
| `json_parse` / `json_stringify` | likely present (GMS2 standard) |

**Implication**: Route B must use file-bridge mode, not HTTP mode.
`bridge/server.py --mode file` is the correct startup for Route B.

---

## file bridge protocol (Route B)

```
GML side:
  1. build JSON string: {"event":..., "player_choice":..., "scene":...}
  2. write to: working_directory() + "bridge_event.json"  (or %TEMP% path)
  3. poll for: working_directory() + "bridge_reply.json"  existence
  4. read reply, display in dialog, delete both files

Python side (bridge/server.py --mode file):
  1. watch bridge_event.json for new mtime
  2. read event, call Claude API
  3. write bridge_reply.json: {"reply":..., "trust":...}
```

---

## dialogue system scripts (local details only)

Confirmed dialogue-related scripts exist (names kept local).
Hook injection targets: inspect/interact → yes-no dialog flow.
Actual object and script names documented in local patch_manifest.json.

---

## what stays local

- data.win
- UTMT output and string dump
- Actual object / script names
- Dialogue strings
- Patched build artifacts
- patch_manifest.json with real hook points
