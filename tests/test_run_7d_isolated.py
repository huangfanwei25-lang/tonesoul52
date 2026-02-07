import pytest

import scripts.run_7d_isolated as run_7d_isolated


def test_parse_base_url_accepts_localhost_with_port():
    host, port = run_7d_isolated._parse_base_url("http://127.0.0.1:5001", "api-base")
    assert host == "127.0.0.1"
    assert port == 5001


def test_parse_base_url_rejects_non_localhost():
    with pytest.raises(ValueError):
        run_7d_isolated._parse_base_url("http://example.com:5001", "api-base")


def test_parse_base_url_requires_explicit_port():
    with pytest.raises(ValueError):
        run_7d_isolated._parse_base_url("http://127.0.0.1", "api-base")
