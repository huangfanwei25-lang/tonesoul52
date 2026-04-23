# Game AI Character Bridge

Generic framework for adding a persistent-memory AI character to an existing game.

**Route A** — external overlay, no game modification (public, in this repo)  
**Route B** — GML injection into game binary (private, local only)

---

## repo boundary rules

| stays in repo | stays local only |
|---|---|
| bridge server framework | game binary (data.win) |
| persona template / schema | decompile output |
| event adapter interface | actual hook points |
| mock event source | character-specific persona pack |
| redacted recon notes | patched build |

---

## directory layout

```
games/under_the_island/
  bridge/
    server.py               Route A HTTP server (port 7701)
    persona_template.py     Generic character persona scaffold
    soul_schema.json        Soul store schema
    event_adapter.py        Abstract event source interface
    character_pack.local.json   ← your local persona (git-ignored)
    soul_store.local.json       ← your local save state (git-ignored)
  mock/
    fake_events.json        Dev events for testing without the game
  recon/
    structure_report_redacted.md   Engine recon (no IP content)
    patch_manifest.template.md     Route B manifest schema
  overlay/                  (future) Electron/web overlay shell
```

---

## quick start (Route A)

```bash
# 1. install
pip install anthropic

# 2. create your local persona pack (git-ignored)
cp games/under_the_island/bridge/persona_template.py \
   games/under_the_island/bridge/character_pack.local.json
# edit character_pack.local.json with your character's name/personality

# 3. set API key
export ANTHROPIC_API_KEY=your_key

# 4. start bridge
python games/under_the_island/bridge/server.py \
  --token mytoken --game-id your_game --character your_character

# 5. send a test event
curl -X POST http://localhost:7701/event \
  -H "Authorization: Bearer mytoken" \
  -H "Content-Type: application/json" \
  -d '{"event": "puzzle_solved", "player_choice": "helped_npc", "scene": "chamber"}'

# 6. ask the character
curl "http://localhost:7701/ask?msg=你好" \
  -H "Authorization: Bearer mytoken"
```

---

## Route B status

See `recon/patch_manifest.template.md` for the manifest schema.  
Actual injection points are documented locally (not committed).

Async pattern required — see template for GML snippet.
