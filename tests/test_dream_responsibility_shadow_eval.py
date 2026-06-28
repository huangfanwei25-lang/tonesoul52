from __future__ import annotations

from tools.probe.dream_responsibility_shadow_eval import SCENARIOS, evaluate_scenarios


def test_shadow_eval_all_scenarios_match_expected() -> None:
    report, failures = evaluate_scenarios()
    assert failures == 0
    assert "Dream Responsibility Shadow Eval" in report


def test_shadow_eval_exercises_deny_cases_not_only_allow() -> None:
    # a self-authored "0 deny" baseline would be the self-authored-test trap; require deny coverage
    deny = [s for s in SCENARIOS if s[2] is False]
    allow = [s for s in SCENARIOS if s[2] is True]
    assert deny, "baseline must include expected-deny scenarios"
    assert allow, "baseline must include expected-allow scenarios"


def test_shadow_eval_report_states_observe_only_boundary() -> None:
    report, _ = evaluate_scenarios()
    assert "OBSERVE-ONLY" in report
    assert "NOT enforcement" in report
    assert "non-bypassable" in report
