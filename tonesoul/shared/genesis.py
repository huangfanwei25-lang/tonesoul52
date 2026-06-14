from __future__ import annotations

from enum import Enum
from typing import Dict

__ts_layer__ = "shared"
__ts_purpose__ = (
    "Origin-of-intent domain type (Genesis) and responsibility-tier mapping; "
    "stdlib-only, relocated from repo-root memory/ (PR1 packaging truth, 2026-06-13)."
)


class Genesis(Enum):
    """Origin of intent for a decision."""

    AUTONOMOUS = "autonomous"
    REACTIVE_USER = "reactive_user"
    REACTIVE_SOCIAL = "reactive_social"
    MANDATORY = "mandatory"


RESPONSIBILITY_TIER: Dict[Genesis, str] = {
    Genesis.AUTONOMOUS: "TIER_1",
    Genesis.REACTIVE_USER: "TIER_2",
    Genesis.REACTIVE_SOCIAL: "TIER_2",
    Genesis.MANDATORY: "TIER_3",
}


def resolve_responsibility_tier(genesis: Genesis) -> str:
    return RESPONSIBILITY_TIER.get(genesis, "TIER_3")
