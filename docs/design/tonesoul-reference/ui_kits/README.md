# UI Kits

Two product surfaces shipped with ToneSoul, recreated here as pixel-faithful component kits.

| Kit | Aesthetic | Source | Purpose |
| --- | --- | --- | --- |
| `site/` | **Blueprint** · parchment + steel blue | `sources/site/` | Public marketing / docs site (GitHub Pages). Shipped in English with Chinese ceremonial accents. |
| `dashboard/` | **Obsidian** · deep navy + cyan/mint glow | `sources/council-playground/` | Backend observability dashboard for operators. Shipped in Traditional Chinese (`zh-TW`). |

Each kit contains:

- `README.md` — what it covers, which source files it mirrors
- `index.html` — a click-thru prototype demonstrating the kit in use
- `Component*.jsx` — small, composable React components (loaded via Babel standalone)

Components are cosmetic recreations — they reproduce the visual language, not the backing logic. Data is faked; buttons advance prototype state.
