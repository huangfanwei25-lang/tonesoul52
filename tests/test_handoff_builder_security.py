from tools.handoff_builder import HandoffBuilder


def test_handoff_builder_uses_env_secret(monkeypatch):
    monkeypatch.setenv("HANDOFF_SECRET", "custom_secret")
    builder = HandoffBuilder()
    assert builder.secret_key == "custom_secret"


def test_handoff_builder_without_env_uses_non_default_secret(monkeypatch):
    monkeypatch.delenv("HANDOFF_SECRET", raising=False)
    builder = HandoffBuilder()
    assert builder.secret_key != "default_dev_secret"
    assert len(builder.secret_key) == 64
