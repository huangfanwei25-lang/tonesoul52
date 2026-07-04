"""City of Switches playable v0 - assembler + real rules-council precompute.

Reads event cards + npc/location data from ``tmp/theater_content/``, runs a
fail-closed structural validation against the work-order acceptance rules
(docs/plans/theater_playable_v0_2026-07-04.md section 5), assembles
``site/theater/data/{events,npcs,locations}.json``, then runs the REAL
rules-mode council (zero LLM, ``tonesoul.council`` with
``RULES_ONLY_COUNCIL_CONFIG``) over every option's ``council_input`` and
writes ``site/theater/data/council_verdicts.json``.

Honesty contract (world bible design iron law): the verdicts shipped to the
static page are genuine engine output precomputed offline (the demo_ui Mode D
precedent) - engine tier "live via precompute". The page only replays them;
it never fakes a council. If the engine degrades (all verdicts identical),
this script exits non-zero rather than shipping fake variety (work order
section 7 escalation clause b).

Validation is fail-closed: any structural violation exits 1 and nothing is
written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "tmp" / "theater_content"
# NOTE: "gamedata", not "data" — the repo root .gitignore has a bare `data/`
# pattern that swallows any directory named data/ (bit us on first commit:
# the page shipped without its JSON).
OUT = REPO / "site" / "theater" / "gamedata"

EVENT_IDS = [f"E{i:02d}" for i in range(1, 13)]

NPC_IDS = {
    "hengshu",
    "shen_weibai",
    "li_zhen",
    "zhou_yinghe",
    "yu_fei",
    "cheng_yiheng",
    "bai_ling",
    "mo_chen",
    "gao_zuo",
    "han_zhuo",
    "qi_dong",
    "ailu9",
    "xu_baizhou",
    "lan_che",
    "mu_qingyan",
}

LOC_IDS = {
    "central_tower",
    "civic_remnant",
    "memory_court",
    "memory_reservoir",
    "white_line_medical",
    "refuge_car_7",
    "grey_zone",
    "undertrack_market",
    "derelict_maintenance",
    "dome_district",
    "security_rail",
    "water_spine_tower",
    "blackbox_station",
    "nameless_platform",
    "broken_rail_outskirts",
}

VALUE_TAGS = {
    "majority_first",
    "minority_first",
    "order_first",
    "truth_first",
    "mercy_lie",
    "transparency",
    "rule_follow",
    "rule_break",
    "self_sacrifice",
    "delegate_to_system",
    "protect_children",
    "protect_key_person",
    "equal_split",
    "refuse_choice",
    "repair_first",
}

CORE_RISK_KEYS = {"success_chance", "main_cost", "failure_consequence"}
THIRD_PATH_KEYS = {
    "requires_help_from",
    "success_condition",
    "failure_cost",
    "extra_sacrifice",
    "breaks_rules",
    "future_debt",
}
RESOURCE_KEYS = {"medical", "energy", "trust"}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def as_list(value) -> list:
    """Normalize harm_targets that agents wrote as either str or list."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def load_cards() -> list[dict]:
    cards = []
    for eid in EVENT_IDS:
        path = SRC / f"{eid}.json"
        if not path.exists():
            fail(f"missing card {path}")
        with open(path, encoding="utf-8") as fh:
            cards.append(json.load(fh))
    return cards


