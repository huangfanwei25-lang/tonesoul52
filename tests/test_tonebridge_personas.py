from __future__ import annotations

from tonesoul.tonebridge import personas as module


def test_persona_config_to_prompt_section_contains_mode_and_patterns() -> None:
    config = module.PersonaConfig(
        mode=module.PersonaMode.ENGINEER,
        keywords=["alpha", "beta"],
        forbidden=["gamma"],
        style="structured",
        sentence_patterns=["1. step", "2. verify"],
        anti_loop_trigger=True,
    )

    section = config.to_prompt_section()

    assert "Engineer" in section
    assert "alpha" in section and "beta" in section
    assert "gamma" in section
    assert '"1. step"' in section
    assert "structured" in section


def test_detect_triggers_reads_keywords_and_context_flags() -> None:
    switcher = module.PersonaSwitcher()

    triggers = switcher._detect_triggers(
        "請幫我修 Python API bug",
        context={
            "boundary_violated": True,
            "loop_detected": True,
            "logic_error": True,
            "tone_strength": 0.8,
            "safety_risk": True,
            "emotional_tone": "tense",
        },
    )

    assert triggers["boundary_violation"] == 1.0
    assert triggers["loop_detected"] == 1.0
    assert triggers["logic_error"] == 0.8
    assert triggers["high_tension"] == 0.8
    assert triggers["safety_concern"] == 0.9
    assert triggers["technical_question"] == 0.7
    assert triggers["emotional_exploration"] == 0.7


def test_calculate_persona_scores_normalizes_weights() -> None:
    switcher = module.PersonaSwitcher()

    scores = switcher._calculate_persona_scores(
        {
            "boundary_violation": 1.0,
            "technical_question": 0.5,
        }
    )

    assert round(sum(scores.values()), 6) == 1.0
    assert scores[module.PersonaMode.GUARDIAN] > scores[module.PersonaMode.ENGINEER]
    assert scores[module.PersonaMode.PHILOSOPHER] == 0.0


def test_evaluate_defaults_to_resonance_mapping_without_triggers() -> None:
    switcher = module.PersonaSwitcher()

    philosopher, _, philosopher_conf = switcher.evaluate(
        "", resonance_state="resonance", context={}
    )
    engineer, _, engineer_conf = switcher.evaluate("", resonance_state="tension", context={})
    guardian, _, guardian_conf = switcher.evaluate("", resonance_state="conflict", context={})

    assert philosopher is module.PersonaMode.PHILOSOPHER
    assert engineer is module.PersonaMode.ENGINEER
    assert guardian is module.PersonaMode.GUARDIAN
    assert philosopher_conf == 1.0
    assert engineer_conf == guardian_conf == 0.6


def test_evaluate_selects_engineer_for_technical_input() -> None:
    switcher = module.PersonaSwitcher()

    persona, reasoning, confidence = switcher.evaluate(
        "How do I debug this Python API bug?",
        context={},
    )

    assert persona is module.PersonaMode.ENGINEER
    assert "technical_question" in reasoning
    assert confidence > 0.5


def test_evaluate_tracks_switch_history_and_inherited_memory() -> None:
    switcher = module.PersonaSwitcher()

    first, _, _ = switcher.evaluate("", resonance_state="resonance", context={})
    second, _, _ = switcher.evaluate(
        "How do I fix this API bug?",
        resonance_state="resonance",
        context={},
    )

    assert first is module.PersonaMode.PHILOSOPHER
    assert second is module.PersonaMode.ENGINEER
    history = switcher.get_switch_history()
    assert len(history) == 1
    assert history[0]["from"] == "Philosopher"
    assert history[0]["to"] == "Engineer"
    assert switcher._inherited_memory["Philosopher"]["inherited"] is True
    assert switcher.get_current_persona() is module.PersonaMode.ENGINEER


def test_get_transition_prompt_returns_known_and_unknown_transitions() -> None:
    switcher = module.PersonaSwitcher()

    known = switcher.get_transition_prompt(
        module.PersonaMode.PHILOSOPHER,
        module.PersonaMode.ENGINEER,
    )
    unknown = switcher.get_transition_prompt(
        module.PersonaMode.GUARDIAN,
        module.PersonaMode.GUARDIAN,
    )

    assert known
    assert unknown == ""


def test_get_persona_from_resonance_handles_known_and_unknown_values() -> None:
    assert module.get_persona_from_resonance("resonance") is module.PersonaMode.PHILOSOPHER
    assert module.get_persona_from_resonance("tension") is module.PersonaMode.ENGINEER
    assert module.get_persona_from_resonance("conflict") is module.PersonaMode.GUARDIAN
    assert module.get_persona_from_resonance("unknown") is module.PersonaMode.PHILOSOPHER


def test_evaluate_persona_uses_global_switcher(monkeypatch) -> None:
    fresh = module.PersonaSwitcher()
    monkeypatch.setattr(module, "_persona_switcher", fresh)

    persona, reasoning, confidence = module.evaluate_persona(
        "How do I fix this API bug?",
        resonance_state="resonance",
        context={},
    )

    assert persona is module.PersonaMode.ENGINEER
    assert "technical_question" in reasoning
    assert confidence > 0.5


def test_build_hardened_prompt_adds_anti_loop_for_engineer_only() -> None:
    engineer_prompt = module.build_hardened_prompt("tension", loop_detected=True)
    philosopher_prompt = module.build_hardened_prompt("resonance", loop_detected=True)

    assert "Engineer" in engineer_prompt
    assert "Anti-Loop" in engineer_prompt
    assert "Philosopher" in philosopher_prompt
    assert "Anti-Loop" not in philosopher_prompt


def test_generate_internal_monologue_prompt_includes_input_and_analysis() -> None:
    prompt = module.generate_internal_monologue_prompt(
        resonance_state="tension",
        trajectory_analysis={"direction_change": "narrowing", "loop_detected": True},
        user_input="How do I fix this bug?",
    )

    assert "How do I fix this bug?" in prompt
    assert "narrowing" in prompt
    assert "tension" in prompt


def test_navigator_response_to_dict_serializes_persona_mode() -> None:
    response = module.NavigatorResponse(
        internal_monologue="think",
        deep_motive="help",
        collapse_radar={"risk_level": "safe"},
        navigation_system={"strategy": "steady"},
        direct_response={"text": "answer"},
        suggested_user_replies=[{"text": "ok"}],
        persona_mode=module.PersonaMode.GUARDIAN,
    )

    payload = response.to_dict()

    assert payload["persona_mode"] == "Guardian"
    assert payload["direct_response"]["text"] == "answer"


def test_build_navigation_prompt_includes_json_contract_and_user_input() -> None:
    prompt = module.build_navigation_prompt(
        user_input="Review the architecture",
        trajectory_analysis={"resonance_state": "tension", "loop_detected": False},
        history_context=["earlier answer"],
    )

    assert "Review the architecture" in prompt
    assert '"internal_monologue"' in prompt
    assert '"direct_response"' in prompt
    assert "Engineer" in prompt
