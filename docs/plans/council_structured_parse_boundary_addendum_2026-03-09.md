# Council Structured Parse Boundary Addendum (2026-03-09)

> Purpose: record the structured-parse boundary fix that prevents council fallback parsing from overriding valid JSON votes.
> Last Updated: 2026-03-23

## Problem

The council perspective seam had two parsing modes:

- structured JSON parse
- keyword-based text fallback

That fallback is necessary for weaker models, but the boundary was wrong.

If a response contained one valid JSON object and then stray brace-bearing text such as `{OBJECT}`, the old extraction path could fail to isolate the valid object. Once structured parsing returned `None`, the whole response dropped into the fallback parser, and the stray `OBJECT` token could override the real structured decision.

That means a response whose JSON said `APPROVE` could be reinterpreted as `OBJECT`.

## Why This Matters

This is not only an observability or typing issue. It changes runtime behavior:

- one perspective vote can flip
- the council verdict can change
- a request can be blocked or escalated for the wrong reason

## Fix Scope

This phase deliberately stayed narrow:

- keep text fallback for genuinely non-JSON outputs
- do not redesign the external council verdict payload
- only tighten the structured-parse boundary

The change was to replace greedy JSON-object extraction with balanced object extraction in `tonesoul/safe_parse.py`.

## Guardrail

When a runtime seam supports both structured output and fuzzy fallback:

- a valid structured object must always win
- fallback should trigger only when no valid structured payload can be recovered

Otherwise the fallback parser stops being a safety net and becomes a silent override path.
