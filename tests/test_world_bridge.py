"""Tests for world_bridge — governance data → HTML injection."""

import json

from apps.dashboard.frontend.utils.world_bridge import (
    _load_aegis,
    _load_gov_data,
    _load_visitors,
    _load_world_data,
    build_world_html,
)


def test_load_world_data_returns_dict():
    result = _load_world_data()
    assert isinstance(result, dict)


def test_load_gov_data_returns_dict():
    result = _load_gov_data()
    assert isinstance(result, dict)


def test_load_visitors_returns_list():
    result = _load_visitors()
    assert isinstance(result, list)


def test_load_aegis_returns_dict():
    result = _load_aegis()
    assert isinstance(result, dict)
    assert "integrity" in result
    assert "chain_valid" in result


def test_build_world_html_returns_string():
    html = build_world_html()
    assert isinstance(html, str)
    # Should contain injected data or fallback message
    if "world.html not found" not in html:
        assert "__WORLD_DATA__" in html
        assert "__GOV_DATA__" in html
        assert "__VISITORS__" in html
        assert "__AEGIS__" in html


def test_build_world_html_injection_is_valid_json():
    html = build_world_html()
    if "world.html not found" in html:
        return  # world.html doesn't exist in test env, skip

    # Extract injected JSON from the first <script> block
    marker = "var __WORLD_DATA__ = "
    if marker not in html:
        return
    start = html.index(marker) + len(marker)
    end = html.index(";\n", start)
    data = html[start:end]
    parsed = json.loads(data)
    assert isinstance(parsed, dict)
