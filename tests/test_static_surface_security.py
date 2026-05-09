from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_council_playground_drops_query_token_ingest() -> None:
    source = (REPO_ROOT / "apps" / "council-playground" / "app.js").read_text(encoding="utf-8")

    assert 'new URLSearchParams(window.location.search).get("read_token")' not in source
    assert "window.sessionStorage" in source
    assert "localStorage.getItem(READ_TOKEN_STORAGE_KEY)" not in source


def test_council_playground_renders_audit_logs_with_text_nodes() -> None:
    source = (REPO_ROOT / "apps" / "council-playground" / "app.js").read_text(encoding="utf-8")

    assert "nodes.auditList.innerHTML = logs" not in source
    assert "rationale.textContent" in source
    assert "title.textContent" in source


def test_world_surface_escapes_dynamic_text() -> None:
    source = (REPO_ROOT / "apps" / "dashboard" / "world.html").read_text(encoding="utf-8")

    assert "function escapeHtml(value)" in source
    assert "escapeHtml(v.content || '')" in source
    assert "escapeHtml(t.topic || " in source
    assert "escapeHtml(v.agent || '?')" in source
    assert "${v.content || ''}" not in source
    assert "${t.topic || " not in source
