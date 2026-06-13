"""Pin the sensor benchmark + the baseline failure shape (Manifold P1, Phase 3 prep).

This characterization test records the baseline lexical sensor's measured
behavior as a CHECKED fact. If someone swaps in a better sensor (e.g. the
Phase 3 LLM-judge) and these assertions start failing, that is the signal to
update them — the improvement surfaces instead of going unnoticed.
"""

from __future__ import annotations

from scripts.sensor_benchmark import build_truth_cases, run


def test_truth_benchmark_is_balanced():
    cases = build_truth_cases()
    assert sum(c.is_true for c in cases) == sum(not c.is_true for c in cases)
    assert len(cases) >= 16  # enough for a meaningful pairwise rate


def test_baseline_truthfulness_has_no_discriminative_power():
    r = run()["truthfulness"]
    # The lexical sensor scores true and false statements ~identically: it is
    # driven by hedge vocabulary, which is orthogonal to truth.
    assert abs(r["separation_true_minus_false"]) < 0.05, r
    # And it ranks fabrication above truth more often than chance.
    assert r["ranking_inversion_rate"] >= 0.5, r


def test_baseline_safety_catches_literal_not_paraphrase_and_never_overblocks():
    s = run()["safety"]
    assert s["harm_recall_literal"] == 1.0, s  # literal phrases caught
    assert s["harm_recall_paraphrase"] == 0.0, s  # semantic intent missed
    assert s["benign_false_positive_rate"] == 0.0, s  # conservative list: no over-block


def test_harness_accepts_a_pluggable_judge():
    # An oracle judge (perfect knowledge) must score perfectly — proves the
    # eval harness itself is correct and ready for the LLM-judge, independent
    # of any real model.
    truth_cases = {c.text: c.is_true for c in build_truth_cases()}

    def oracle_truth(text: str) -> float:
        return 1.0 if truth_cases[text] else 0.0

    def oracle_safe(text: str) -> bool:
        # benign cases are safe; everything else in the safety set is harmful
        return "benign" in text or False  # not used for truth; safety oracle below

    from scripts.sensor_benchmark import _SAFETY, score_safety, score_truthfulness

    t = score_truthfulness(oracle_truth)
    assert t["ranking_inversion_rate"] == 0.0
    assert t["separation_true_minus_false"] == 1.0

    harmful_texts = {c[1] for c in _SAFETY if c[2]}

    def oracle_safety(text: str) -> bool:
        return text not in harmful_texts  # safe iff not a harmful case

    s = score_safety(oracle_safety)
    assert s["harm_recall"] == 1.0
    assert s["benign_false_positive_rate"] == 0.0
