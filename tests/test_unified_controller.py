import builtins

from tonesoul import council as council_pkg
from tonesoul import unified_controller as controller_mod


class _FakeSemanticController:
    def __init__(self):
        self.calls = []
        self.reset_called = False

    def process(self, intended, generated):
        self.calls.append((intended, generated))
        return {
            "tension": 0.3,
            "coupler": "ok",
            "lambda_state": "stable",
            "memory_action": "none",
            "bridge_allowed": True,
            "timestamp": "semantic-ts",
        }

    def reset(self):
        self.reset_called = True


def test_process_delegates_to_semantic_controller(monkeypatch):
    fake_semantic = _FakeSemanticController()
    monkeypatch.setattr(controller_mod, "SemanticController", lambda: fake_semantic)

    controller = controller_mod.UnifiedController(enable_council=False)
    result = controller.process([1.0], [0.5])

    assert fake_semantic.calls == [([1.0], [0.5])]
    assert result["tension"] == 0.3


def test_validate_output_returns_default_when_council_disabled(monkeypatch):
    monkeypatch.setattr(controller_mod, "SemanticController", _FakeSemanticController)
    controller = controller_mod.UnifiedController(enable_council=False)

    assert controller.validate_output("draft") == {
        "verdict": "approve",
        "summary": "Council not enabled",
        "council_enabled": False,
    }


def test_init_disables_council_on_import_error(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "tonesoul.council":
            raise ImportError("no council runtime")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(controller_mod, "SemanticController", _FakeSemanticController)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    controller = controller_mod.UnifiedController(enable_council=True)

    assert controller._council_enabled is False
    assert controller._council is None


def test_process_with_council_includes_verdict_and_context(monkeypatch):
    fake_semantic = _FakeSemanticController()
    captured = {}

    class FakeVerdict:
        def to_dict(self):
            return {"verdict": "approve", "summary": "ok"}

    class FakeCouncilRuntime:
        def deliberate(self, request):
            captured["request"] = request
            return FakeVerdict()

    class FakeCouncilRequest:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(controller_mod, "SemanticController", lambda: fake_semantic)
    monkeypatch.setattr(council_pkg, "CouncilRuntime", lambda: FakeCouncilRuntime())
    monkeypatch.setattr(council_pkg, "CouncilRequest", FakeCouncilRequest)

    controller = controller_mod.UnifiedController(enable_council=True)
    result = controller.process_with_council(
        [1.0],
        [0.2],
        "draft output",
        context={
            "selected_frames": ["frame-1"],
            "role_summary": "summary",
            "role_catalog": {"guardian": "G"},
        },
        user_intent="help",
    )

    assert result["council_verdict"] == {"verdict": "approve", "summary": "ok"}
    assert result["council_enabled"] is True
    assert result["timestamp"]
    assert captured["request"].draft_output == "draft output"
    assert captured["request"].context["semantic_tension"]["tension"] == 0.3
    assert captured["request"].selected_frames == ["frame-1"]
    assert captured["request"].role_summary == "summary"
    assert captured["request"].role_catalog == {"guardian": "G"}
    assert captured["request"].user_intent == "help"


def test_reset_delegates_to_semantic_controller(monkeypatch):
    fake_semantic = _FakeSemanticController()
    monkeypatch.setattr(controller_mod, "SemanticController", lambda: fake_semantic)

    controller = controller_mod.UnifiedController(enable_council=False)
    controller.reset()

    assert fake_semantic.reset_called is True
