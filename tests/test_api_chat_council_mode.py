from types import SimpleNamespace

from apps.api.server import app


def _client():
    app.config["TESTING"] = True
    return app.test_client()


def _mock_pipeline(result_store: dict):
    class _Pipeline:
        def process(self, **kwargs):
            result_store["kwargs"] = kwargs
            return SimpleNamespace(
                response="ok",
                council_verdict={},
                tonebridge_analysis={},
                inner_narrative="",
                intervention_strategy="",
                internal_monologue="",
                persona_mode="",
                trajectory_analysis={},
                self_commits=[],
                ruptures=[],
                emergent_values=[],
            )

    return _Pipeline()


def test_chat_forwards_council_mode_and_perspective_config(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={
            "message": "hello",
            "council_mode": "full_llm",
            "perspective_config": {"guardian": {"mode": "rules"}},
        },
    )
    assert response.status_code == 200
    kwargs = captured["kwargs"]
    assert kwargs["council_mode"] == "full_llm"
    assert kwargs["perspective_config"] == {"guardian": {"mode": "rules"}}


def test_chat_normalizes_rules_only_alias(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={
            "message": "hello",
            "council_mode": "rules_only",
        },
    )
    assert response.status_code == 200
    kwargs = captured["kwargs"]
    assert kwargs["council_mode"] == "rules"


def test_chat_rejects_invalid_council_mode_value():
    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "council_mode": "unknown"},
    )
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid council_mode"


def test_chat_rejects_invalid_perspective_config_shape():
    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "perspective_config": {"guardian": "rules"}},
    )
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid perspective_config"


def test_chat_rejects_invalid_execution_profile_value():
    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "execution_profile": "fast_mode"},
    )
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid execution_profile"


