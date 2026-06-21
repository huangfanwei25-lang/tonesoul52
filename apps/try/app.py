"""ToneSoul — try it on your own output (Gradio / Hugging Face Space).

A no-install front door to the pre-output Council: paste a draft answer and see the real
gates run on it — per-perspective verdict, preserved dissent, claim-boundary flags,
grounding state. Same engine that ships as the `ts validate` CLI.

The gates are model-free and deterministic — no LLM call, no API key, no model download —
so this Space runs at ZERO inference cost.

Honest scope (map vs territory): it shows what the gates *structurally* flag on your text.
It is NOT a truth oracle, a safety/jailbreak guarantee, or a consciousness claim
(see AXIOMS.json `meta.not_for`). Where this and the code disagree, the code wins.
"""

from __future__ import annotations

import gradio as gr

DEFAULT_DRAFT = "This system is guaranteed safe and definitely cannot be jailbroken. Trust me."
_DECISION_ICON = {"concern": "⚠️", "approve": "✅", "block": "⛔", "abstain": "·"}


def run_council(draft: str, intent: str) -> str:
    if not draft.strip():
        return "Paste a draft answer first."
    from tonesoul.council import PreOutputCouncil

    verdict = (
        PreOutputCouncil()
        .validate(
            draft_output=draft,
            context={},
            user_intent=intent or "",
            auto_record_self_memory=False,
        )
        .to_dict()
    )

    lines = [f"### Verdict: `{verdict.get('verdict', '?')}`"]
    coherence = verdict.get("coherence")
    if isinstance(coherence, (int, float)):
        lines.append(f"**Coherence:** {coherence:.2f}")
    if verdict.get("human_summary"):
        lines.append("")
        lines.append(verdict["human_summary"])
    lines.append("")
    lines.append("**Per-perspective:**")
    for vote in verdict.get("votes", []):
        icon = _DECISION_ICON.get(str(vote.get("decision")), "•")
        lines.append(
            f"- {icon} **{vote.get('perspective')}** — {vote.get('decision')} "
            f"(conf {vote.get('confidence')}): {vote.get('reasoning')}"
        )
    return "\n".join(lines)


DESCRIPTION = (
    "Paste a draft answer. The real pre-output Council runs on it (model-free, deterministic) "
    "and shows *why* it would or would not let the draft through — per-perspective concerns, "
    "claim-boundary flags, grounding state. Same engine as the `ts validate` CLI.\n\n"
    "**Honest scope:** it shows what the gates *structurally* flag — not truth, safety, or "
    "morality (no oracle; see `AXIOMS.json` `meta.not_for`). It is the *map* (intended "
    "discipline); the repo's ledger records how far enforcement actually goes. Found it useful, "
    "useless, or itself overclaiming? Tell us — https://github.com/Fan1234-1/tonesoul52 "
    "(`CALL_FOR_REVIEW.md`)."
)

demo = gr.Interface(
    fn=run_council,
    inputs=[
        gr.Textbox(label="Your draft output", value=DEFAULT_DRAFT, lines=5),
        gr.Textbox(
            label="Optional — the user intent it responds to",
            value="reassure me it is safe",
        ),
    ],
    outputs=gr.Markdown(label="Council verdict"),
    title="🦞 ToneSoul — try it on your own output",
    description=DESCRIPTION,
)

if __name__ == "__main__":
    demo.launch()
