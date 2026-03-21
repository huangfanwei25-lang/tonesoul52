"""Safe JSON parsing utilities for LLM responses.

LLMs often return JSON wrapped in markdown code blocks, or with
trailing commas, or missing fields. This module provides robust
parsing that extracts, cleans, and validates JSON against Pydantic schemas.

Usage:
    from tonesoul.safe_parse import safe_parse_json, parse_llm_response
    from tonesoul.schemas import ToneAnalysisResult

    # Parse raw LLM text into a validated Pydantic model
    result = parse_llm_response(llm_text, ToneAnalysisResult)

    # Or just safely extract JSON dict from messy LLM output
    data = safe_parse_json(llm_text)
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# JSON extraction from messy LLM output
# ---------------------------------------------------------------------------

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```")


def _strip_trailing_commas(text: str) -> str:
    """Remove trailing commas before } or ] (common LLM mistake)."""
    return re.sub(r",\s*([}\]])", r"\1", text)


def _extract_balanced_json_object(text: str) -> Optional[str]:
    """Extract the first balanced JSON object from free-form text.

    This avoids greedy `{...}` matching when valid JSON is followed by
    extra brace-bearing text or stray decision tokens.
    """
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue

        if char == "{":
            depth += 1
            continue

        if char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None


def _extract_json_str(text: str) -> Optional[str]:
    """Extract JSON string from LLM output, handling various formats.

    Tries in order:
    1. Direct JSON parse
    2. Markdown code block extraction (```json ... ```)
    3. First JSON object regex match
    """
    text = text.strip()

    # 1. Direct parse attempt
    if text.startswith("{"):
        return _extract_balanced_json_object(text)
    if text.startswith("["):
        return text

    # 2. Markdown code block
    match = _JSON_BLOCK_RE.search(text)
    if match:
        return match.group(1).strip()

    # 3. First balanced JSON object
    balanced = _extract_balanced_json_object(text)
    if balanced:
        return balanced

    return None


def safe_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Safely extract and parse JSON from LLM output.

    Handles:
    - Raw JSON strings
    - JSON wrapped in markdown code blocks
    - Trailing commas
    - Whitespace issues

    Args:
        text: Raw LLM response text.

    Returns:
        Parsed dict, or None if parsing fails.
    """
    if not text or not text.strip():
        return None

    json_str = _extract_json_str(text)
    if json_str is None:
        return None

    # Clean common LLM formatting errors
    json_str = _strip_trailing_commas(json_str)

    try:
        result = json.loads(json_str)
        if isinstance(result, dict):
            return result
        return None
    except json.JSONDecodeError:
        return None


def parse_llm_response(
    text: str,
    schema: Type[T],
    *,
    strict: bool = False,
) -> Optional[T]:
    """Parse LLM response text into a validated Pydantic model.

    This is the primary entry point for converting LLM output into
    type-safe, validated data structures.

    Args:
        text: Raw LLM response text.
        schema: Pydantic model class to validate against.
        strict: If True, raise ValidationError on failure.
                If False (default), return None on failure.

    Returns:
        Validated Pydantic model instance, or None if parsing/validation fails.

    Raises:
        ValidationError: If strict=True and validation fails.

    Example:
        from tonesoul.schemas import ToneAnalysisResult
        result = parse_llm_response(llm_text, ToneAnalysisResult)
        if result:
            print(f"Tone strength: {result.tone_strength}")
    """
    data = safe_parse_json(text)
    if data is None:
        if strict:
            raise ValueError(f"Could not extract JSON from LLM response: {text[:200]}")
        return None

    try:
        return schema.model_validate(data)
    except ValidationError:
        if strict:
            raise
        # Try with defaults for missing fields
        try:
            return schema.model_validate(data, strict=False)
        except ValidationError:
            return None


def validate_dict(
    data: Dict[str, Any],
    schema: Type[T],
) -> T:
    """Validate an already-parsed dict against a Pydantic schema.

    Unlike parse_llm_response, this expects a pre-parsed dict
    and always raises on validation failure.

    Args:
        data: Pre-parsed dictionary.
        schema: Pydantic model class.

    Returns:
        Validated Pydantic model instance.

    Raises:
        ValidationError: If the data doesn't match the schema.
    """
    return schema.model_validate(data)