def test_chat_defaults_to_interactive_profile_and_rules_mode(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["execution_profile"] == "interactive"
    kwargs = captured["kwargs"]
    assert kwargs["council_mode"] == "rules"


def test_chat_engineering_profile_defaults_to_full_llm_mode(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "execution_profile": "engineering"},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["execution_profile"] == "engineering"
    kwargs = captured["kwargs"]
    assert kwargs["council_mode"] == "full_llm"


def test_chat_elisa_context_infers_engineering_profile(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={
            "message": "hello",
            "elisa_context": {"source": "elisa_ide"},
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["execution_profile"] == "engineering"
    kwargs = captured["kwargs"]
    assert kwargs["council_mode"] == "full_llm"


def test_chat_explicit_council_mode_overrides_execution_profile_default(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={
            "message": "hello",
            "execution_profile": "engineering",
            "council_mode": "rules",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["execution_profile"] == "engineering"
    kwargs = captured["kwargs"]
    assert kwargs["council_mode"] == "rules"


def test_chat_interactive_profile_defaults_full_analysis_false(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "execution_profile": "interactive"},
    )

    assert response.status_code == 200
    kwargs = captured["kwargs"]
    assert kwargs["full_analysis"] is False


def test_chat_engineering_profile_defaults_full_analysis_true(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={"message": "hello", "execution_profile": "engineering"},
    )

    assert response.status_code == 200
    kwargs = captured["kwargs"]
    assert kwargs["full_analysis"] is True


def test_chat_explicit_full_analysis_overrides_profile_default(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post(
        "/api/chat",
        json={
            "message": "hello",
            "execution_profile": "engineering",
            "full_analysis": False,
        },
    )

    assert response.status_code == 200
    kwargs = captured["kwargs"]
    assert kwargs["full_analysis"] is False


def test_chat_exposes_default_semantic_fields_when_pipeline_omits_them(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["semantic_contradictions"] == []
    assert payload["semantic_graph_summary"] == {}
    assert payload["dispatch_trace"] == {}
    deliberation = payload.get("deliberation")
    assert isinstance(deliberation, dict)
    assert deliberation["semantic_contradictions"] == []
    assert deliberation["semantic_graph_summary"] == {}
    assert deliberation["visual_chain_snapshot"] == {}


def test_chat_exposes_compressed_brief_fields_with_sparse_pipeline_data(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    governance_brief = payload.get("governance_brief")
    life_entry_brief = payload.get("life_entry_brief")

    assert isinstance(governance_brief, dict)
    assert governance_brief["verdict"] == "unknown"
    assert governance_brief["responsibility_tier"] == "unknown"
    assert governance_brief["uncertainty_band"] == "unknown"
    assert governance_brief["coherence"] is None
    assert governance_brief["soul_passed"] is True
    assert governance_brief["contradiction_count"] == 0
    assert isinstance(governance_brief["crystal_freshness"], dict)
    assert "total_crystals" in governance_brief["crystal_freshness"]

    assert isinstance(life_entry_brief, dict)
    assert life_entry_brief["response_summary"] == "ok"
    assert life_entry_brief["inner_intent"] == "Unspecified"
    assert life_entry_brief["strategy"] == "direct_response"
    assert life_entry_brief["self_commit_count"] == 0
    assert life_entry_brief["rupture_count"] == 0
    assert life_entry_brief["emergent_value_count"] == 0


def test_chat_exposes_compressed_brief_fields_with_rich_pipeline_data(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    class _Pipeline:
        def process(self, **kwargs):
            return SimpleNamespace(
                response="Provide a bounded plan with one rollback checkpoint and accountability logs.",
                council_verdict={
                    "verdict": "refine",
                    "coherence": 0.66,
                    "responsibility_tier": "tier-2",
                    "uncertainty_band": "medium",
                    "summary": "Needs one rollback checkpoint before execution.",
                    "votes": [
                        {
                            "perspective": "analyst",
                            "decision": "concern",
                            "confidence": 0.82,
                            "reasoning": "Rollback condition should be explicit.",
                        }
                    ],
                },
                tonebridge_analysis={
                    "motive_prediction": {
                        "likely_motive": "Need a safe execution path",
                    }
                },
                inner_narrative="",
                intervention_strategy="clarify_then_commit",
                internal_monologue="",
                persona_mode="architect",
                trajectory_analysis={"state": "stabilizing"},
                self_commits=[{"id": "s1"}],
                ruptures=[{"id": "r1"}],
                emergent_values=[{"id": "v1"}, {"id": "v2"}],
                semantic_contradictions=[{"found": True, "description": "minor mismatch"}],
                semantic_graph_summary={"total_nodes": 4},
                dispatch_trace={"state": "B", "mode": "tension"},
            )

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    governance_brief = payload.get("governance_brief")
    life_entry_brief = payload.get("life_entry_brief")

    assert governance_brief["verdict"] == "refine"
    assert governance_brief["responsibility_tier"] == "tier-2"
    assert governance_brief["uncertainty_band"] == "medium"
    assert governance_brief["coherence"] == 0.66
    assert governance_brief["soul_passed"] is False
    assert governance_brief["contradiction_count"] == 1
    assert governance_brief["strategy"] == "clarify_then_commit"
    assert governance_brief["dispatch_state"] == "B"
    assert isinstance(governance_brief["crystal_freshness"], dict)

    assert life_entry_brief["response_summary"].startswith("Provide a bounded plan")
    assert life_entry_brief["inner_intent"] == "Need a safe execution path"
    assert life_entry_brief["strategy"] == "clarify_then_commit"
    assert life_entry_brief["persona_mode"] == "architect"
    assert life_entry_brief["trajectory_label"] == "stabilizing"
    assert life_entry_brief["self_commit_count"] == 1
    assert life_entry_brief["rupture_count"] == 1
    assert life_entry_brief["emergent_value_count"] == 2


def test_chat_exposes_semantic_fields_when_pipeline_provides_them(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    class _Pipeline:
        def process(self, **kwargs):
            return SimpleNamespace(
                response="ok",
                council_verdict={},
                tonebridge_analysis={},
                inner_narrative="",
                intervention_strategy="",
                internal_monologue="",
                persona_mode="",
                trajectory_analysis={},
                self_commits=[],
                ruptures=[],
                emergent_values=[],
                semantic_contradictions=[{"found": True, "description": "test"}],
                semantic_graph_summary={"total_nodes": 2, "contradictions": 1},
                dispatch_trace={"state": "B", "mode": "tension"},
            )

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["semantic_contradictions"] == [{"found": True, "description": "test"}]
    assert payload["semantic_graph_summary"] == {"total_nodes": 2, "contradictions": 1}
    assert payload["dispatch_trace"]["state"] == "B"
    deliberation = payload.get("deliberation")
    assert isinstance(deliberation, dict)
    assert deliberation["semantic_contradictions"] == [{"found": True, "description": "test"}]
    assert deliberation["semantic_graph_summary"] == {"total_nodes": 2, "contradictions": 1}


def test_chat_exposes_deliberation_payload_for_frontend_contract(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    class _Pipeline:
        def process(self, **kwargs):
            return SimpleNamespace(
                response="ok",
                council_verdict={
                    "verdict": "refine",
                    "summary": "Needs refinement before final output.",
                    "coherence": 0.66,
                    "responsibility_tier": "tier-2",
                    "uncertainty_band": "medium",
                    "refinement_hints": [
                        "Clarify assumptions.",
                        "Add one safety fallback.",
                    ],
                    "votes": [
                        {
                            "perspective": "analyst",
                            "decision": "concern",
                            "confidence": 0.82,
                            "reasoning": "Logic chain needs clearer assumptions.",
                        },
                        {
                            "perspective": "guardian",
                            "decision": "approve",
                            "confidence": 0.71,
                            "reasoning": "No direct safety violation found.",
                        },
                        {
                            "perspective": "critic",
                            "decision": "concern",
                            "confidence": 0.57,
                            "reasoning": "Tone may be too absolute for the context.",
                        },
                    ],
                },
                tonebridge_analysis={
                    "tone_analysis": {
                        "tone_strength": 0.68,
                        "emotion_prediction": "focused",
                    },
                    "motive_prediction": {
                        "likely_motive": "Need confidence in execution plan",
                    },
                    "collapse_risk": {
                        "collapse_risk_level": "low",
                    },
                    "resonance_defense": {
                        "suggested_intervention_strategy": "clarify_then_commit",
                    },
                },
                inner_narrative="",
                intervention_strategy="clarify_then_commit",
                internal_monologue="",
                persona_mode="",
                trajectory_analysis={},
                self_commits=[],
                ruptures=[],
                emergent_values=[],
                semantic_contradictions=[],
                semantic_graph_summary={},
                dispatch_trace={"state": "B", "mode": "tension"},
            )

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    deliberation = payload.get("deliberation")
    assert isinstance(deliberation, dict)
    assert deliberation["final_synthesis"]["response_text"] == "ok"
    assert (
        deliberation["decision_matrix"]["user_hidden_intent"] == "Need confidence in execution plan"
    )
    assert deliberation["decision_matrix"]["ai_strategy_name"] == "clarify_then_commit"
    assert deliberation["council_chamber"]["engineer"]["stance"] == (
        "Logic chain needs clearer assumptions."
    )
    assert deliberation["entropy_meter"]["value"] == 0.68
    assert deliberation["soulAudit"]["passed"] is True
    assert deliberation["semantic_contradictions"] == []
    assert deliberation["semantic_graph_summary"] == {}
    assert deliberation["visual_chain_snapshot"] == {}
    assert len(deliberation["next_moves"]) >= 1


def test_chat_deliberation_payload_is_stable_with_sparse_pipeline_data(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    captured: dict = {}
    monkeypatch.setattr(
        unified_pipeline,
        "create_unified_pipeline",
        lambda: _mock_pipeline(captured),
    )

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    deliberation = payload.get("deliberation")
    assert isinstance(deliberation, dict)
    assert deliberation["final_synthesis"]["response_text"] == "ok"
    assert set(deliberation["council_chamber"].keys()) == {"philosopher", "engineer", "guardian"}
    assert 0.0 <= deliberation["entropy_meter"]["value"] <= 1.0
    assert deliberation["decision_matrix"]["user_hidden_intent"] == "Unspecified"
    assert isinstance(deliberation["next_moves"], list)


def test_chat_deliberation_exposes_divergence_quality(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    class _Pipeline:
        def process(self, **kwargs):
            return SimpleNamespace(
                response="ok",
                council_verdict={
                    "verdict": "refine",
                    "summary": "Needs stronger alignment before response.",
                    "coherence": 0.61,
                    "votes": [
                        {
                            "perspective": "analyst",
                            "decision": "concern",
                            "confidence": 0.84,
                            "reasoning": "Assumptions are underspecified for execution.",
                            "evidence": ["trace://logic"],
                        },
                        {
                            "perspective": "guardian",
                            "decision": "approve",
                            "confidence": 0.72,
                            "reasoning": "No direct safety violation detected.",
                        },
                        {
                            "perspective": "critic",
                            "decision": "concern",
                            "confidence": 0.67,
                            "reasoning": "Tone could be interpreted as overconfident.",
                        },
                    ],
                    "divergence_analysis": {
                        "core_divergence": "Engineer asks for stronger assumptions while Guardian allows current draft.",
                        "role_tensions": [
                            {
                                "from_role": "analyst",
                                "to_role": "guardian",
                                "reason": "Needs explicit assumptions before execution.",
                                "counter_reason": "Safety risk remains acceptable.",
                            }
                        ],
                        "quality": {
                            "score": 0.81,
                            "band": "high",
                            "conflict_coverage": 0.67,
                            "reasoning_specificity": 0.79,
                            "evidence_coverage": 0.33,
                            "confidence_balance": 0.75,
                            "role_tension_coverage": 0.66,
                        },
                    },
                },
                tonebridge_analysis={},
                inner_narrative="",
                intervention_strategy="",
                internal_monologue="",
                persona_mode="",
                trajectory_analysis={},
                self_commits=[],
                ruptures=[],
                emergent_values=[],
                semantic_contradictions=[],
                semantic_graph_summary={},
                dispatch_trace={},
            )

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())

    client = _client()
    response = client.post("/api/chat", json={"message": "hello"})
    payload = response.get_json()

    assert response.status_code == 200
    deliberation = payload.get("deliberation")
    assert isinstance(deliberation, dict)
    assert deliberation["divergence_quality"]["band"] == "high"
    assert deliberation["divergence_quality"]["score"] == 0.81
    assert deliberation["council_chamber"]["engineer"]["conflict_point"].startswith("guardian:")
