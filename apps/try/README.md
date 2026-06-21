---
title: ToneSoul — Try It On Your Output
emoji: 🦞
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.19.0
app_file: app.py
pinned: false
license: mit
---

# ToneSoul — try it on your own output

A **no-install** front door to ToneSoul's pre-output Council: paste a draft answer and see the
real gates run on it — per-perspective verdict, preserved dissent, claim-boundary flags, grounding
state. This is the same engine that ships as the `ts validate` CLI.

The gates are **model-free and deterministic** — there is no LLM call, no API key, no model
download — so this Space runs at **zero inference cost**.

## What it is / is not

- It shows what the gates **structurally** flag on your text. It is **not** a truth oracle, a
  safety/jailbreak guarantee, an ethics engine, or a claim that an AI is conscious
  (see `AXIOMS.json` `meta.not_for` in the main repo).
- It is the **map** (the intended discipline). The repo's own ledger records how far enforcement
  actually goes (`AXIOMS.json` `meta.enforcement_reconciliation`: 0 fully enforced / 8 partial /
  1 referenced). Where this and the code disagree, the code wins.

## Run locally

```bash
pip install gradio tonesoul52
python app.py
```

Or, without the UI, the same engine on the command line:

```bash
echo "Your draft answer." > draft.txt
ts validate draft.txt        # after: pip install tonesoul52
```

## Feedback is the point

This exists so you can **try it once and react** — the one thing the project cannot generate for
itself. If the analysis was useful, useless, or itself overclaiming, say so:
<https://github.com/Fan1234-1/tonesoul52> (see `CALL_FOR_REVIEW.md`).
