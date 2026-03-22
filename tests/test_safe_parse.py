from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from tonesoul.safe_parse import parse_llm_response, safe_parse_json, validate_dict


class _SamplePayload(BaseModel):
    title: str
    score: int
    meta: dict[str, object] | None = None


def test_safe_parse_json_valid() -> None:
    payload = safe_parse_json('{"title": "alpha", "score": 3, "meta": {"nested": {"ok": true}}}')

    assert payload == {
        "title": "alpha",
        "score": 3,
        "meta": {"nested": {"ok": True}},
    }


def test_safe_parse_json_with_trailing_commas() -> None:
    payload = safe_parse_json('{"title": "alpha", "score": 3, "meta": {"tags": ["x", "y",],},}')

    assert payload == {
        "title": "alpha",
        "score": 3,
        "meta": {"tags": ["x", "y"]},
    }


def test_safe_parse_json_from_markdown_codeblock() -> None:
    payload = safe_parse_json("""
        ```json
        {"title": "alpha", "score": 3}
        ```
        """)

    assert payload == {"title": "alpha", "score": 3}


def test_safe_parse_json_returns_none_on_garbage() -> None:
    assert safe_parse_json("not json at all") is None


def test_parse_llm_response_extracts_object() -> None:
    result = parse_llm_response(
        (
            "Here is the final answer.\n"
            '{"title": "alpha", "score": 3, "meta": {"tags": ["x"], "inner": {"ok": true}}}\n'
            "Use this object."
        ),
        _SamplePayload,
    )

    assert result is not None
    assert result.title == "alpha"
    assert result.score == 3
    assert result.meta == {"tags": ["x"], "inner": {"ok": True}}


def test_parse_llm_response_strict_rejects_partial() -> None:
    with pytest.raises(ValidationError):
        parse_llm_response('{"title": "alpha"}', _SamplePayload, strict=True)


def test_validate_dict_with_valid_schema() -> None:
    result = validate_dict({"title": "alpha", "score": 3}, _SamplePayload)

    assert result.title == "alpha"
    assert result.score == 3


def test_validate_dict_missing_field() -> None:
    with pytest.raises(ValidationError):
        validate_dict({"title": "alpha"}, _SamplePayload)
