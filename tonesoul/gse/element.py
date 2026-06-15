# PACKAGE-STATUS (as of 2026-06-15): GSEElement is the gse package's core dataclass, imported by gse/registry.py and gse/__init__.py — but the gse package as a whole is unwired (no non-test live importer; see registry.py DORMANT marker). Live only within a parked package. see docs/architecture/architecture_legibility_2026-06-15.md
"""GSEElement — the atomic unit of the Governance Semantic Engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

__ts_layer__ = "governance"

ClusterType = Literal["deliberation", "interiority", "propagation"]
RoleType = Literal["主導", "催化", "約束"]


@dataclass(frozen=True)
class GSEElement:
    """One governance element: a concept made operatable.

    Fields
    ------
    symbol          Short identifier, e.g. "[Ten]", "[Dbt]".
    name            Chinese name.
    definition      What the concept IS (static).
    role            Function in a governance combination.
    cluster         Which of the three clusters it belongs to.
    period          Sub-grouping within the cluster (1-based).
    trigger         The condition that activates this element.
    operation       Step-by-step instruction an agent can follow directly.
    falsifiable     How to verify the element is functioning correctly.
    """

    symbol: str
    name: str
    definition: str
    role: RoleType
    cluster: ClusterType
    period: int
    trigger: str
    operation: str
    falsifiable: str

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "definition": self.definition,
            "role": self.role,
            "cluster": self.cluster,
            "period": self.period,
            "trigger": self.trigger,
            "operation": self.operation,
            "falsifiable": self.falsifiable,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GSEElement":
        return cls(
            symbol=data["symbol"],
            name=data["name"],
            definition=data["definition"],
            role=data["role"],
            cluster=data["cluster"],
            period=int(data["period"]),
            trigger=data["trigger"],
            operation=data["operation"],
            falsifiable=data["falsifiable"],
        )
