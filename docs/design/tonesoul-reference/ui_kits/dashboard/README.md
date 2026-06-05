# Dashboard UI Kit — Obsidian

> **Prototype / Reference only**
>
> This folder is a **prototype reference** for the Obsidian surface.
> It is **not** a production implementation and is **not** intended to be deployed as-is.
>
> Specifically:
> - `index.html` uses CDN React + ReactDOM + Babel so the file can be previewed standalone.
> - Dashboard data is fixture-driven; refresh, token storage, and status changes are demo behavior.
> - The token field does not represent real auth wiring.
> - No real API client, routing, or production build pipeline is included here.

Backend observability dashboard recreation. Mirrors `sources/council-playground/` at the level of tone, hierarchy, and panel composition.

## Canonical source in this package

Within this design-reference package, **`index.html` is the canonical source** for the Obsidian kit.

- `index.html` is the maintained v2 prototype.
- `index_v1.html` is kept as a **frozen contrast** so the revision remains traceable (Axiom 1).
- Treat `Components.jsx`, `App.jsx`, and `dashboard.css` as **frozen extracts for reading/reference**.
- Do **not** maintain the inlined HTML and the sibling JSX/CSS as two separate live implementations.

Upstream visual lineage still comes from `sources/council-playground/style.css`, but inside this package the single-file prototype is the maintained artifact.

## Components represented

- `TopBar.jsx` — sticky translucent header with gradient brand mark + refresh
- `Panel.jsx` · `PanelHeader.jsx` — the translucent panel chrome (14-px radius, deep shadow)
- `StatusCard.jsx` — label / value / hint, with tone class (`is-ok | is-warn | is-error`)
- `StatusCardGrid.jsx` — 4-column responsive grid
- `AuthRow.jsx` — 1fr + 2 buttons input row
- `AuditListItem.jsx` — list row: title + meta + body
- `Footer.jsx` — GitHub link + build stamp

Open `index.html` for the click-through demo: enter a token → Save → Refresh → see all panels populate with fixture data.
