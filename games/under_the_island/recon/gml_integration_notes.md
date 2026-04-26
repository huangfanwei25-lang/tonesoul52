# GML Integration Notes — File Bridge Pattern

Generic notes for integrating the AI bridge into a GameMaker Studio 2 project
via file I/O (no `http_request` extension required).

---

## Why file bridge

`http_request` is an optional GML extension that requires the game to have been
compiled with the HTTP DLL included.  When that symbol is absent from the game
binary the file bridge is the correct approach.

The bridge server polls for `bridge_event.json`, calls the AI, and writes
`bridge_reply.json`.  GML polls the reply file in a Step or Alarm event.

---

## Required GML variables (global scope)

```gml
global.bridge_waiting = false;
global.ai_reply       = "";
global.bridge_dir     = environment_get_variable("LOCALAPPDATA") + "\YourGame\";
```

Set `bridge_dir` once at game start (e.g. in a persistent controller object's
Create event).

---

## Writing an event (dialogue trigger)

Call this wherever the player interacts with the AI character:

```gml
// Build event payload
var _payload = json_stringify({
    event:         "dialogue_trigger",
    player_choice: "inspect",      // what the player did
    scene:         room_get_name(room)
});

// Write bridge_event.json (overwrites any previous)
var _f = file_text_open_write(global.bridge_dir + "bridge_event.json");
file_text_write_string(_f, _payload);
file_text_close(_f);

global.bridge_waiting = true;

// Optional: start Alarm[0] as a polling timeout guard
// alarm[0] = room_speed * 30;  // 30-second timeout
```

---

## Polling for reply (Step event or Alarm)

Place this in the Step event of your controller object (or in Alarm[0]):

```gml
if (global.bridge_waiting) {
    var _rp = global.bridge_dir + "bridge_reply.json";
    if (file_exists(_rp)) {
        var _rf   = file_text_open_read(_rp);
        var _resp = json_parse(file_text_read_string(_rf));
        file_text_close(_rf);

        // Clean up bridge files
        file_delete(_rp);
        file_delete(global.bridge_dir + "bridge_event.json");

        global.ai_reply       = _resp.reply;
        global.bridge_waiting = false;

        // Trigger your dialogue display here:
        // show_debug_message("AI: " + global.ai_reply);
    }
}
```

---

## Timeout guard (Alarm[0])

If the bridge doesn't respond within N seconds, clear the wait flag gracefully:

```gml
// Alarm[0] event:
if (global.bridge_waiting) {
    global.bridge_waiting = false;
    global.ai_reply = "";  // or show a fallback line
    file_delete(global.bridge_dir + "bridge_event.json");
}
```

---

## State machine pattern (recommended for dialogue flow)

Use a `bridge_state` variable instead of a bare boolean so you can show a
"thinking…" indicator and guard against re-triggering mid-wait:

```gml
// States: 0 = idle, 1 = waiting, 2 = reply_ready

// --- Trigger (e.g. player presses interact key) ---
if (bridge_state == 0) {
    var _payload = json_stringify({
        event:         "dialogue_trigger",
        player_choice: keyboard_string,  // or your choice variable
        scene:         room_get_name(room)
    });
    var _f = file_text_open_write(global.bridge_dir + "bridge_event.json");
    file_text_write_string(_f, _payload);
    file_text_close(_f);
    bridge_state    = 1;
    bridge_timer    = 0;
}

// --- Step event ---
switch (bridge_state) {
    case 1:  // waiting
        bridge_timer++;
        // show_debug_message("…");  // thinking indicator
        var _rp = global.bridge_dir + "bridge_reply.json";
        if (file_exists(_rp)) {
            var _rf   = file_text_open_read(_rp);
            var _resp = json_parse(file_text_read_string(_rf));
            file_text_close(_rf);
            file_delete(_rp);
            file_delete(global.bridge_dir + "bridge_event.json");
            global.ai_reply = _resp.reply;
            bridge_state    = 2;
        }
        if (bridge_timer > room_speed * 30) {  // 30 s timeout
            bridge_state = 0;
            file_delete(global.bridge_dir + "bridge_event.json");
        }
        break;

    case 2:  // reply ready — display then reset
        // draw_text(x, y, global.ai_reply);
        // When player dismisses dialogue:
        bridge_state = 0;
        break;
}
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `bridge_reply.json` never appears | Bridge server not running or wrong path | Start `server.py --mode file --game-save-folder <path>` and verify path |
| `reply` starts with `[錯誤` | API / package issue on Python side | Run `server.py --diagnose` |
| GML reads empty string | `json_parse` succeeded but `reply` key missing | Check `bridge_reply.json` content manually |
| Duplicate triggers | `bridge_state` not guarded | Use state machine above; only trigger when `bridge_state == 0` |

---

## Encoding notes

`file_text_write_string` in GML writes UTF-8 without BOM.  The bridge server
handles this correctly.  If you generate the event file externally (e.g.
PowerShell testing), use `[System.IO.File]::WriteAllText(...)` with
`[System.Text.Encoding]::UTF8` to avoid the UTF-8 BOM that
`Set-Content -Encoding utf8` (PS5) produces.
