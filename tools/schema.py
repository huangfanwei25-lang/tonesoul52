from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union

try:
    from memory.genesis import Genesis, resolve_responsibility_tier
except Exception:
    Genesis = None  # type: ignore

    def resolve_responsibility_tier(_: object) -> str:
        return "TIER_3"


class ToolErrorCode(str, Enum):
    INVALID_INPUT = "E001"
    MISSING_CREDENTIALS = "E002"
    NETWORK_ERROR = "E003"
    UPSTREAM_ERROR = "E004"
    GOVERNANCE_BLOCK = "E010"
    INTERNAL_ERROR = "E999"


_TIER_ORDER = {
    "TIER_1": 1,
    "TIER_2": 2,
    "TIER_3": 3,
}


@dataclass
class ToolError:
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details is not None:
            payload["details"] = self.details
        return payload


@dataclass
class ToolResponse:
    success: bool
    data: Optional[Any] = None
    error: Optional[ToolError] = None
    genesis: Optional[str] = None
    intent_id: Optional[str] = None
    responsibility_tier: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "success": self.success,
            "data": self.data,
            "error": self.error.to_dict() if self.error else None,
            "genesis": self.genesis,
            "responsibility_tier": self.responsibility_tier,
            "intent_id": self.intent_id,
        }
        return payload


def _normalize_genesis(genesis: Optional[Union[str, "Genesis"]]) -> Optional[str]:
    if genesis is None:
        return None
    if Genesis is not None and isinstance(genesis, Genesis):
        return genesis.value
    if isinstance(genesis, str):
        return genesis
    return str(genesis)


def _resolve_tier(genesis: Optional[Union[str, "Genesis"]]) -> Optional[str]:
    if genesis is None:
        return None
    if Genesis is not None and isinstance(genesis, Genesis):
        return resolve_responsibility_tier(genesis)
    if isinstance(genesis, str) and Genesis is not None:
        try:
            enum_value = Genesis(genesis)
        except Exception:
            return "TIER_3"
        return resolve_responsibility_tier(enum_value)
    return "TIER_3"


def enforce_responsibility_tier(
    *,
    genesis: Optional[Union[str, "Genesis"]],
    minimum: str,
    intent_id: Optional[str] = None,
    action: Optional[str] = None,
    message: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if minimum not in _TIER_ORDER:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message="Invalid responsibility tier configuration.",
            details={"required_tier": minimum},
            genesis=genesis,
            intent_id=intent_id,
        )

    actual = _resolve_tier(genesis) or "TIER_3"
    if _TIER_ORDER.get(actual, 99) <= _TIER_ORDER[minimum]:
        return None

    return tool_error(
        code=ToolErrorCode.GOVERNANCE_BLOCK,
        message=message or "Responsibility tier insufficient for this action.",
        details={
            "required_tier": minimum,
            "actual_tier": actual,
            "action": action,
        },
        genesis=genesis,
        intent_id=intent_id,
    )


def tool_success(
    *,
    data: Optional[Any] = None,
    genesis: Optional[Union[str, "Genesis"]] = None,
    intent_id: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_genesis = _normalize_genesis(genesis)
    tier = _resolve_tier(genesis)
    response = ToolResponse(
        success=True,
        data=data,
        error=None,
        genesis=normalized_genesis,
        responsibility_tier=tier,
        intent_id=intent_id,
    )
    return response.to_dict()


def tool_error(
    *,
    code: Union[ToolErrorCode, str],
    message: str,
    details: Optional[Dict[str, Any]] = None,
    genesis: Optional[Union[str, "Genesis"]] = None,
    intent_id: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_genesis = _normalize_genesis(genesis)
    tier = _resolve_tier(genesis)
    error = ToolError(
        code=code.value if isinstance(code, ToolErrorCode) else str(code),
        message=message,
        details=details,
    )
    response = ToolResponse(
        success=False,
        data=None,
        error=error,
        genesis=normalized_genesis,
        responsibility_tier=tier,
        intent_id=intent_id,
    )
    return response.to_dict()
