# Game AI Character Bridge

Generic framework for adding a persistent-memory AI character to an existing game.

**Route A** — external overlay, no game modification (this repo, public)
**Route B** — GML injection into game binary (local only, never committed)

---

## Repo boundary

| Stays in this repo | Stays local only |
|---|---|
| Bridge server + provider logic | Game binary (`data.win`) |
| Persona template + soul schema | Decompile output |
| Event adapter (mock + file bridge) | Real hook points |
| Mock events for dev/testing | Character-specific persona pack |
| Redacted recon notes | Patched build artifacts |

---

## Directory layout

```
games/under_the_island/
  bridge/
    server.py             Main entry point — HTTP and/or file-bridge server
    llm_provider.py       Multi-provider LLM interface (Anthropic, Gemini, auto)
    persona_template.py   Generic character persona scaffold
    soul_schema.json      Soul store schema (no IP)
    event_adapter.py      EventAdapter base + MockEventAdapter + FileBridgeAdapter
    character_pack.local.json   ← your local persona (git-ignored)
    soul_store.local.json       ← your local save state (git-ignored)
  mock/
    fake_events.json      Dev events — test bridge without the game
  recon/
    structure_report_redacted.md   Engine recon (no IP)
    patch_manifest.template.md     Route B manifest schema
```

---

## Quick start

### 1. Install

```bash
# Anthropic (Claude)
pip install anthropic
export ANTHROPIC_API_KEY=sk-...

# Gemini (Google)
pip install google-genai
export GEMINI_API_KEY=...
```

### 2. Create your local persona (git-ignored)

```json
// bridge/character_pack.local.json
{
  "character_name": "Your Character",
  "personality_description": "...",
  "speech_style": "...",
  "value_axes": {
    "trust": 0.40,
    "honesty": 0.80,
    "curiosity": 0.85
  }
}
```

### 3. Start the bridge

**Anthropic (auto-detected if ANTHROPIC_API_KEY is set):**
```bash
python games/under_the_island/bridge/server.py --mode file \
  --game-save-folder "C:\Users\user\AppData\Local\YourGame"
```

**Gemini:**
```bash
python games/under_the_island/bridge/server.py --mode file \
  --provider gemini \
  --game-save-folder "C:\Users\user\AppData\Local\YourGame"
```

**Auto (picks provider based on which key is present):**
```bash
python games/under_the_island/bridge/server.py --mode file \
  --provider auto \
  --game-save-folder "C:\Users\user\AppData\Local\YourGame"
```

**Override model:**
```bash
python games/under_the_island/bridge/server.py --mode file \
  --provider anthropic --model claude-opus-4-7 \
  --game-save-folder "C:\Users\user\AppData\Local\YourGame"
```

**HTTP mode (if game has http_request extension):**
```bash
python games/under_the_island/bridge/server.py --mode http \
  --provider anthropic --token mytoken
```

---

## Provider / model config reference

| Priority | Source | Example |
|---|---|---|
| 1 (highest) | `--provider` / `--model` CLI flags | `--provider gemini` |
| 2 | `BRIDGE_LLM_PROVIDER` / `BRIDGE_LLM_MODEL` env vars | `export BRIDGE_LLM_MODEL=gemini-pro` |
| 3 (lowest) | Built-in defaults | anthropic → `claude-sonnet-4-6` / gemini → `gemini-2.0-flash` |

**`auto` provider selection order:**
1. `BRIDGE_LLM_PROVIDER` env var
2. `ANTHROPIC_API_KEY` present → anthropic
3. `GEMINI_API_KEY` present → gemini
4. Fallback → anthropic

---

## Diagnostics

Check your config before starting (no API call made):

```bash
python games/under_the_island/bridge/server.py --diagnose
```

Example output when ready:
```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-6",
  "anthropic_key_set": true,
  "gemini_key_set": false,
  "package_ok": true,
  "issues": [],
  "ready": true
}
```

