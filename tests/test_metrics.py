from tonesoul import poav, tsr_metrics


def test_poav_score_empty():
    result = poav.score("")
    assert result["total"] == 0.0
    assert result["token_count"] == 0.0
    assert result["sentence_count"] == 0.0


def test_poav_score_with_evidence_and_paths():
    text = "Evidence and source in report. See C:\\data\\audit.json and /var/log/app.log."
    result = poav.score(text)
    assert result["keyword_hits"] >= 2.0
    assert result["path_hits"] >= 2.0
    assert result["verifiability"] > 0.0


def test_tsr_score_custom_policy():
    policy = {
        "tension": {
            "base": 0.0,
            "length_weight": 0.0,
            "modal_weight": 0.0,
            "caution_weight": 0.0,
            "punctuation_weight": 0.0,
            "length_tokens": 1.0,
            "modal_hits": 1.0,
            "caution_hits": 1.0,
            "punctuation_hits": 1.0,
        },
        "variability": {
            "unique_ratio_target": 1.0,
            "length_tokens": 1.0,
        },
        "lexicon": {
            "positive": ["go"],
            "negative": ["stop"],
            "strong_modals": [],
            "caution": [],
        },
    }
    result = tsr_metrics.score("go go stop", policy=policy)
    assert result["signals"]["token_count"] == 3
    assert result["tsr"]["S"] == 0.3333
    assert result["tsr"]["S_norm"] == 0.6667
    assert result["tsr"]["R"] == 0.6667


def test_build_tsr_metrics_delta():
    policy = {
        "tension": {
            "base": 0.0,
            "length_weight": 0.0,
            "modal_weight": 0.0,
            "caution_weight": 0.0,
            "punctuation_weight": 0.0,
            "length_tokens": 1.0,
            "modal_hits": 1.0,
            "caution_hits": 1.0,
            "punctuation_hits": 1.0,
        },
        "variability": {
            "unique_ratio_target": 1.0,
            "length_tokens": 1.0,
        },
        "lexicon": {
            "positive": ["go"],
            "negative": ["stop"],
            "strong_modals": [],
            "caution": [],
        },
    }
    baseline = {
        "run_id": "baseline",
        "metrics_path": "baseline.json",
        "tsr": {"T": 0.1, "S": 0.2, "S_norm": 0.6, "R": 0.4},
    }
    payload = tsr_metrics.build_tsr_metrics(
        "go stop",
        run_id="current",
        source_path="source.txt",
        baseline_entry=baseline,
        policy=policy,
    )
    assert payload["delta"]["available"] is True
    assert payload["delta"]["baseline_run_id"] == "baseline"
    assert payload["delta"]["baseline_metrics_path"] == "baseline.json"
