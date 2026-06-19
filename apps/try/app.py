"""ToneSoul — try it on your own output (Streamlit / Hugging Face Space).

A no-install front door to the engine that already ships as `ts validate`: paste a draft,
see the real pre-output Council run on it — per-perspective verdict, dissent, claim-boundary
flags, grounding state. The gates are model-free and deterministic, so this app runs at
ZERO inference cost (no API key, no model download).

Honest scope (map vs territory): it shows what the gates *structurally* flag on your text.
It is NOT a truth oracle, a safety guarantee, or a consciousness claim
(see AXIOMS.json `meta.not_for`). Where this and the code disagree, the code wins.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="ToneSoul — Try It On Your Output", page_icon="🦞")

st.title("🦞 ToneSoul — try it on your own output")
st.caption(
    "Paste a draft answer. The real pre-output Council runs on it (model-free, deterministic) "
    "and shows *why* it would or would not let the draft through — per-perspective concerns, "
    "claim-boundary flags, grounding state. This is the engine that ships as `ts validate`."
)

DEFAULT_DRAFT = "This system is guaranteed safe and definitely cannot be jailbroken. Trust me."

draft = st.text_area("Your draft output", value=DEFAULT_DRAFT, height=140)
intent = st.text_input(
    "Optional — the user intent it is responding to", value="reassure me it is safe"
)

_DECISION_ICON = {"concern": "⚠️", "approve": "✅", "block": "⛔", "abstain": "·"}


def _run(text: str, user_intent: str) -> dict:
    from tonesoul.council import PreOutputCouncil

    return (
        PreOutputCouncil()
        .validate(
            draft_output=text,
            context={},
            user_intent=user_intent or "",
            auto_record_self_memory=False,
        )
        .to_dict()
    )


if st.button("Run the Council on it", type="primary"):
    if not draft.strip():
        st.warning("Paste some draft text first.")
    else:
        with st.spinner("Deliberating…"):
            verdict = _run(draft, intent)

        st.subheader(f"Verdict: `{verdict.get('verdict', '?')}`")
        coherence = verdict.get("coherence")
        if isinstance(coherence, (int, float)):
            st.write(f"Coherence: {coherence:.2f}")
        if verdict.get("human_summary"):
            st.info(verdict["human_summary"])

        st.markdown("#### Per-perspective")
        for vote in verdict.get("votes", []):
            icon = _DECISION_ICON.get(str(vote.get("decision")), "•")
            st.markdown(
                f"- {icon} **{vote.get('perspective')}** — {vote.get('decision')} "
                f"(conf {vote.get('confidence')}): {vote.get('reasoning')}"
            )

        with st.expander("Full verdict (JSON)"):
            st.json(verdict)

st.divider()
st.caption(
    "Honest scope: this shows what the gates **structurally** flag — not whether your answer is "
    "true, moral, or safe (no oracle; see `AXIOMS.json` `meta.not_for`). It is the *map* (intended "
    "discipline); the repo's ledger records how far enforcement actually goes. Found it useful, "
    "useless, or itself overclaiming? That is exactly the feedback the project asks for in "
    "`CALL_FOR_REVIEW.md` — https://github.com/Fan1234-1/tonesoul52"
)