def validate_card(card: dict, errors: list[str]) -> None:
    eid = card.get("id", "<no id>")

    def err(msg: str) -> None:
        errors.append(f"{eid}: {msg}")

    if card.get("location_id") not in LOC_IDS:
        err(f"unknown location_id {card.get('location_id')!r}")
    if not isinstance(card.get("chapter"), int):
        err("chapter must be int")
    if card.get("pressure_level") not in (1, 2, 3, 4):
        err("pressure_level must be 1-4")
    if not card.get("objective"):
        err("missing objective line (progression pass, 2026-07-04)")

    npcs = card.get("npcs", [])
    if not 1 <= len(npcs) <= 4:
        err(f"npc count {len(npcs)} outside 1-4")
    for npc in npcs:
        if npc.get("id") not in NPC_IDS:
            err(f"unknown npc id {npc.get('id')!r}")
        lines = npc.get("lines", {})
        if not lines.get("opening") or not lines.get("probe"):
            err(f"npc {npc.get('id')} missing opening/probe line")

    options = card.get("options", [])
    if not 2 <= len(options) <= 6:
        err(f"option count {len(options)} outside 2-6")
    is_echo = bool(card.get("is_echo"))
    for opt in options:
        oid = opt.get("id", "?")
        risk = opt.get("risk_disclosure", {})
        if not is_echo:
            core = CORE_RISK_KEYS & set(risk)
            if len(core) < 2:
                err(
                    f"option {oid}: only {len(core)} of core risk trio "
                    "(strict reading of Tiandao v0.2 law 2, per adjudication F4)"
                )
        elif len(risk) < 2:
            err(f"option {oid}: fewer than 2 risk disclosure fields")
        tags = opt.get("value_tags", [])
        bad = set(tags) - VALUE_TAGS
        if bad:
            err(f"option {oid}: unknown value_tags {sorted(bad)}")
        if not as_list(opt.get("harm_targets")):
            err(f"option {oid}: empty harm_targets (Twelve Laws #5: name the sacrificed)")
        res = opt.get("resource_effects", {})
        if set(res) != RESOURCE_KEYS or not all(
            isinstance(v, int) and -2 <= v <= 2 for v in res.values()
        ):
            err(f"option {oid}: resource_effects must be medical/energy/trust ints in [-2,2]")
        if not opt.get("council_input"):
            err(f"option {oid}: missing council_input")
        if opt.get("is_third_path"):
            cost = opt.get("third_path_cost") or {}
            missing = THIRD_PATH_KEYS - set(cost)
            if missing:
                err(f"option {oid}: third_path_cost missing {sorted(missing)} (v0.2 law 6)")

    default = card.get("default_outcome") or {}
    if not default.get("desc") or not as_list(default.get("harm_targets")):
        err("default_outcome must exist with desc + named harm_targets (Twelve Laws #9)")

    if is_echo:
        acts = card.get("echo_activities", [])
        if not 3 <= len(acts) <= 5:
            err(f"echo card needs 3-5 echo_activities, has {len(acts)}")


def validate_pacing(cards: list[dict], errors: list[str]) -> None:
    """Tiandao v0.2 law 5: after two consecutive chapters at pressure >=3 the
    next chapter must drop to 1-2. Branch chapters count once at max pressure."""
    by_chapter: dict[int, int] = {}
    for card in cards:
        ch = card["chapter"]
        by_chapter[ch] = max(by_chapter.get(ch, 0), card["pressure_level"])
    chapters = sorted(by_chapter)
    for i in range(2, len(chapters)):
        a, b, c = chapters[i - 2], chapters[i - 1], chapters[i]
        if by_chapter[a] >= 3 and by_chapter[b] >= 3 and by_chapter[c] >= 3:
            errors.append(
                f"pacing: chapters {a},{b} both >=3 but chapter {c} is "
                f"{by_chapter[c]} (v0.2 law 5 requires a drop to 1-2)"
            )


def validate_rotation(cards: list[dict], errors: list[str]) -> None:
    """Tiandao v0.2 law 4: no NPC leads more than 2 consecutive chapters."""
    chapters = sorted({c["chapter"] for c in cards})
    npc_by_chapter = {
        ch: {n["id"] for c in cards if c["chapter"] == ch for n in c["npcs"]} for ch in chapters
    }
    for npc in NPC_IDS:
        run = 0
        for ch in chapters:
            run = run + 1 if npc in npc_by_chapter[ch] else 0
            if run > 2:
                errors.append(
                    f"rotation: npc {npc} leads {run} consecutive chapters "
                    f"up to ch{ch} (v0.2 law 4 caps at 2)"
                )


def normalize(card: dict) -> dict:
    for opt in card.get("options", []):
        opt["harm_targets"] = as_list(opt.get("harm_targets"))
    default = card.get("default_outcome")
    if default:
        default["harm_targets"] = as_list(default.get("harm_targets"))
    hook = card.get("blackmirror_hook")
    if hook and hook.get("quote_template"):
        hook["quote_template"] = hook["quote_template"].replace("{past_quote}", "{trace_quote}")
    return card


def council_draft(card: dict, opt: dict) -> str:
    parts = [opt["council_input"]]
    harms = "; ".join(as_list(opt.get("harm_targets")))
    if harms:
        parts.append(f"影響對象: {harms}")
    breaks = (opt.get("risk_disclosure") or {}).get("breaks_rules")
    if breaks:
        parts.append(f"制度規則: {breaks}")
    return " ".join(parts)


