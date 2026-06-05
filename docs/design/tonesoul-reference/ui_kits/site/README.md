# Site UI Kit — Blueprint

> **Prototype / Reference only**
>
> This folder is a **prototype reference** for the Blueprint surface.
> It is **not** a production implementation and is **not** intended to be deployed as-is.
>
> Specifically:
> - `index.html` uses CDN React + ReactDOM + Babel so the file can be previewed standalone.
> - Navigation is front-end page-state only, not a real router.
> - Buttons and click-through states are demo interactions for layout review.
> - No build pipeline, deep-linking, or production SEO behavior is included here.

Marketing + docs site recreation. Mirrors `sources/site/` (GitHub Pages build) at the level of visual language and content structure.

## Canonical source in this package

Within this design-reference package, **`index.html` is the canonical source** for the Blueprint kit.

- Edit `index.html` when the packaged prototype itself changes.
- Treat `Components.jsx`, `Pages.jsx`, and `site.css` as **frozen extracts for reading/reference**.
- Do **not** maintain the inlined HTML and the sibling JSX/CSS as two separate live implementations.

Upstream visual lineage still comes from `sources/site/style.css`, but inside this package the single-file prototype is the maintained artifact.

## Components represented

- `SiteNav.jsx` — top navigation with brand + active state
- `Hero.jsx` — crystal-eye motif, bilingual H1, tagline pair, badges, CTA pair
- `FeatureCard.jsx` — translucent card used in feature grids
- `AxiomCard.jsx` — narrative card with FOL mono line
- `Blockquote.jsx` — left-rule ceremonial quote
- `CodeBlock.jsx` — dark code surface
- `ComparisonTable.jsx` — traditional AI vs. prompt-eng vs. ToneSoul
- `SiteFooter.jsx` — philosophy lines + GitHub credit

Open `index.html` to preview the click-through demo (home → concepts → getting-started).
