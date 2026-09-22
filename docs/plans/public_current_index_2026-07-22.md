# Public Current Index v0 — implementation plan

> Status: owner-authorized implementation plan (2026-07-22)
> Scope: public discovery and routing; no new axiom, identity claim, or runtime capability
> Base reviewed: `892d2dcf82069046c4d2d06723762ac7fe503b20`

## Problem

ToneSoul already has searchable essays, repositories, a dataset, a static site,
and an interactive app. Those traces do not currently share one public answer to
"which surface describes the project now?" GitHub Pages and Vercel also present
different roles without a stable machine-readable routing boundary.

The missing artifact is not more memory. It is a small public projection that
routes a reader to current evidence while keeping historical traces visible.

## Decision

- GitHub Pages remains the canonical public documentation and SEO origin.
- `/current/` is the human-readable routing projection.
- `/current.json` is the equivalent machine-readable projection.
- The interactive Vercel application remains a separate, non-authoritative
  product surface; it must not host a second copy of the current index.
- The index is derived and read-only. It does not outrank the sources it links.

Authority remains separated by purpose:

1. code and tests describe currently observable repository behavior;
2. `README.md`, `DESIGN.md`, `AXIOMS.json`, and architecture contracts describe
   reviewed intent and specification;
3. dated generated status files describe point-in-time, noncanonical measurements.

Here, "current" means "selected by this dated routing projection." It is not a
governance, implementation, verification, or lifecycle status. A historical
surface may be called `superseded` only when an explicit replacement event and
successor source exist.

## Machine contract

`site/current.json` is a closed, allowlisted document with these top-level fields:

- `$schema`
- `format`
- `artifact_type`
- `as_of`
- `reviewed_revision`
- `canonical`
- `projection`
- `project`
- `scope`
- `sources`
- `source_routes`
- `entrypoints`
- `known_limits`
- `open_tensions`
- `history`
- `does_not_claim`
- `change_conditions`

Each source route answers one orientation question with a bounded summary,
source references, and caveats. It does not classify a subject or record an
event. Each `projection_role` describes how a source is used by this index; it
does not redefine the repository's document-authority taxonomy or imply
maturity or authority status. The projection carries no
honesty score, soul score, hidden reasoning, or duplicated authority status.
Cross-repository change events remain the responsibility of Accountable
Dialogue's `change-case-v0`; this index does not become another event ledger.

## Public/private projection boundary

The public index may include already-public repository, site, essay, game, and
dataset links. It must exclude private Memory locations and content, local paths,
raw dialogue, hidden/internal reasoning, system prompts, credentials, financial
or hardware context, real private thresholds, deep red-team payloads,
auto-patching configuration, and player-hidden story information.

## Phases

### Phase 1: Contract

- Record the routing and authority boundary.
- Add a bounded active short board to `task.md`.

**Success:** the artifact's role and non-goals are explicit before code changes.

### Phase 2: Red tests

- Add a standard-library static-surface contract test.
- Prove the baseline fails because `/current/` and `/current.json` do not exist.

**Success:** absence, metadata, discovery, structure, and privacy tests fail for
the expected reason.

### Phase 3: Minimal public projection

- Add `site/current/index.html` and `site/current.json`.
- Link the human route from the Pages home, root READMEs, and sitemap.
- Reuse the existing static visual language without adding a framework or generator.

**Success:** the human and machine views agree on their canonical pair and scope.

### Phase 4: Product-surface routing

- Add only a visible outbound link from the interactive app to `/current/`.
- Correct stale public repository links touched by that app surface.
- Do not duplicate the current JSON or page in Next.js.

**Success:** the application identifies the public orientation surface without
claiming to be it.

### Phase 5: Verification and publication

- Run targeted tests, the full Python suite, Ruff, web tests, lint, and build.
- Push a feature branch and open a draft PR.
- After owner-approved merge and Pages deployment, verify both URLs live before
  changing the GitHub repository homepage.

**Success:** local and remote checks pass; merge and homepage mutation remain
human review gates.

## Non-goals

- no deletion or rewriting of old articles;
- no promise that search engines will rank or retain the page;
- no public import from private Memory;
- no new memory engine, database, telemetry service, or model training;
- no broad Vercel SEO redesign in this slice;
- no claim that a public index creates shared identity across models.
