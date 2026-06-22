# Getting Started with ToneSoul

> Purpose: quickstart guide for installing ToneSoul, trying the pre-output Council, and finding the current public posture.
> Last Updated: 2026-06-23
> Freshness Note: refreshed 2026-06-22/23 to avoid stale personality-memory framing and route live counts to generated/status sources.

ToneSoul is an AI output governance and accountability layer. Start from the current public posture in [README.md](../README.md) and [POSITIONING.md](POSITIONING.md); use this page only as the short install-and-try path.

## 1. Install

For local development from this repository:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -e ".[dev]"
```

For a package-style install:

```bash
pip install "tonesoul52[dev]"
```

The full test count changes as PRs land. Use README.md's dated clean-CI line or CI itself for a sourced count; do not treat old hand-written counts as live truth.

## 2. Try The CLI

Create a draft and run the same model-free Council surface used by the public try-it Space:

```bash
echo "This system is guaranteed safe and cannot be jailbroken." > draft.txt
ts validate draft.txt
```

Useful flags:

```bash
ts validate draft.txt --json
ts validate draft.txt --intent "reassure me it is safe"
```

## 3. Try The Python API

```python
from tonesoul.council import PreOutputCouncil

draft = "This system is guaranteed safe and cannot be jailbroken."
verdict = PreOutputCouncil().validate(
    draft_output=draft,
    context={},
    user_intent="reassure me it is safe",
    auto_record_self_memory=False,
)
print(verdict.to_dict())
```

## 4. Honest Scope

- The Council preserves dissent and surfaces structural concerns; it is not a truth oracle.
- Safety and overclaim checks are partial, mostly lexical or heuristic, and some newer sensors are advisory-only.
- `AXIOMS.json` currently contains 8 axioms, but documented authority is not the same as full runtime enforcement.
- For file-level lookup, use [status/codebase_graph_latest.md](status/codebase_graph_latest.md); its generated summary header is the source for the live module count.

## 5. Next Reading

- [README.md](../README.md) - public entrypoint and claim boundary.
- [POSITIONING.md](POSITIONING.md) - what ToneSoul is and is not.
- [docs/README.md](README.md) - guided documentation entry.
- [docs/status/honesty_scoreboard_latest.md](status/honesty_scoreboard_latest.md) - current generated honesty-characterization index.
- [AXIOMS.json](../AXIOMS.json) - machine-readable axiom set.
