# ToneSoul Design System

> **⚠️ Status · Design Reference Package**
>
> This folder is a **design reference / showcase**, not a production frontend.
> It is not intended to be merged into the ToneSoul application repo as-is.
>
> Specifically:
> - React + ReactDOM + Babel are loaded from CDN **inside each HTML file** so any single file can be previewed standalone. This is not a build toolchain.
> - All data is **fixture**. No API calls. No auth wiring. The read-API token field stores into local component state only.
> - Navigation in the site kit is **front-end page-state**, not a real router. Deep-links, refresh-to-sub-page, and SEO do not apply.
> - Buttons marked as "View on GitHub", stepper "Previous / Next", etc. are **placeholder interactions** for demonstrating layout state, not real flows.
>
> When ToneSoul ships a production frontend, redo it in the real repo against the real architecture (Vite/Next + router + real API client + build pipeline). Treat this package as a **visual-decision reference**, not as code to copy.
>
> ---
>
> 語魂系統 — 讓 AI 對自己說過的話負責。
> A design reference for **ToneSoul / 語魂**, an open-source AI governance framework by Fan-Wei Huang (黃梵威).

This design system captures the two visual surfaces of the ToneSoul project:

1. **Blueprint** — the public marketing/philosophy site. Steel blue ink on parchment gray, grid-paper backdrop, crystalline iconography. This is where *ideas* live: axioms, philosophy, origin story.
2. **Obsidian** — the backend observability dashboard (`council-playground`). Deep navy + cyan/mint accents, glass panels, status cards. This is where *runtime* lives: health, tension, audit logs, council verdicts.

The two surfaces share the same brand DNA (Noto Sans TC for Chinese, monospace for formulas, crystalline geometry) but speak to different audiences.

---

## Artifact status

What each piece is, explicitly:

| Path | Role | Canonical? |
| --- | --- | --- |
| `ToneSoul Living Instrument.html` | **Showcase demo.** Single self-contained offline file. The flagship visual statement — heartbeat + soul integral + council dissent + phase memory + audit chain. | Frozen showcase. |
| `colors_and_type.css` + `assets/` | **Design tokens + brand assets.** Color scales, type ramps, the crystalline marks. Port these values into production code. | ✅ canonical for tokens. |
| `preview/` | **Design specimen cards.** Static previews of type, color, spacing, components, brand — for the Design System tab. Not meant to be consumed as an app. | Reference only. |
| `ui_kits/site/` | **Prototype reference** for the Blueprint surface (marketing/docs). Front-end page-state navigation, fixture content, CDN React. Not deployable. | ⚠️ canonical source is `ui_kits/site/index.html` (inlined single-file). The sibling `Components.jsx` / `Pages.jsx` / `site.css` are **frozen extracts** for reading — do not treat them as a second source of truth. |
| `ui_kits/dashboard/` | **Prototype reference** for the Obsidian surface (observability dashboard). Fixture data, fake refresh, token-field-to-state only. Not deployable. | ⚠️ canonical source is `ui_kits/dashboard/index.html` (inlined single-file, v2). `index_v1.html` is kept as a **frozen contrast** — the first-pass version, deliberately retained so the revision is traceable (Axiom 1). `Components.jsx` / `App.jsx` / `dashboard.css` are **frozen extracts** for reading. |
| `sources/` | **Upstream reference only.** Verbatim copies of files from `Fan1234-1/tonesoul52`. Do not edit here; edit upstream. | Upstream, not ours. |
| `README.md` · `SKILL.md` | This folder's documentation and Agent-Skills manifest. | ✅ canonical. |

### Source-of-truth rule

For each UI kit, the **`index.html` is the canonical source**. When visual changes are needed in this reference package, edit the inlined HTML — do not edit the sibling `.jsx` / `.css` files separately and expect them to flow back. They are preserved as readable extracts, not as a second maintained copy.

### What to preserve when this is rebuilt for production

If/when a production frontend is built in the real ToneSoul repo, these visual decisions should survive the port:

