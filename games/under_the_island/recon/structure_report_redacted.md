# Game Structure Recon — Redacted

Engine confirmed: **GameMaker Studio 2**

Recon performed locally via UndertaleModTool.
Specific findings (object names, script contents, dialogue text) are kept
local and not committed — they're derived from the game binary.

---

## confirmed file layout (public info only)

```
<install dir>/
  data.win          ← main compiled data (GML bytecode + assets)
  *.yy              ← GameMaker project metadata
  GMEXT-*.html      ← extension documentation
```

---

## confirmed engine capabilities

- `http_request()` available (built-in async HTTP)
- `json_parse()` / `json_stringify()` available
- Async HTTP event pattern works for bridge calls
- No native blocking HTTP — async required

---

## integration approach

Route B injects calls at dialogue trigger points.
Actual hook locations documented in local `patch_manifest.json`
(not committed).

See `patch_manifest.template.md` for the manifest schema.
