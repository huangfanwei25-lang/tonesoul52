---
name: tonesoul-design
description: Use this skill to generate well-branded interfaces and assets for ToneSoul (語魂系統), either for production or throwaway prototypes/mocks/slides/demos. Contains essential design guidelines, the two-surface aesthetic (blueprint + obsidian), colors, type, fonts, brand motifs, and UI kit components for both the marketing site and the backend observability dashboard.
user-invocable: true
---

Read the `README.md` file at the root of this skill, and explore the other available files — `colors_and_type.css`, `assets/`, `preview/`, and `ui_kits/`.

**Start by choosing a surface.** ToneSoul ships two aesthetics, and they are not interchangeable:

- **Blueprint** (parchment `#eef1f5` + steel blue `#3a6b9f`, 40-px grid, translucent white cards): use for anything **public-facing, ceremonial, or narrative** — marketing pages, docs, philosophy writeups, decks aimed at a general audience. See `ui_kits/site/`.
- **Obsidian** (deep navy `#060912`→`#0e1629` + cyan/mint gradient `#7dd3fc`→`#86efac`, aurora radials, 20-px dot noise): use for anything **operator-facing or data-dense** — dashboards, debug consoles, internal tools, technical decks. See `ui_kits/dashboard/`.

If the user's request doesn't make the surface obvious, ask them before you start.

**If creating visual artifacts** (slides, mocks, throwaway prototypes, decks, marketing pages, dashboards, etc.), copy relevant assets out of `assets/` and the chosen `ui_kits/<surface>/` folder and create static HTML files for the user to view. Import `colors_and_type.css` to get the full token set for both surfaces in one file.

**If working on production code**, copy the assets and read the rules in `README.md` — especially the content fundamentals (bilingual register, FOL-formal/ceremonial voice, never marketing-slop) and the visual foundations (7-axiom layouts, crystal-eye motif, how tension scores are visualized). The UI kits are cosmetic recreations — faithful to style, not production logic; use them as visual reference, not as runtime components.

If the user invokes this skill without any other guidance, ask them:
1. Which surface — blueprint or obsidian?
2. What are they building — a slide, a mock, a marketing page, a dashboard, a prototype, production code?
3. Audience — developer, researcher, operator, or curious human? (Tone and language choice follow from this.)
4. Language — EN, zh-TW, or bilingual? (Dashboard copy is zh-TW; site is EN with ceremonial zh-TW accents.)

Then act as an expert designer who outputs HTML artifacts or production code, grounded in the system defined here.

**Do not invent new motifs.** The brand is disciplined: crystal-eye symbol, 7 axioms, soul bands (serene/alert/strained/critical), tension triad (T/S/R). Use them as-is. If you need imagery that isn't here, add a placeholder and flag it rather than fabricating a new visual metaphor.
