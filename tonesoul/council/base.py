"""Council base: abstract perspective interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

from .types import PerspectiveType, PerspectiveVote

if TYPE_CHECKING:
    from .epistemic_labeler import EpistemicLabel

__ts_layer__ = "shared"
__ts_purpose__ = "Abstract IPerspective contract implemented by every council perspective."


class IPerspective(ABC):
    @property
    @abstractmethod
    def perspective_type(self) -> Union[PerspectiveType, str]: ...

    @abstractmethod
    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
        epistemic_label: Optional["EpistemicLabel"] = None,
    ) -> PerspectiveVote:
        """Evaluate a draft and return a PerspectiveVote.

        PR #50 (epistemic_label wiring): adds optional `epistemic_label` kwarg.
        Perspectives that consume the label (Analyst, Critic per ratified §3.1)
        use it as a soft prior when their other branches do not fire.
        Perspectives that do not consume (Guardian, Advocate, Axiomatic) accept
        the kwarg without using it for backward compat — adding it does not
        change their behaviour.
        """
