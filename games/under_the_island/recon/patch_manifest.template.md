# Patch Manifest Template — Route B

This template documents the *shape* of a GML injection manifest.
Actual hook points, script names, and dialogue content are kept local
(never committed — they're derived from the game binary).

---

## manifest structure

```json
{
  "schema_version": "v1",
  "game": "<game_id>",
  "engine": "GameMaker Studio 2",
  "bridge_url": "http://localhost:7701",
  "status": "pending_recon | recon_done | patched",
  "patches": [
    {
      "object": "<object_name>",
      "event": "<Step|Create|Other>",
      "trigger_condition": "<description>",
      "action": "call bridge /event",
      "async_handling": "Async HTTP event"
    }
  ],
  "notes": ""
}
```

---

## recon checklist (local only)

- [ ] Identify dialogue trigger objects via UndertaleModTool
- [ ] Map event names to in-game conditions
- [ ] Confirm async HTTP extension availability in build
- [ ] Test `http_request` → Async HTTP round-trip with mock server
- [ ] Verify no main-thread blocking on API call

---

## async integration pattern

GameMaker cannot block main thread waiting for HTTP.
The correct pattern:

```gml
// In dialogue trigger event:
global.bridge_req = http_request(bridge_url, "POST", headers, body);

// In Async - HTTP event:
if (async_load[? "id"] == global.bridge_req) {
    var _data = json_parse(async_load[? "result"]);
    global.ai_reply = _data.reply;
    // state machine picks up global.ai_reply when ready to display
}
```

---

## what stays local

- data.win
- UTMT decompile output
- Actual object/script names
- Dialogue strings
- Patched build artifacts
