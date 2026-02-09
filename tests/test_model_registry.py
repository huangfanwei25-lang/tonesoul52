from tonesoul.council.model_registry import (
    DEFAULT_LLM_MODEL,
    HYBRID_COUNCIL_CONFIG,
    MULTI_MODEL_COUNCIL_CONFIG,
    RULES_ONLY_COUNCIL_CONFIG,
    get_council_config,
    get_perspective_model,
)


def test_get_perspective_model_is_case_insensitive():
    assert get_perspective_model("GUARDIAN") == "gemini-1.5-pro"
    assert get_perspective_model("analyst") == DEFAULT_LLM_MODEL


def test_get_perspective_model_returns_default_for_unknown():
    assert get_perspective_model("unknown_role") == DEFAULT_LLM_MODEL


def test_get_council_config_full_llm_shape():
    config = get_council_config("full_llm")
    assert config["guardian"]["mode"] == "llm"
    assert config["analyst"]["mode"] == "llm"
    assert config["critic"]["mode"] == "llm"
    assert config["advocate"]["mode"] == "llm"
    assert config["axiomatic"]["mode"] == "rules"


def test_get_council_config_rules_only_shape():
    config = get_council_config("rules_only")
    for value in config.values():
        assert value["mode"] == "rules"


def test_get_council_config_rules_alias_shape():
    config = get_council_config("rules")
    for value in config.values():
        assert value["mode"] == "rules"


def test_get_council_config_custom_map_normalizes_keys():
    config = get_council_config("hybrid", custom_map={"GUARDIAN": "gemini-1.5-pro"})
    assert config["guardian"] == {"mode": "llm", "model": "gemini-1.5-pro"}


def test_get_council_config_returns_deep_copy():
    config = get_council_config("full_llm")
    config["guardian"]["model"] = "mutated-model"
    assert MULTI_MODEL_COUNCIL_CONFIG["guardian"]["model"] != "mutated-model"

    hybrid = get_council_config("hybrid")
    hybrid["analyst"]["mode"] = "llm"
    assert HYBRID_COUNCIL_CONFIG["analyst"]["mode"] == "rules"

    rules = get_council_config("rules_only")
    rules["critic"]["mode"] = "llm"
    assert RULES_ONLY_COUNCIL_CONFIG["critic"]["mode"] == "rules"
