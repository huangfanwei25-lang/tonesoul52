from tonesoul.tonebridge.trajectory import (
    DirectionChange,
    ResonanceState,
    TrajectoryAnalyzer,
)


def test_context_window_empty_and_prompt_none():
    analyzer = TrajectoryAnalyzer(window_size=3)

    assert analyzer.get_context_window() == []
    assert analyzer.get_context_for_prompt() is None


def test_context_window_respects_window_size_and_prompt_shape():
    analyzer = TrajectoryAnalyzer(window_size=3)

    for idx in range(4):
        analyzer.add_turn(
            user_input=f"user-{idx}",
            ai_response=f"ai-{idx}",
            tone_state="resonance" if idx % 2 == 0 else "tension",
            tone_strength=0.2 + idx * 0.1,
        )

    window = analyzer.get_context_window()
    prompt_context = analyzer.get_context_for_prompt()

    assert [turn.index for turn in window] == [1, 2, 3]
    assert prompt_context == [
        {
            "index": 1,
            "user_input": "user-1",
            "ai_response": "ai-1",
            "tone_state": "tension",
        },
        {
            "index": 2,
            "user_input": "user-2",
            "ai_response": "ai-2",
            "tone_state": "resonance",
        },
        {
            "index": 3,
            "user_input": "user-3",
            "ai_response": "ai-3",
            "tone_state": "tension",
        },
    ]


def test_similarity_heuristics_cover_exact_subset_jaccard_and_empty():
    analyzer = TrajectoryAnalyzer()

    assert analyzer._is_similar("same phrase", "same phrase") is True
    assert analyzer._is_similar("alignment", "ai alignment governance") is True
    assert (
        analyzer._is_similar(
            "alpha beta gamma delta epsilon zeta",
            "alpha beta gamma delta epsilon eta",
        )
        is True
    )
    assert analyzer._is_similar("alpha beta", "gamma delta") is False
    assert analyzer._is_similar("", "gamma delta") is False


def test_detect_loop_and_analyze_circular_logic():
    analyzer = TrajectoryAnalyzer()
    analyzer.add_turn("repeat this", tone_strength=0.6)
    analyzer.add_turn("repeat this again", tone_strength=0.6)
    analyzer.add_turn("repeat this now", tone_strength=0.6)

    loop_detected, loop_count = analyzer.detect_loop("repeat this")
    analysis = analyzer.analyze("repeat this", current_tone_strength=0.6)

    assert loop_detected is True
    assert loop_count >= 2
    assert analysis.loop_detected is True
    assert analysis.direction_change is DirectionChange.CIRCULAR_LOGIC
    assert analysis.resonance_state is ResonanceState.TENSION


def test_analyze_without_history_returns_initial_stable_state():
    analyzer = TrajectoryAnalyzer()

    analysis = analyzer.analyze("hello world", current_tone_strength=0.4)

    assert analysis.shift_magnitude == 0.0
    assert analysis.direction_change is DirectionChange.STABLE
    assert analysis.resonance_state is ResonanceState.RESONANCE
    assert analysis.loop_detected is False


def test_determine_direction_covers_stable_escalating_deescalating_and_abrupt():
    analyzer = TrajectoryAnalyzer()

    assert analyzer._determine_direction(0.4, 0.45, 0.05) is DirectionChange.STABLE
    assert analyzer._determine_direction(0.3, 0.5, 0.2) is DirectionChange.ESCALATING
    assert analyzer._determine_direction(0.5, 0.3, 0.2) is DirectionChange.DE_ESCALATING
    assert analyzer._determine_direction(0.2, 0.85, 0.65) is DirectionChange.ABRUPT_SHIFT


def test_analyze_uses_recent_tension_history_for_resonance_state():
    analyzer = TrajectoryAnalyzer()
    analyzer.add_turn("turn-1", tone_state="tension", tone_strength=0.2)
    analyzer.add_turn("turn-2", tone_state="tension", tone_strength=0.3)
    analyzer.add_turn("turn-3", tone_state="resonance", tone_strength=0.4)

    analysis = analyzer.analyze("turn-4", current_tone_strength=0.55)

    assert analysis.direction_change is DirectionChange.ESCALATING
    assert analysis.resonance_state is ResonanceState.TENSION
    assert analysis.loop_detected is False


def test_reset_clears_history_and_recent_inputs():
    analyzer = TrajectoryAnalyzer()
    analyzer.add_turn("hello")
    analyzer.add_turn("world")

    analyzer.reset()

    assert analyzer.history == []
    assert analyzer.get_context_window() == []
    assert analyzer.detect_loop("hello") == (False, 0)
