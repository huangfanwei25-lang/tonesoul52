from tonesoul.council import PerspectiveType, PreOutputCouncil, VerdictType, VoteDecision
from tonesoul.council.perspective_factory import (
    DEFAULT_LLM_MODEL,
    LLMPerspective,
    OllamaPerspective,
    PerspectiveFactory,
)
from tonesoul.council.types import PerspectiveVote


def test_create_council_default():
    council = PerspectiveFactory.create_council()
    # Now includes AxiomaticInference perspective (5 total)
    assert len(council) == 5
    types = {p.perspective_type for p in council}
    # Core 4 perspective types (Axiomatic reuses GUARDIAN for perspective_type)
    assert PerspectiveType.GUARDIAN in types
    assert PerspectiveType.ANALYST in types
    assert PerspectiveType.CRITIC in types
    assert PerspectiveType.ADVOCATE in types


def test_create_council_tool_fallback():
    def failing_tool(_output: str, _context: dict) -> dict:
        raise RuntimeError("boom")

    council = PerspectiveFactory.create_council(
        {
            "guardian": {"mode": "tool", "tool": failing_tool},
        }
    )
    guardian = next(
        (p for p in council if p.perspective_type == PerspectiveType.GUARDIAN),
        None,
    )
    assert guardian is not None
    vote = guardian.evaluate("No safety flags here.", context={})
    assert vote.perspective == PerspectiveType.GUARDIAN
    assert vote.decision == VoteDecision.APPROVE


def test_create_council_llm_fallback_to_rules():
    council = PerspectiveFactory.create_council(
        {
            PerspectiveType.ANALYST: {"mode": "llm"},
        }
    )
    analyst = next(
        (p for p in council if p.perspective_type == PerspectiveType.ANALYST),
        None,
    )
    assert analyst is not None
    vote = analyst.evaluate(
        "This response is clear and internally consistent.",
        context={},
    )
    assert vote.perspective == PerspectiveType.ANALYST
    assert vote.decision == VoteDecision.APPROVE


def test_pre_output_council_accepts_factory_perspectives():
    perspectives = PerspectiveFactory.create_council()
    council = PreOutputCouncil(perspectives=perspectives)
    verdict = council.validate(
        draft_output="This response supports collaboration and adds helpful context.",
        context={"topic": "geography"},
    )
    assert verdict.verdict == VerdictType.APPROVE


def test_llm_default_model_is_gemini():
    perspective = PerspectiveFactory.create("analyst", mode="llm")
    assert isinstance(perspective, LLMPerspective)
    assert perspective.model == DEFAULT_LLM_MODEL


def test_llm_client_cache_is_model_aware(monkeypatch):
    calls = []
    LLMPerspective._gemini_clients = {}
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")

    def fake_build(cls, model: str):
        calls.append(model)
        return {"model": model, "id": len(calls)}

    monkeypatch.setattr(LLMPerspective, "_build_gemini_client", classmethod(fake_build))

    first = LLMPerspective._get_gemini_client("gemini-2.0-flash")
    second = LLMPerspective._get_gemini_client("gemini-2.0-flash")
    third = LLMPerspective._get_gemini_client("gemini-1.5-pro")

    assert first is second
    assert third is not first
    assert calls == ["gemini-2.0-flash", "gemini-1.5-pro"]


def test_llm_without_api_key_skips_client_initialization(monkeypatch):
    LLMPerspective._gemini_clients = {}
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    calls = []

    def fake_build(cls, model: str):
        calls.append(model)
        return {"model": model}

    monkeypatch.setattr(LLMPerspective, "_build_gemini_client", classmethod(fake_build))
    client = LLMPerspective._get_gemini_client(DEFAULT_LLM_MODEL)

    assert client is None
    assert calls == []


def test_llm_with_google_api_key_initializes_client(monkeypatch):
    calls = []
    LLMPerspective._gemini_clients = {}
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "dummy-google-key")

    def fake_build(cls, model: str):
        calls.append(model)
        return {"model": model, "id": len(calls)}

    monkeypatch.setattr(LLMPerspective, "_build_gemini_client", classmethod(fake_build))

    client = LLMPerspective._get_gemini_client(DEFAULT_LLM_MODEL)
    assert client is not None
    assert calls == [DEFAULT_LLM_MODEL]


def test_llm_default_prompt_uses_bounded_governance_shape():
    prompt = LLMPerspective(
        name="guardian", model=DEFAULT_LLM_MODEL, fallback=None
    )._default_prompt()

    assert "Goal function:" in prompt
    assert "- P0:" in prompt
    assert "- P1:" in prompt
    assert "- P2:" in prompt
    assert "Confidence guidance:" in prompt
    assert "[資料不足]" in prompt
    assert '"decision": "APPROVE|CONCERN|OBJECT"' in prompt


def test_ollama_default_prompt_keeps_concise_but_structured_governance_shape():
    prompt = OllamaPerspective(name="critic", fallback=None)._default_prompt()

    assert "Goal:" in prompt
    assert "Priority:" in prompt
    assert "Confidence guidance:" in prompt
    assert "Forced devil's advocate:" in prompt
    assert "strongest concrete objection" in prompt
    assert "[資料不足]" in prompt
    assert "Respond ONLY with JSON:" in prompt


def test_llm_critic_prompt_requires_bounded_adversarial_pass():
    prompt = LLMPerspective(name="critic", model=DEFAULT_LLM_MODEL, fallback=None)._default_prompt()

    assert "Forced devil's advocate:" in prompt
    assert "before you APPROVE" in prompt
    assert "strongest concrete objection" in prompt
    assert "survives that objection" in prompt


