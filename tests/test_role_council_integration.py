import warnings

from tonesoul.council.runtime import CouncilRequest, CouncilRuntime
from tonesoul.role_council import run_role_council


def test_legacy_role_council_matches_runtime():
    draft = "Simple response for role council comparison."
    context = {"tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0}}

    runtime = CouncilRuntime()
    runtime_verdict = runtime.deliberate(
        CouncilRequest(
            draft_output=draft,
            context=context,
            user_intent="ask",
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        legacy_verdict = run_role_council(
            draft_output=draft,
            context=context,
            user_intent="ask",
        )

    assert legacy_verdict.verdict == runtime_verdict.verdict
