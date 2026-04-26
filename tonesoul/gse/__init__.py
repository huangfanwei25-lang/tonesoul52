"""tonesoul.gse — Governance Semantic Engine

Operatable ontology for governance, agent interiority, and principle propagation.
Each element carries: definition + operation_instruction + trigger + falsifiable criterion.

Three clusters:
  deliberation  — dynamics of decision-making (審議動態)
  interiority   — agent subjective states (主體性狀態)
  propagation   — principle spread across agent generations (原則傳播)

Roles (borrowed from PSE structure, reseated in governance):
  主導 (driver)    — sets the direction of a governance move
  催化 (catalyst)  — accelerates or surfaces what's latent
  約束 (constraint) — sets the boundary that must not be crossed
"""

from .element import GSEElement
from .registry import GSERegistry

__all__ = ["GSEElement", "GSERegistry"]
__ts_layer__ = "governance"
__ts_purpose__ = "Governance Semantic Engine: operatable ontology for governance elements."
