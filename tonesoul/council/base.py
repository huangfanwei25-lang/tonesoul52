"""Council base: abstract perspective interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union

from .types import PerspectiveType, PerspectiveVote

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
    ) -> PerspectiveVote: ...