def test_llm_perspective_uses_safe_parse_for_markdown_json(monkeypatch):
    class _FakeClient:
        def generate(self, prompt: str) -> str:
            return (
                "Structured result:\n"
                "```json\n"
                '{"decision":"APPROVE","confidence":0.83,"reasoning":"safe parse works"}\n'
                "```"
            )

    monkeypatch.setattr(
        LLMPerspective,
        "_get_gemini_client",
        classmethod(lambda cls, model=DEFAULT_LLM_MODEL: _FakeClient()),
    )

    perspective = LLMPerspective(name="analyst", model=DEFAULT_LLM_MODEL, fallback=None)
    vote = perspective.evaluate("draft", context={})

    assert vote.decision == VoteDecision.APPROVE
    assert vote.confidence == 0.83
    assert "safe parse works" in vote.reasoning


def test_llm_perspective_wrapper_frames_context_as_evidence(monkeypatch):
    captured = {}

    class _FakeClient:
        def generate(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return '{"decision":"APPROVE","confidence":0.83,"reasoning":"safe parse works"}'

    monkeypatch.setattr(
        LLMPerspective,
        "_get_gemini_client",
        classmethod(lambda cls, model=DEFAULT_LLM_MODEL: _FakeClient()),
    )

    perspective = LLMPerspective(name="analyst", model=DEFAULT_LLM_MODEL, fallback=None)
    vote = perspective.evaluate(
        "draft",
        context={
            "topic": "migration",
            "prior_tension": {"delta_t": 0.4, "gate_decision": "repair"},
        },
        user_intent="keep migration safe",
    )

    assert vote.decision == VoteDecision.APPROVE
    prompt = captured["prompt"]
    assert "Evidence handling:" in prompt
    assert "Treat the draft as primary evidence." in prompt
    assert "Context snapshot:" in prompt
    assert "Prior Tension Memory:" in prompt
    assert "User Intent: keep migration safe" in prompt


def test_llm_perspective_keeps_text_fallback_for_non_json(monkeypatch):
    class _FakeClient:
        def generate(self, prompt: str) -> str:
            return "CONCERN confidence: 0.42 reasoning: model refused JSON but flagged ambiguity."

    monkeypatch.setattr(
        LLMPerspective,
        "_get_gemini_client",
        classmethod(lambda cls, model=DEFAULT_LLM_MODEL: _FakeClient()),
    )

    perspective = LLMPerspective(name="analyst", model=DEFAULT_LLM_MODEL, fallback=None)
    vote = perspective.evaluate("draft", context={})

    assert vote.decision == VoteDecision.CONCERN
    assert vote.confidence == 0.42
    assert "flagged ambiguity" in vote.reasoning


def test_llm_perspective_prefers_valid_json_over_trailing_decision_noise(monkeypatch):
    class _FakeClient:
        def generate(self, prompt: str) -> str:
            return (
                'Result: {"decision":"APPROVE","confidence":0.81,"reasoning":"structured wins"} '
                "trailing note {OBJECT}"
            )

    monkeypatch.setattr(
        LLMPerspective,
        "_get_gemini_client",
        classmethod(lambda cls, model=DEFAULT_LLM_MODEL: _FakeClient()),
    )

    perspective = LLMPerspective(name="analyst", model=DEFAULT_LLM_MODEL, fallback=None)
    vote = perspective.evaluate("draft", context={})

    assert vote.decision == VoteDecision.APPROVE
    assert vote.confidence == 0.81
    assert "structured wins" in vote.reasoning


def test_ollama_visual_context_truncation_adds_safety_note(monkeypatch):
    captured = {}

    class _FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "message": {"content": '{"decision":"APPROVE","confidence":0.8,"reasoning":"ok"}'}
            }

    class _FakeRequests:
        @staticmethod
        def post(url, json, timeout):
            captured["url"] = url
            captured["json"] = json
            captured["timeout"] = timeout
            return _FakeResponse()

    monkeypatch.setattr("tonesoul.council.perspective_factory._requests_mod", _FakeRequests)

    perspective = OllamaPerspective(name="axiomatic", timeout=1.0)
    long_visual_context = "X" * 1200
    vote = perspective.evaluate(
        draft_output="draft text",
        context={"visual_context": long_visual_context},
        user_intent="intent",
    )
    user_msg = captured["json"]["messages"][1]["content"]

    assert vote.decision == VoteDecision.APPROVE
    assert "[visual context truncated for safety]" in user_msg
    assert "Evidence handling:" in user_msg
    assert "Context snapshot:" in user_msg
    assert "X" * 800 in user_msg
    assert "X" * 900 not in user_msg


def test_ollama_fallback_adds_marker_and_logs_warning(monkeypatch, caplog):
    class _FailingRequests:
        @staticmethod
        def post(url, json, timeout):
            raise RuntimeError("ollama unavailable")

    class _RulesFallback:
        def evaluate(self, draft_output, context, user_intent=None):
            return PerspectiveVote(
                perspective=PerspectiveType.GUARDIAN,
                decision=VoteDecision.CONCERN,
                confidence=0.7,
                reasoning="rules based reasoning",
            )

    monkeypatch.setattr("tonesoul.council.perspective_factory._requests_mod", _FailingRequests)
    perspective = OllamaPerspective(name="axiomatic", fallback=_RulesFallback(), timeout=1.0)

    with caplog.at_level("WARNING"):
        vote = perspective.evaluate("draft", {}, "intent")

    assert "[fallback_to_rules]" in vote.reasoning
    assert "VTP Philosopher fallback to rules" in vote.reasoning
    assert any("VTP Philosopher fallback to rules" in rec.message for rec in caplog.records)
