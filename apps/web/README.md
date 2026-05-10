# ToneSoul Web

ToneSoul Web is the repository's current interactive frontend.

It is the Next.js application surface for chat, navigator, and app-level UI work. It is not the public static site in `site/`, and it is not the operator shell in `apps/dashboard/`.

## Role Boundary

Use `apps/web` for:

- the interactive product/frontend surface
- Next.js route handlers under `src/app/api/`
- app-level UI, chat orchestration, and browser-facing state

Do not use `apps/web` as:

- the marketing/docs site
- the operator workspace shell
- a static observability playground

## Start

From repo root:

```bash
npm --prefix apps/web install
npm --prefix apps/web run dev
```

Local URL:

```text
http://localhost:3000
```

## Key Paths

- `src/app/page.tsx`
  - main app entry page
- `src/app/api/`
  - browser-to-backend route handlers
- `src/components/`
  - reusable UI components
- `src/lib/`
  - client/runtime helpers such as Soul Engine visualization support

## Verification

From repo root:

```bash
npm --prefix apps/web run build
npm --prefix apps/web run lint
npm --prefix apps/web run test
```
