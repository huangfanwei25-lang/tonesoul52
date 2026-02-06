from __future__ import annotations

from enum import Enum
from typing import Dict


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
