# ToneSoul Site

`site/` is the public static marketing and docs surface for ToneSoul.

It is a multi-page HTML/CSS site intended for GitHub Pages or other static hosting. It is not the interactive Next.js app and it is not the operator shell.

## Canonical Files

- `index.html`
- `concepts.html`
- `getting-started.html`
- `story.html`
- `style.css`

## Role Boundary

Use `site/` for:

- public landing pages
- philosophy and concepts pages
- static onboarding and getting-started content
- SEO-facing content and static hosting

Do not use `site/` as:

- the app/chat frontend
- the operator workspace
- a backend observability console

## Neighbor Surfaces

- Interactive app: `apps/web/`
- Operator shell: `apps/dashboard/`
- Static observability playground: `apps/council-playground/`
- Design reference archive: `docs/design/tonesoul-reference/`
