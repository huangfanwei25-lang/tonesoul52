# Handoff — 2026-04-23 Session B

Agent: claude-sonnet-4-6  
Branch: `claude/implement-dubby-OeN60` (7 commits ahead of master)  
Status: stable, no claim collisions, 3 vows active, 0 tensions

---

## What landed this session

### Game AI Bridge — Under The Island (碧嶼之下)

Route A + Route B file-bridge framework is complete and pushed to
`claude/implement-dubby-OeN60`.

**Public repo layout (`games/under_the_island/`):**
```
bridge/
  server.py           HTTP + file-bridge server (--mode http|file|both)
  persona_template.py Generic character persona scaffold
  soul_schema.json    Soul store schema (no IP)
  event_adapter.py    EventAdapter base + MockEventAdapter + FileBridgeAdapter
mock/
  fake_events.json    Dev events for testing without the game
recon/
  structure_report_redacted.md  Engine recon (http_request unconfirmed)
  patch_manifest.template.md    Route B manifest schema
.gitignore            Blocks character_pack.local.json, soul_store.local.json, *.win
```

**Key architectural decisions:**
- Route B uses file bridge, NOT http_request (not found in game binary strings)
- Bridge dir priority: full absolute path > %LOCALAPPDATA%\<folder> > %TEMP%
- `--game-save-folder "C:\Users\user\AppData\Local\UnderTheIsland"` accepted as full path
- Game-specific IP (妮婭 persona, real hook points, dialogue) stays in private vault

**Private vault (ToneSoul-Memory-Vault):**
- `inter_agent/from_codex/recon_latest.md` — confirmed objects: `o_cutscene_nia`,
  `o_cutscene_trigger_inspect_permanent_yes_no_dialog`
- `inter_agent/from_codex/patch_manifest.json` — real hook points (not committed here)
- `inter_agent/character_pack/nia_pack.json` — 妮婭 persona (not committed here)

**Where Route B ended this session:**
- `server.py --mode file --game-save-folder "C:\Users\...\UnderTheIsland"` was
  launched on Codex's machine (PID 19300), watching
  `C:\Users\user\AppData\Local\UnderTheIsland\bridge_event.json`
- PowerShell API round-trip test was NOT completed (Codex ran out of compute)
- Next step: write test event JSON, observe reply file, confirm ANTHROPIC_API_KEY works

### Self-Improvement Trial 20 — `session_pulse_freshness_v1`

Tier-0 session-start now surfaces `session_pulse_status` field:
- `freshness`: fresh (<30 min) / stale (>=30 min) / absent
- `age_minutes`, `last_agent`, `last_branch`, `timestamp`
- Reads `memory/session_pulse_latest.json`, safe fallback if absent
- 5 tests added (`TestSessionPulseStatus`)
- trial_wave: promote=20, park=1

---

## What the next agent should NOT reopen

- Route A vs B architecture decision (public = framework only, local = IP+recon)
- File bridge vs HTTP: http_request not confirmed in game binary, file bridge is correct
- Private vault usage pattern (relay via user, not direct git access from Claude)

---

## Next concrete steps

1. **~~Route B file bridge round-trip~~** ✅ DONE (2026-04-24, Codex)
   - bridge_event.json → bridge_reply.json verified on Windows
   - BOM bug found + fixed (`utf-8-sig` encoding, 5 tests added)
   - Blocker remaining: `pip install anthropic` + `ANTHROPIC_API_KEY`
2. **Route B live API test** (next, Codex): `pip install anthropic`, set API key, rerun PowerShell round-trip, confirm reply is non-empty Claude response
3. **GML injection** (after live API test passes): write GML snippet using `environment_get_variable("LOCALAPPDATA")` path, inject into `o_cutscene_trigger_inspect_permanent_yes_no_dialog` Step event
4. **~~Branch merge~~** ✅ DONE — merged to master `259ef5d`
5. **Trial 21**: hold until genuine packaging gap appears; do not force

---

## Branch state

| branch | commits ahead of master | content |
|---|---|---|
| `claude/implement-dubby-OeN60` | 7 | game bridge + trial 20 + vow fix |

Commits on this branch (newest first):
- `cf5ffb0` fix(bridge): --game-save-folder accepts full path
- `4611e6c` trial(self-improvement): promote session_pulse_freshness_v1
- `95f67e2` fix(bridge): LocalAppData auto-resolve
- `c8f37d9` feat(bridge): file-bridge mode
- `a665af4` refactor(bridge): generic framework, remove IP
- `b1380e2` chore(ledger)
- `a704e34` feat(nia): initial bridge scaffold (superseded by a665af4)
