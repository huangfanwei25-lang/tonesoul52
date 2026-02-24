import scripts.verify_vercel_preflight as preflight


def _status(payload: dict, name: str) -> str:
    for check in payload["checks"]:
        if check["name"] == name:
            return check["status"]
    raise AssertionError(f"missing check: {name}")


def test_validate_backend_url_rejects_localhost() -> None:
    ok, detail = preflight._validate_backend_url(
        "http://127.0.0.1:5000",
        allow_http=False,
        same_origin=False,
    )
    assert ok is False
    assert "local host" in detail


def test_validate_backend_url_requires_https_by_default() -> None:
    ok, detail = preflight._validate_backend_url(
        "http://api.example.com",
        allow_http=False,
        same_origin=False,
    )
    assert ok is False
    assert "HTTPS" in detail


def test_validate_backend_url_allows_http_with_flag() -> None:
    ok, detail = preflight._validate_backend_url(
        "http://api.example.com",
        allow_http=True,
        same_origin=False,
    )
    assert ok is True
    assert "valid" in detail


def test_evaluate_preflight_fails_when_report_provider_fallback_unset() -> None:
    payload = preflight.evaluate_preflight(
        backend_url="https://api.example.com",
        env_values={
            "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK": "0",
            "NEXT_PUBLIC_CHAT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_BACKEND_CHAT_FIRST": None,
            "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK": "0",
            "NEXT_PUBLIC_REPORT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK": None,
        },
        allow_http=False,
        allow_chat_mock_fallback=False,
        same_origin=False,
        probe_health=False,
        timeout=5,
    )
    assert payload["ok"] is False
    assert _status(payload, "report_provider_fallback") == "fail"


def test_evaluate_preflight_fails_when_chat_mock_fallback_enabled() -> None:
    payload = preflight.evaluate_preflight(
        backend_url="https://api.example.com",
        env_values={
            "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK": "1",
            "NEXT_PUBLIC_CHAT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_BACKEND_CHAT_FIRST": None,
            "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK": "0",
            "NEXT_PUBLIC_REPORT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK": "0",
        },
        allow_http=False,
        allow_chat_mock_fallback=False,
        same_origin=False,
        probe_health=False,
        timeout=5,
    )
    assert payload["ok"] is False
    assert _status(payload, "chat_mock_fallback") == "fail"


def test_evaluate_preflight_passes_with_health_probe() -> None:
    def fake_probe(_backend_url: str, _timeout: int) -> tuple[bool, str]:
        return True, "health probe passed"

    payload = preflight.evaluate_preflight(
        backend_url="https://api.example.com",
        env_values={
            "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK": "0",
            "NEXT_PUBLIC_CHAT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_BACKEND_CHAT_FIRST": None,
            "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK": "0",
            "NEXT_PUBLIC_REPORT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK": "0",
        },
        allow_http=False,
        allow_chat_mock_fallback=False,
        same_origin=False,
        probe_health=True,
        timeout=5,
        health_probe_fn=fake_probe,
    )
    assert payload["ok"] is True
    assert _status(payload, "backend_health_probe") == "pass"


def test_evaluate_preflight_allows_same_origin_without_backend_url() -> None:
    payload = preflight.evaluate_preflight(
        backend_url=None,
        env_values={
            "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK": "0",
            "NEXT_PUBLIC_CHAT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_BACKEND_CHAT_FIRST": None,
            "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK": "0",
            "NEXT_PUBLIC_REPORT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK": "0",
        },
        allow_http=False,
        allow_chat_mock_fallback=False,
        same_origin=True,
        probe_health=True,
        timeout=5,
    )
    assert payload["ok"] is True
    assert _status(payload, "backend_url") == "pass"
    assert _status(payload, "backend_health_probe") == "skip"


def test_evaluate_preflight_governance_status_probe_passes() -> None:
    def fake_probe(_web_base: str, _timeout: int) -> tuple[bool, str]:
        return True, "governance status probe passed"

    payload = preflight.evaluate_preflight(
        backend_url="https://api.example.com",
        env_values={
            "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK": "0",
            "NEXT_PUBLIC_CHAT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_BACKEND_CHAT_FIRST": None,
            "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK": "0",
            "NEXT_PUBLIC_REPORT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK": "0",
        },
        allow_http=False,
        allow_chat_mock_fallback=False,
        same_origin=False,
        probe_health=False,
        web_base="https://tonesoul52-ruby.vercel.app",
        probe_governance_status=True,
        timeout=5,
        governance_probe_fn=fake_probe,
    )
    assert payload["ok"] is True
    assert _status(payload, "governance_status_probe") == "pass"


def test_evaluate_preflight_governance_status_probe_fails_without_web_base() -> None:
    payload = preflight.evaluate_preflight(
        backend_url="https://api.example.com",
        env_values={
            "TONESOUL_ENABLE_CHAT_MOCK_FALLBACK": "0",
            "NEXT_PUBLIC_CHAT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_BACKEND_CHAT_FIRST": None,
            "NEXT_PUBLIC_ENABLE_PROVIDER_FALLBACK": "0",
            "NEXT_PUBLIC_REPORT_EXECUTION_MODE": "backend",
            "NEXT_PUBLIC_REPORT_PROVIDER_FALLBACK": "0",
        },
        allow_http=False,
        allow_chat_mock_fallback=False,
        same_origin=False,
        probe_health=False,
        web_base=None,
        probe_governance_status=True,
        timeout=5,
    )
    assert payload["ok"] is False
    assert _status(payload, "governance_status_probe") == "fail"
