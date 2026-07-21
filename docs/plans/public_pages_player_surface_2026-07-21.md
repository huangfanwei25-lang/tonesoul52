# Public Pages player surface — 2026-07-21

**Status:** deployed and live-verified through [PR #2](https://github.com/huangfanwei25-lang/tonesoul52/pull/2).

## Decision

The public first release is a static GitHub Pages site:

- / is the ToneSoul public entry surface.
- /theater/ is the playable City of Switches.
- The game is browser-local: save state stays in localStorage unless the player
  chooses memory-only mode, and traces can only be downloaded or viewed locally.

## Boundary

Pages must not collapse player, operator, and audit surfaces into one artifact.

- docs/demo_ui/ is not copied to Pages.
- The theater loads council_player_projection.json, a lossy projection that
  contains only verdict shape, perspective, and decision.
- The player UI renders responsibility cues, not a council vote's raw rationale
  or confidence value.
- The public game has no GitHub Issue trace-submission path.

This is an artifact boundary, not a claim to erase prior public repository
history or make every historic audit record secret. It states what the current
player build delivers to a browser.

## Acceptance checks

1. The Pages workflow assembles only site/.
2. The game regression suite still completes all routes and endings.
3. The projection regression test proves the deployed game data has no
   reasoning fields and the UI cannot render vote.reasoning.
4. Public links, sitemap, canonical URLs, repository links, and share cards
   point to huangfanwei25-lang/tonesoul52.
5. The live URL is only called launched after the Pages deployment succeeds.

## Verification environment note

The isolated checkout starts sparse so it cannot accidentally pull private
memory data into this public-release branch. The first full-suite attempt
therefore lacked the tracked memory Python modules. After those code-only files
were added, pytest resolved its configuration from the parent working tree
because the isolated root pytest.ini was not materialized, then reported a
missing integrations module from that mixed collection.

Before another full-suite attempt, the isolated checkout must include its own
pytest.ini plus the tracked code-only integrations directory. It must continue
to exclude memory JSONL, database, and vector/index data. These collection
failures are recorded as environment setup failures, not evidence about the
player-surface patch.

The next attempt uses a complete code-only checkout instead of adding one
module at a time: all tracked source and test directories needed by the suite
are materialized, while memory data remains excluded by pattern. This changes
the verification method after repeated collection failures; it does not widen
the public release artifact.

That complete source pass reached 408 tests after the Aegis isolation repair,
then stopped because the sparse root omitted AXIOMS.json, a tracked root
configuration input. The final checkout rule therefore includes every tracked
root file from the target commit, rather than a hand-maintained subset, while
still selecting only memory Python code and schemas. No product failure has
been attributed to the player-surface changes during these environment passes.

## Verification results

- `python -m pytest tests/ -x`: 8142 passed.
- `python -m ruff check tonesoul tests`: passed.
- `npm --prefix apps/web run build` and `npm --prefix apps/web run lint`:
  passed.
- The theater's syntax, projection, scene, ending, and full-route Node checks
  passed; the full-route sweep resolved all 47 option paths.
- A real browser loaded `/theater/`, completed the local-storage consent gate,
  and requested `council_player_projection.json` with no console errors.
- A local reproduction of the Pages assembly contained the landing page, game,
  and player projection, while excluding `demo/` and the legacy raw verdict
  payload.

`npm ci` reported 12 advisories in the separate `apps/web` dependency tree.
The lockfile is unchanged and this release does not attempt an unrelated
dependency upgrade; that review remains follow-up work.

## GitHub PR gate follow-up

The first PR run exposed two repository-governance failures before either
checked the product change:

- The dual-track boundary workflow initialized an unavailable legacy memory
  submodule even though the gate only needs Git metadata and changed paths.
  Its checkout now explicitly leaves submodules uninitialized.
- The two feature-branch commits initially lacked the repository's required
  `Agent` and `Trace-Topic` trailers. Both were added while the branch was
  still unmerged, then the local incremental-attribution verifier passed.

The local strict dual-track verifier also passed after the workflow adjustment.
The final authority for this release remains the re-run GitHub checks and the
subsequent Pages deployment.

## Deployment record

- Merge commit: `4a6f0567d82e863bdaf18ea605c4fe78c8e24e90`.
- Pages workflow: [Deploy public site to GitHub Pages](https://github.com/huangfanwei25-lang/tonesoul52/actions/runs/29849599810), passed on its first deployment attempt.
- Live root: <https://huangfanwei25-lang.github.io/tonesoul52/> returned 200 and
  contained the public game entry.
- Live game: <https://huangfanwei25-lang.github.io/tonesoul52/theater/> returned
  200; the player projection JSON also returned 200 and retained only
  `perspective` and `decision` per vote.
- Negative checks: the legacy raw verdict URL and `/demo/` both returned 404.

This record establishes the scope of what was deployed. It does not change the
earlier boundary statement: raw audit materials can still exist in public
repository history or non-Pages paths, and client-delivered story data is not
a secrecy mechanism against browser developer tools.
