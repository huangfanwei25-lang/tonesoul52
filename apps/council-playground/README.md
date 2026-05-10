# ToneSoul Council Playground

ToneSoul Council Playground is a static observability playground.

It is an auxiliary HTML/CSS/JS surface for backend-observation demos and visual experiments. It is not the canonical operator shell and it is not the main interactive frontend.

## Canonical Files

- `index.html`
- `style.css`
- `app.js`

## Role Boundary

Use `apps/council-playground` for:

- static observability demos
- read-only visual experiments around backend health and council state
- lightweight prototype inspection without the Streamlit shell

Do not use `apps/council-playground` as:

- the operator workspace
- the public marketing site
- the canonical product frontend

## If You Need Another Surface

- Operator shell: `apps/dashboard/`
- Interactive app: `apps/web/`
- Public site: `site/`
- CLI observability: `scripts/tension_dashboard.py`
