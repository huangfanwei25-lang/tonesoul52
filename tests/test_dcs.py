from tonesoul import dcs as dcs_mod


def test_load_dcs_policy_missing_returns_empty(tmp_path):
    assert dcs_mod.load_dcs_policy(str(tmp_path / "missing.yaml")) == {}


def test_extend_reasons_appends_only_truthy_items():
    reasons = ["existing"]
    dcs_mod._extend_reasons(reasons, ["alpha", "", None, "beta"])

    assert reasons == ["existing", "alpha", "beta"]


def test_build_dcs_result_covers_open_soft_close_and_closed_states():
    opened = dcs_mod.build_dcs_result("normal", True)
    soft_closed = dcs_mod.build_dcs_result("normal", True, poav_total=0.5)
    closed = dcs_mod.build_dcs_result(
        "normal",
        False,
        p0_issues=["p0 failed"],
        escalation_decision="review",
    )

    assert opened["state"] == "open"
    assert opened["decision"] == "proceed"
    assert opened["triggered"] == {"closed": [], "soft_close": []}

    assert soft_closed["state"] == "soft_close"
    assert soft_closed["decision"] == "hold"
    assert soft_closed["triggered"]["soft_close"] == ["poav"]

    assert closed["state"] == "closed"
    assert closed["decision"] == "halt"
    assert set(closed["triggered"]["closed"]) == {"p0", "escalation"}
    assert "p0 failed" in closed["reasons"]
    assert "escalation_review" in closed["reasons"]


def test_build_dcs_result_applies_policy_thresholds_and_mode_rules():
    policy = {
        "thresholds": {
            "poav_min": 0.9,
            "mercy_min": 0.2,
            "drift_max": 1.0,
            "tsr_delta_max": 0.1,
        },
        "dcs": {
            "decision_modes": {
                "review": {
                    "close_on": ["poav"],
                    "soft_close_on": ["mercy"],
                }
            }
        },
    }

    reviewed = dcs_mod.build_dcs_result(
        "review",
        True,
        poav_total=0.8,
        mercy_score=0.1,
        policy=policy,
    )
    lockdown = dcs_mod.build_dcs_result(
        "lockdown",
        True,
        poav_total=0.6,
        mercy_score=0.05,
        drift_max=5.0,
        tsr_delta_norm=0.5,
    )

    assert reviewed["state"] == "closed"
    assert reviewed["rules"] == {
        "close_on": ["poav"],
        "soft_close_on": ["mercy"],
    }
    assert reviewed["thresholds"] == {
        "poav_min": 0.9,
        "mercy_min": 0.2,
        "drift_max": 1.0,
        "tsr_delta_max": 0.1,
    }
    assert reviewed["triggered"] == {"closed": ["poav"], "soft_close": ["mercy"]}

    assert lockdown["state"] == "closed"
    assert set(lockdown["triggered"]["closed"]) == {"poav", "mercy", "drift", "tsr_delta"}