### What you'll see when something is wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| `reply` is `[錯誤：pip install anthropic]` | Package not installed | `pip install anthropic` |
| `reply` is `[錯誤：pip install google-genai ...]` | Wrong or missing package | `pip install google-genai` (not `google-generativeai`) |
| `reply` is `[Anthropic API 錯誤：...]` + "認證失敗" | Key missing or invalid | Set / check `ANTHROPIC_API_KEY` |
| `reply` is `[Gemini API 錯誤：...]` + "認證失敗" | Key missing or invalid | Set / check `GEMINI_API_KEY` |
| `[... Quota / rate limit ...]` | Usage exceeded | Wait or switch account |
| `[... 帳單問題 ...]` | Billing not enabled | Enable billing in API console |
| `bridge_reply.json` never appears | Server not polling / wrong path | Confirm `--game-save-folder` path and that server is running |
| `bridge_reply.json` appears but contains error string | API issue, not file-bridge issue | Run `--diagnose` to check |

---

## File bridge acceptance check

Run in order to confirm end-to-end functionality:

**Step 1 — Start server:**
```bash
python games/under_the_island/bridge/server.py --mode file \
  --provider auto \
  --game-save-folder "C:\Users\user\AppData\Local\YourGame"
```
✅ Expected: `File bridge active — watching C:\...\bridge_event.json`

**Step 2 — Write test event (PowerShell):**
```powershell
# Note: use -Encoding utf8BOM (PS7+) or pipe through UTF-8 without BOM
# The bridge handles BOM automatically, so either form works
$event = '{"event":"test_event","player_choice":"explore","scene":"start_room"}'
[System.IO.File]::WriteAllText(
  "$env:LOCALAPPDATA\YourGame\bridge_event.json",
  $event,
  [System.Text.Encoding]::UTF8
)
```

**Step 3 — Wait for reply:**
```powershell
$rp = "$env:LOCALAPPDATA\YourGame\bridge_reply.json"
$deadline = (Get-Date).AddSeconds(30)
while (-not (Test-Path $rp) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 300 }
if (Test-Path $rp) { Get-Content $rp } else { Write-Host "TIMEOUT" }
```
✅ Expected: `{"reply": "...", "trust": 0.40}` with non-empty `reply`

**Step 4 — Verify reply is from AI (not an error string):**
✅ reply should NOT start with `[錯誤` or `[Anthropic` or `[Gemini`

---

## Windows / PowerShell encoding notes

**Problem:** `Set-Content -Encoding utf8` in PowerShell 5.x writes a UTF-8 BOM
(`\xef\xbb\xbf`) before the JSON content. This broke earlier versions of the bridge.

**Status:** Fixed. `event_adapter.py` uses `utf-8-sig` encoding which strips the BOM
automatically. Both BOM and non-BOM UTF-8 files are handled correctly.

**Recommendation:** Use one of these safe write methods:
```powershell
# Safe: UTF-8 without BOM (explicit)
[System.IO.File]::WriteAllText($path, $json, [System.Text.Encoding]::UTF8)

# Also safe: PowerShell 7+ utf8BOM variant
$json | Set-Content $path -Encoding utf8BOM  # BOM is handled by bridge

# Avoid in PS5: Set-Content -Encoding utf8 can add BOM
```

---

## Route B status

See `recon/patch_manifest.template.md` for manifest schema.
Actual injection points are local only (not committed).

Required async pattern for GML (file bridge, no http_request needed):

```gml
// Write event (in dialogue trigger):
var _dir = environment_get_variable("LOCALAPPDATA") + "\YourGame\";
var _f = file_text_open_write(_dir + "bridge_event.json");
file_text_write_string(_f, json_stringify({
    event: "dialogue_trigger",
    player_choice: "inspect",
    scene: room_get_name(room)
}));
file_text_close(_f);
global.bridge_waiting = true;

// Poll for reply (in Step event or Alarm):
if (global.bridge_waiting) {
    var _rp = _dir + "bridge_reply.json";
    if (file_exists(_rp)) {
        var _rf = file_text_open_read(_rp);
        var _resp = json_parse(file_text_read_string(_rf));
        file_text_close(_rf);
        file_delete(_rp);
        file_delete(_dir + "bridge_event.json");
        global.ai_reply = _resp.reply;
        global.bridge_waiting = false;
    }
}
```
