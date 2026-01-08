
from enum import Enum

class Dimension(Enum):
    """
    The 5 Governance Dimensions (Standard Spec).
    Ref: docs/DIMENSIONS.md
    """
    STABILITY = "S"
    TENSION = "T"
    RESPONSIBILITY = "R"
    ETHICS = "E"
    INTENT = "I"

class Grade(Enum):
    """
    Human-facing Grades.
    Ref: docs/DIMENSIONS.md
    """
    LOW = "LOW"
    MID = "MID"
    HIGH = "HIGH"

class PolicyRoot(Enum):
    """
    Core Policy Roots.
    Ref: body/law/
    """
    PRIVACY = "P0_PRIVACY"
    AXIOM = "AXIOM"
    SAFEGUARD = "P1_SAFEGUARD"

class NarrativeTerm(Enum):
    """
    Terms allowed ONLY in Narrative Layer.
    Ref: docs/NARRATIVE_LAYER.md
    """
    SOUL = "Soul"
    AWAKENED = "Awakened"
    COMPASSION = "Compassion"
    FIELD = "ToneField"
