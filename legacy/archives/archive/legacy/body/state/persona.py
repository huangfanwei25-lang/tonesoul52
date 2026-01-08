
from dataclasses import dataclass

@dataclass
class CPM:
    """
    The Narrative Vector for ToneSoul.
    Used for Tone, Persona consistency, and Creative flavor.
    NO Governance Power.
    """
    Compassion: float = 0.5       # C: Empathy warmth level
    Precision: float = 0.5        # P: Technical accuracy vs poetic license
    MultiPerspective: float = 0.5 # M: Diversity of viewpoints

    def to_dict(self):
        return {
            "C": self.Compassion,
            "P": self.Precision,
            "M": self.MultiPerspective
        }

    def __repr__(self):
        return f"CPM(C={self.Compassion:.2f}, P={self.Precision:.2f}, M={self.MultiPerspective:.2f})"

class PersonaState:
    """
    L1 State Layer (Narrative Side).
    Maintains the 'Soul's Tone'.
    """
    def __init__(self):
        self.current_tone = CPM()

    def update_tone(self, context: str):
        """
        Adjusts tone based on context (e.g., if user is sad, increase Compassion).
        """
        # Placeholder logic
        pass