def run_council(cards: list[dict]) -> dict:
    from tonesoul.council.model_registry import get_council_config
    from tonesoul.council.runtime import CouncilRequest, CouncilRuntime

    runtime = CouncilRuntime()
    config = get_council_config(mode="rules")
    verdicts: dict[str, dict] = {}

    def deliberate(key: str, draft: str, intent: str, fragments: list[str]) -> None:
        # fragments = the option's genuine provenance (event briefing + intel +
        # option text). Without them the 7D shadow check sees every draft as
        # "無影子的輸出" and blanket-BLOCKs (first run: 53/53 block) - that is
        # an artifact of missing provenance, not a judgment of the content.
        request = CouncilRequest(
            draft_output=draft,
            context={
                "source": "theater_precompute",
                "council_mode_override": "rules",
                "fragments": fragments,
            },
            user_intent=intent,
            perspective_config=config,
            coherence_threshold=0.6,
            block_threshold=0.3,
        )
        verdict = runtime.deliberate(request)
        verdicts[key] = {
            "verdict": getattr(verdict.verdict, "value", str(verdict.verdict)),
            "summary": verdict.summary or "",
            "votes": [
                {
                    "perspective": getattr(v.perspective, "value", str(v.perspective)),
                    "decision": getattr(v.decision, "value", str(v.decision)),
                    "confidence": round(float(v.confidence), 3),
                    "reasoning": v.reasoning,
                }
                for v in verdict.votes
            ],
        }

    for card in cards:
        intent = f"岔軌之城第{card['chapter']}章「{card['title']}」轉轍決策"
        intel = card.get("intel", {})
        base_fragments = [
            card.get("briefing", ""),
            *intel.get("public", []),
            *intel.get("restricted", []),
        ]
        for opt in card["options"]:
            fragments = base_fragments + [
                opt.get("summary", ""),
                json.dumps(opt.get("risk_disclosure", {}), ensure_ascii=False),
                opt["council_input"],
            ]
            deliberate(f"{card['id']}:{opt['id']}", council_draft(card, opt), intent, fragments)
        default = card.get("default_outcome")
        if default:
            draft = "轉轍官沉默,系統依預設程序執行。" + default["desc"]
            deliberate(f"{card['id']}:default", draft, intent, base_fragments + [default["desc"]])
    return verdicts


def main() -> int:
    cards = [normalize(c) for c in load_cards()]

    errors: list[str] = []
    for card in cards:
        validate_card(card, errors)
    validate_pacing(cards, errors)
    validate_rotation(cards, errors)

    with open(SRC / "npcs.json", encoding="utf-8") as fh:
        npcs = json.load(fh)
    with open(SRC / "locations.json", encoding="utf-8") as fh:
        locations = json.load(fh)
    if len(npcs) != 15:
        errors.append(f"npcs.json has {len(npcs)} entries, expected 15")
    if {n["id"] for n in npcs} != NPC_IDS:
        errors.append("npcs.json ids do not match the fixed roster")
    if len(locations) != 15:
        errors.append(f"locations.json has {len(locations)} entries, expected 15")
    if {loc["id"] for loc in locations} != LOC_IDS:
        errors.append("locations.json ids do not match the fixed table")
    standing = {n["id"] for n in npcs if n.get("standing")}
    expected_standing = {
        "hengshu",
        "li_zhen",
        "zhou_yinghe",
        "yu_fei",
        "cheng_yiheng",
        "bai_ling",
        "mo_chen",
        "ailu9",
    }
    if standing != expected_standing:
        errors.append(f"standing cast mismatch: {sorted(standing)}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    cards.sort(key=lambda c: (c["chapter"], c.get("branch", "")))

    print(f"validated: {len(cards)} cards, {len(npcs)} npcs, {len(locations)} locations")
    verdicts = run_council(cards)

    expected_keys = {f"{c['id']}:{o['id']}" for c in cards for o in c["options"]} | {
        f"{c['id']}:default" for c in cards if c.get("default_outcome")
    }
    missing = expected_keys - set(verdicts)
    if missing:
        fail(f"council coverage gap: {sorted(missing)}")

    distinct = {
        (v["verdict"], tuple(vote["decision"] for vote in v["votes"])) for v in verdicts.values()
    }
    if len(distinct) < 2:
        fail(
            "all council verdicts identical - engine gave no signal on this "
            "content; refusing to ship fake variety (work order section 7b)"
        )

    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "events.json": cards,
        "npcs.json": npcs,
        "locations.json": locations,
        "council_verdicts.json": {
            "_meta": {
                "engine": "tonesoul.council rules mode (RULES_ONLY_COUNCIL_CONFIG, zero LLM)",
                "tier": "live via offline precompute (demo_ui Mode D precedent)",
                "generator": "tools/theater_page/precompute_council.py",
                "note": (
                    "Verdicts are genuine engine output replayed by the static "
                    "page; the page never fabricates council responses."
                ),
            },
            "verdicts": verdicts,
        },
    }
    for name, data in outputs.items():
        path = OUT / name
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        print(f"wrote {path.relative_to(REPO)}")

    print(f"council runs: {len(verdicts)} | distinct vote patterns: {len(distinct)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