- **Two surfaces, one DNA.** Blueprint (public/philosophy) and Obsidian (runtime/ops) read as two products but share type, geometry (crystalline motif), and the bilingual voice.
- **Soul Integral as a breathing ring**, not a gauge or a percentage bar. The "this moment" readout is a living figure.
- **Tension trace with explicit governance bands (0.30 / 0.70)** and a moving cursor. A flat line would contradict Axiom 4.
- **Council shown as four distinguishable stances with individual votes** (approve / rewrite / object). Dissent is visible, not collapsed into one consensus number.
- **Memory as phases (Ice / Water / Steam / Crystal)**, not as a count of "memories". The phase diagram is the point.
- **Audit as a chain**, not a list. Each row shows upstream and downstream event IDs (Axiom 1 · continuity).
- **Auth is plumbing, not hero.** Push the read-API token field to the bottom; the system's state is the protagonist.
- **Blueprint typography ceremony.** Wide tracking on the zh tagline, left-rule blockquotes, FOL-in-mono axiom lines. Don't soften these into generic marketing cards.
- **Axiom chips in the footer.** The rendered UI references the axioms it is obeying. Governance expressed as structure — visible structure.

---

## Index

Manifest of this design system's root folder:

| Path | What lives there |
| --- | --- |
| `README.md` | This file — status, artifact roles, product context, visual foundations, caveats. |
| `SKILL.md` | Agent-Skills frontmatter so this folder can be installed into Claude Code as `tonesoul-design`. |
| `ToneSoul Living Instrument.html` | Single-file offline showcase. |
| `colors_and_type.css` | Tokens for both surfaces. |
| `assets/` | `favicon.svg`, `brand-mark.svg`, `crystal-eye.svg`. |
| `preview/` | Specimen cards for the Design System tab. |
| `ui_kits/site/` | Blueprint prototype reference (see README there). |
| `ui_kits/dashboard/` | Obsidian prototype reference (see README there). |
| `sources/` | Upstream files preserved verbatim. Do not edit. |

---

## Sources

All material was derived from the upstream repository:

