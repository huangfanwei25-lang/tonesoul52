"""
Generate the agent identity card — 人/事/時/地/物/觀點/狀態 from observable traces.

Why this exists (2026-07-02, owner request): an agent picking this repo up cold should
be able to answer "who has been here, what is in flight, how fresh is the evidence,
where am I, what is the shape of the thing, what stances are already taken, what is
the governance state" from ONE page — without re-deriving it from a dozen artifacts.

Claim boundary (non-negotiable, printed on the card): every field aggregates
OBSERVABLE traces — git trailers, committed artifacts, the governance state file.
The 狀態 section is observable state, NOT a feelings/felt-self claim
(AXIOMS meta.not_for: consciousness-claim). A map of traces is not an inner life.

Sources (all pre-existing; this script computes nothing new):
- 人 who    : Agent: trailers in recent git log
- 事 what   : task.md section headings + docs/plans/*decision_record*.md
- 時 when   : docs/status/status_freshness_latest.json summary
- 地 where  : git branch / HEAD / remote
- 物 things : docs/status/codebase_graph_latest.json summary
- 觀點 stance: AXIOMS.json meta.not_for (standing refusals) + ratified decision records
- 狀態 state : governance_state.json (vows / risk posture / drift) — observable only

Usage:
    python scripts/run_identity_card.py [--agent NAME] [--no-write]
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS_DIR = REPO_ROOT / "docs" / "status"
JSON_FILENAME = "identity_card_latest.json"
MARKDOWN_FILENAME = "identity_card_latest.md"

CLAIM_BOUNDARY = (
    "此卡只聚合可觀察痕跡(git trailers / committed artifacts / state 檔)。"
    "「狀態」是 observable state,不是 felt-self 宣稱(AXIOMS meta.not_for: "
    "consciousness-claim)。痕跡的地圖不等於內在生活。"
)


def _git(args: list[str], repo_root: Path) -> str:
    try:
        return (
            subprocess.run(["git", *args], cwd=repo_root, capture_output=True, check=True)
            .stdout.decode("utf-8", errors="replace")
            .strip()
        )
    except (subprocess.CalledProcessError, OSError):
        return ""


def collect_git_info(repo_root: Path) -> dict:
    trailers = _git(["log", "-50", "--format=%(trailers:key=Agent,valueonly)"], repo_root)
    agents: dict[str, int] = {}
    for line in trailers.splitlines():
        name = line.strip()
        if name:
            agents[name] = agents.get(name, 0) + 1
    return {
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root),
        "head": _git(["rev-parse", "--short", "HEAD"], repo_root),
        "remote": _git(["remote", "get-url", "origin"], repo_root),
        "recent_agents": agents,
    }


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _task_headings(repo_root: Path, limit: int = 6) -> list[str]:
    task = repo_root / "task.md"
    if not task.exists():
        return []
    heads = []
    for line in task.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("## "):
            heads.append(line[3:].strip())
        if len(heads) >= limit:
            break
    return heads


def _decision_records(repo_root: Path) -> list[str]:
    plans = repo_root / "docs" / "plans"
    if not plans.exists():
        return []
    return sorted(p.name for p in plans.glob("*decision_record*.md"))


def build_card(
    repo_root: Path = REPO_ROOT,
    *,
    now: datetime | None = None,
    agent: str = "",
    git_info: dict | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    git_info = git_info if git_info is not None else collect_git_info(repo_root)

    freshness = _read_json(repo_root / "docs" / "status" / "status_freshness_latest.json")
    graph = _read_json(repo_root / "docs" / "status" / "codebase_graph_latest.json")
    governance = _read_json(repo_root / "governance_state.json")
    axioms = _read_json(repo_root / "AXIOMS.json")

    not_for = []
    if isinstance(axioms, dict):
        not_for = list((axioms.get("meta") or {}).get("not_for") or [])

    tension_history = (governance or {}).get("tension_history") or []
    last_tension = tension_history[-1] if tension_history else None

    return {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "scripts/run_identity_card.py",
        "claim_boundary": CLAIM_BOUNDARY,
        "who": {
            "current_agent": agent or "(not given — pass --agent)",
            "recent_agents_from_git_trailers": git_info.get("recent_agents", {}),
        },
        "what": {
            "task_md_headings": _task_headings(repo_root),
            "decision_records": _decision_records(repo_root),
        },
        "when": {
            "evidence_freshness": (freshness or {}).get("summary"),
            "freshness_generated_at": (freshness or {}).get("generated_at"),
            "note": None if freshness else "status_freshness_latest.json not available",
        },
        "where": {
            "branch": git_info.get("branch", ""),
            "head": git_info.get("head", ""),
            "remote": git_info.get("remote", ""),
        },
        "things": {
            "codebase_graph_summary": (graph or {}).get("summary"),
            "god_nodes": len((graph or {}).get("god_nodes") or []),
            "graph_generated_at": (graph or {}).get("generated_at"),
            "note": None if graph else "codebase_graph_latest.json not available",
        },
        "stances": {
            "standing_refusals_meta_not_for": not_for,
            "ratified_or_pending_decision_records": _decision_records(repo_root),
        },
        "observable_state": {
            "active_vows": len((governance or {}).get("active_vows") or []),
            "risk_posture": (governance or {}).get("risk_posture"),
            "soul_integral": (governance or {}).get("soul_integral"),
            "baseline_drift": (governance or {}).get("baseline_drift"),
            "last_tension_entry": last_tension,
            "state_last_updated": (governance or {}).get("last_updated"),
            "note": (
                "observable state only — not feelings"
                if governance
                else "governance_state.json not available"
            ),
        },
    }


def _render_markdown(card: dict) -> str:
    who = card["who"]
    agents = (
        ", ".join(f"{k}×{v}" for k, v in sorted(who["recent_agents_from_git_trailers"].items()))
        or "—"
    )
    state = card["observable_state"]
    freshness = card["when"]["evidence_freshness"] or {}
    lines = [
        "# Identity Card — 自我索引卡",
        "",
        f"- generated_at: {card['generated_at']}",
        f"> {card['claim_boundary']}",
        "",
        f"**人 who** — 現任 `{who['current_agent']}`;近 50 commit 的 agent 足跡:{agents}",
        "",
        "**事 what** — task.md 現行段落:" + ("、".join(card["what"]["task_md_headings"]) or "—"),
        "",
        "**時 when** — 證據保鮮:"
        + (
            f"fresh {freshness.get('fresh', '?')} / stale-assertive"
            f" {freshness.get('stale_assertive', '?')}(freshness 檔 {card['when']['freshness_generated_at']})"
            if freshness
            else "(無 freshness 檔)"
        ),
        "",
        f"**地 where** — `{card['where']['branch']}` @ `{card['where']['head']}` → {card['where']['remote']}",
        "",
        "**物 things** — codebase graph:"
        + (
            f"{json.dumps(card['things']['codebase_graph_summary'], ensure_ascii=False)}"
            f",god_nodes={card['things']['god_nodes']}(圖 {card['things']['graph_generated_at']})"
            if card["things"]["codebase_graph_summary"]
            else "(無 graph 檔)"
        ),
        "",
        "**觀點 stances** — 常設拒絕(meta.not_for):"
        + (", ".join(card["stances"]["standing_refusals_meta_not_for"]) or "—")
        + ";決策記錄:"
        + (", ".join(card["stances"]["ratified_or_pending_decision_records"]) or "—"),
        "",
        "**狀態 state(observable,非 feelings)** — "
        + f"vows={state['active_vows']},risk={json.dumps(state['risk_posture'], ensure_ascii=False)},"
        + f"drift={json.dumps(state['baseline_drift'], ensure_ascii=False)},更新於 {state['state_last_updated']}",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the agent identity card.")
    parser.add_argument("--agent", default="", help="Current agent name for the 人 section.")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    card = build_card(agent=args.agent)
    if not args.no_write:
        (STATUS_DIR / JSON_FILENAME).write_text(
            json.dumps(card, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (STATUS_DIR / MARKDOWN_FILENAME).write_text(
            _render_markdown(card), encoding="utf-8", newline="\n"
        )
    print(
        f"identity_card generated_at={card['generated_at']} "
        f"agents={len(card['who']['recent_agents_from_git_trailers'])} "
        f"vows={card['observable_state']['active_vows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