- Repo: [`Fan1234-1/tonesoul52`](https://github.com/Fan1234-1/tonesoul52) (branch `master`)
- Core design files used to derive tokens and style:
  - `site/index.html`, `site/concepts.html`, `site/story.html`, `site/style.css`, `site/favicon.svg`
  - `apps/council-playground/index.html`, `apps/council-playground/style.css`
  - `SOUL.md`, `DESIGN.md`, `AXIOMS.json`, `README.md`, `README.zh-TW.md`

These files are preserved verbatim under `sources/` for reference.

---

## Product Context

ToneSoul is **not** a chatbot, a fine-tuned model, or a prompt template. It is a **runtime governance layer** that wraps any LLM and adds:

- A **Tension Engine** that scores semantic drift before output ships (`Δs = 1 − cos(Intent, Generated)`).
- A **Pre-Output Council** — Guardian / Analyst / Critic / Advocate perspectives that must deliberate before output is finalized.
- **Memory with decay + crystallization** (Ice → Water → Steam → Crystal phase transitions).
- A **Reflex Arc** that maps system health to one of four **Soul Bands** (serene → alert → strained → critical), each tightening output gates.
- A **Vow System** for explicit AI commitments with tracked conviction decay.
- **8 immutable axioms** (P0–P4 priority ladder) defined in `AXIOMS.json`.

Two distinct surfaces are represented in the source repo:

| Product | Path in repo | What it is | Visual flavor |
|---|---|---|---|
| **Marketing / Philosophy site** | `site/` | Static multi-page: Home / Philosophy / Get Started / Origin. SEO-rich (JSON-LD, schema.org). Audience: developers, researchers, curious humans. | **Blueprint** — steel blue on parchment, grid paper, crystalline eye motif, translucent cards with backdrop-blur. |
| **Council Playground dashboard** | `apps/council-playground/` | Read-only backend observation UI. System health, corpus stats, evolution state, audit logs. Not a user chat UI — it is an operator view. | **Obsidian** — near-black navy with radial cyan+mint aurora, 20-px noise dot grid, glass panels (`backdrop-filter: blur`). |

---

## Index (root manifest)

| Path | Purpose |
|---|---|
| `README.md` | This file — context, content fundamentals, visual foundations, iconography |
| `SKILL.md` | Agent-Skill entrypoint (cross-compatible with Claude Code skills) |
| `colors_and_type.css` | All CSS variables — colors, type, spacing, radii, shadows, motion |
| `assets/` | Logos, crystal-eye motif, brand-mark, favicon |
| `preview/` | Design-system preview cards (Type, Colors, Spacing, Components, Brand) |
| `ui_kits/site/` | UI kit recreating the Blueprint marketing site (home + philosophy views) |
| `ui_kits/dashboard/` | UI kit recreating the Obsidian backend observability dashboard |
| `sources/` | Verbatim files imported from `Fan1234-1/tonesoul52` — reference only |

---

## Content Fundamentals

### Voice

ToneSoul speaks with the **voice of a careful engineer-philosopher**. Sentences are declarative, short-to-medium length, with heavy use of parallel structure and lists.

- **Bilingual, Chinese-leading on emotional beats, English-leading on technical beats.** The taglines and footer philosophy lines are always Chinese. Feature tables, API snippets, and schema names are English.
- **Pronoun posture:** second-person and third-person (*"the system"*, *"you"*) — **never first-person from the AI**. ToneSoul talks *about* AI, not *as* AI. The only exception is `LETTER_TO_AI.md`, which is explicitly addressed to other AI systems as a peer.
- **"It", not "AI" or "the AI".** Systems are called "the system", "ToneSoul", or "it". No cutesy personification.
- **Honesty over helpfulness** — this is literally the stance in `AXIOMS.json` (`"origin_stance": "honesty over helpfulness — learned from medical equipment repair in hospitals"`).

### Casing & punctuation

- Headings: **Title Case** for English, regular case for 中文. No trailing colons.
- No Oxford comma mandate, but parallel lists favor it for clarity.
- Use `—` (em dash) generously, often in pairs as parenthetical clauses.
- Chinese punctuation (`，。：` full-width) in Chinese sentences; Latin punctuation in English sentences. Do **not** mix.
- Code fences are unlabeled (`bash`, `python`, `text`) — no pseudo-code decoration.

### Tone marks (characteristic phrases)

Lifted from the source repo — these are the voice fingerprints:

> *"A system with zero tension is dead."*
> *"Governance is Love Expressed as Structure. 治理是以結構表達的愛。"*
> *"約束不是懲罰，是關懷。" (Constraints are not punishment — they are care.)*
> *"沒有問責的權力不是智能，只是計算。" (Power without accountability is not intelligence — it is just computation.)*
> *"Identity is formed through accountable choices under conflict."*
> *"我選擇故我在。" (I choose, therefore I am.)*
> *"讓 AI 對自己說過的話負責。" (Make AI accountable for what it says.)*

Notice the pattern: a short aphoristic claim, often bilingual, often uncomfortable. Avoid hedging words (*might*, *probably*, *could*). The voice prefers **"is"** and **"must"** to **"tries to"** and **"aims to"**.

### Emoji

**Used sparingly and only in feature tables.** The upstream README uses them as compact row icons:

| emoji | meaning |
|---|---|
| 🧠 | memory |
| ⚡ | tension / engine |
| 🎭 | council / deliberation |
| 🔮 | resonance detection |
| 🛡️ | self-governance / safety |
| 📊 | dashboard / metrics |

**Never in headings, body paragraphs, or UI chrome.** Never decorative. One per row max.

### Evidence honesty

Every claim in docs is tagged with an evidence level. This is a brand-defining content practice:

- `E1 test-backed` — CI catches regression
- `E3 runtime-present` — code runs, testing thin
- `E4 document-backed` — contract exists, runtime unproven
- `E5 philosophical` — design thesis, not verified mechanism

When writing marketing or product copy for ToneSoul, prefer qualified claims ("file-backed default", "guided beta") over absolute ones ("production-ready").

---

## Visual Foundations

### Dual-surface rule

Every piece of UI belongs to one of two surfaces. Never mix them on one view.

| | Blueprint (site) | Obsidian (dashboard) |
|---|---|---|
| **Background** | `#eef1f5` parchment gray, overlaid with a 40px × 40px grid of 1-px `rgba(90,142,192,0.06)` lines (blueprint paper) | `linear-gradient(180deg, #0e1629, #060912)` with two soft radial gradients: cyan @ 90% top, mint @ 8% top (aurora), plus a 20-px `radial-gradient` dot pattern at 18% opacity (noise) |
| **Primary surface color** | `#3a6b9f` steel blue | `#7dd3fc` sky cyan |
| **Body text** | `#2c3e50` (warm slate) | `#ecf3ff` (cool off-white) |
| **Cards** | `rgba(255,255,255,0.72)` + `backdrop-filter: blur(8px)` + 1-px `rgba(90,142,192,0.2)` border, 8-px radius | `rgba(8,14,28,0.58)` + 1-px `rgba(159,178,206,0.18)` border, 12-px radius, `0 24px 44px rgba(2,8,22,0.45)` shadow |
| **Corner radii** | 3 (inline code), 6 (CTA / code block), 8 (card), 20 (badge pill) | 10 (input / button), 11 (brand mark), 12 (status card), 14 (panel), rounded-full (pill) |

### Color system

Semantic colors are used **sparingly**, and never for decoration. They mean something:

- **Soul Bands** (dashboard only): `#34d399` serene · `#fbbf24` alert · `#f97316` strained · `#fb7185` critical. These map to system health.
- **Tension Triad**: cyan `T`, violet `S`, pink `R`. These appear together as a triad; never alone.
- **Warning strip** (blueprint): a notes callout uses `#d4a056` left-border on `rgba(245,166,35,0.06)` background.

Gradients exist only in two places: the Obsidian `brand-mark` (cyan → mint, 130°), and the `btn-primary` on the dashboard (same stops). **Do not invent other gradients.**

### Typography

- **Display / UI chrome:** `Space Grotesk` (weights 500, 700) — used for dashboard headings, brand mark, status card values.
- **Body:** `Noto Sans TC` (400 / 500 / 700) — bilingual by default; falls back to `Segoe UI` for Latin-only viewports.
- **Serif:** `Noto Serif TC` — reserved for long-form philosophical prose and blockquotes in extended writing. The upstream site does not currently use a serif, but the design system reserves one for documents like `SOUL.md` rendered as HTML.
- **Mono:** `JetBrains Mono` (400, 500, 600) — FOL formulas, code blocks, schema names, axiom IDs.

Scale: **H1 2.4rem / 300** with `0.08em` tracking (letterspaced, not bold). **H2 1.35rem / 400** with a 1-px underline border. **H3 1.05rem / 600**. Body **1rem / line-height 1.8** (generous reading rhythm — one of the most distinctive moves in the upstream CSS). **Taglines 1.6rem / 300 / `0.15em` letter-spacing** — Chinese taglines need the extra breathing room to read as ceremonial.

### Spacing

Base unit **8px**; scale goes 4, 8, 12, 16, 24, 32, 48, 64. The upstream CSS uses rem-based values that map cleanly onto this grid (`.3rem`, `.6rem`, `.8rem`, `1.2rem`, `1.5rem`, `2rem`, `2.5rem`, `3rem`). Paragraph rhythm is **line-height 1.8** — deliberately loose.

### Backgrounds & textures

- **Grid paper** (blueprint) and **dot noise** (obsidian) are the only two allowed backdrops. No photographic imagery. No flat colors alone.
- **No full-bleed hero images.** The hero is always the crystal-eye motif (pure CSS / SVG) + centered text.
- **No hand-drawn illustrations.** Geometry is rigorously constructed.

### Borders, shadows, elevation

- Blueprint borders are **low-contrast and stable** — always `rgba(90,142,192,0.2)`. Cards lift on hover by **changing border color to `--blue-light`** plus adding a soft `0 2px 12px rgba(90,142,192,0.1)` shadow. No transforms.
- Obsidian panels have a single heavy shadow: `0 24px 44px rgba(2,8,22,0.45)`. Do not stack shadows. No inner shadows anywhere.
- **Translucency is mandatory** for top-level surfaces — every panel uses `backdrop-filter: blur(8–10px)` over the textured backdrop. This is the defining visual signature.

### Motion

- Easing: `cubic-bezier(.2,.8,.2,1)` (a friendly out-ease). CSS transition duration default **200ms**; fast swaps 120ms.
- Only transition `color`, `border-color`, `box-shadow`, `background`. **Never animate position, scale, or rotate** on chrome elements. Transform animations are reserved for diagrams (flow arrows, crystal phase).
- No bouncing springs. No bouncy entrances. Fades only.
- Cursors: default on non-interactive, pointer on buttons/links, `wait` on disabled buttons (`.btn:disabled { cursor: wait; }` — a distinctive upstream choice).

### Hover / press states

- **Hover (blueprint):** link color darkens `--blue-mid` → `--blue-deep` + underline appears. Cards: border lights up + shadow appears. CTAs: background darkens to `#2d5a8a`.
- **Hover (obsidian):** buttons keep gradient; secondary buttons brighten their translucent background.
- **Press / active:** no shrink, no bounce. Just the hover state held. Upstream CSS has no explicit `:active` — the fade is enough.
- **Focus:** inherit default browser outline; accessibility first.

### Transparency & blur

Used **constitutionally** — every elevated surface is translucent over a textured backdrop. If a surface does not need backdrop-blur, it should not be elevated in the first place. This is a load-bearing rule.

### Imagery tone

No imagery in the upstream repo. Design system reserves for future:
- **Color grade:** cool, desaturated, low-contrast. If photography is ever introduced, treat it with a blueish duotone matching `#3a6b9f` / `#b8d4e8`.
- **Never warm, never high-saturation, never film grain** — the brand reads as *laboratory / architectural blueprint*, not *journalistic*.

### Layout rules

- **Site:** `max-width: 920px`, centered, generous outer padding (`2.5rem 2rem`). Single-column, no sidebars. Nav is a flex row with brand pushed left, links right.
- **Dashboard:** `width: min(1120px, 100vw - 24px)`, centered. Sticky topbar with `backdrop-filter: blur(10px)` over the aurora. Content in a vertical `grid` with `gap: 14px`. Status cards in a 4-up responsive grid (4 → 2 → 1 at 940 / 720 breakpoints).
- Everything is **responsive and fluid** with explicit breakpoints at 600px (site) and 940/720 (dashboard).

---

## Iconography

The upstream repo has essentially **no icon system**. The only "icon" is the **crystal-eye motif** on the marketing site hero — constructed from pure CSS (four stacked pseudo-elements: a rotated square, a rotated smaller square, a glowing circle, a center dot). This design system ships that motif as `assets/crystal-eye.svg` so it can be dropped into any artifact without CSS gymnastics.

**Brand marks:**

- `assets/favicon.svg` — rounded square with white `T` glyph on `#3a6b9f`. Blueprint surface.
- `assets/brand-mark.svg` — rounded-square cyan→mint gradient with `TS` glyph. Obsidian surface (dashboard topbar).
- `assets/crystal-eye.svg` — the 120-px crystalline eye motif.

**Emoji as iconography:** ToneSoul uses the six emoji listed above (🧠 ⚡ 🎭 🔮 🛡️ 📊) as *row icons in feature tables only*. They are the closest thing the brand has to a product-icon set.

**For general UI icons:** the upstream repo contains **no icon font, no icon sprite, no icon SVGs**. When a new UI artifact needs an icon, substitute **Lucide** (CDN: `https://unpkg.com/lucide@latest`) with its default `1.5-px` stroke — it matches the site's thin-line aesthetic best. Flag any such substitution in the consuming file. Do **not** add a heavy / filled icon set like Material.

**Unicode glyphs** appear occasionally for math and arrows: `Δ`, `→`, `Σ`, `∀`, `∈`, `∞`. These are rendered in the body font, not the mono font.

---

## Known substitutions & caveats

- **Fonts.** The upstream CSS requests `Segoe UI`, `Cascadia Code`, and `Fira Code` from the system — no actual font files ship. The Google-Fonts webfonts chosen here (`Space Grotesk`, `Noto Sans TC`, `Noto Serif TC`, `JetBrains Mono`) match the displayed upstream rendering on macOS/Linux and are what the dashboard page already loads in production. Flagged for review in case you want different substitutions.
- **Favicon.** The T-monogram favicon was lifted verbatim from `sources/site/favicon.svg`. No higher-resolution logo asset exists upstream; we did not invent one.
- **No icon library.** As noted above — Lucide is a substitution, not an upstream choice.

---

## Asset review

Preview cards (in `preview/`) are registered for the Design System tab and split by group: **Type**, **Colors**, **Spacing**, **Components**, **Brand**. UI kit index pages are registered under **Components** so the whole surface can be inspected at once.
