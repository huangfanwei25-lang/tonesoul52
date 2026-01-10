from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .types import PerspectiveType, PerspectiveVote


class IPerspective(ABC):
    @property
    @abstractmethod
    def perspective_type(self) -> PerspectiveType:
        ...

    @abstractmethod
    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
    ) -> PerspectiveVote:
        ...
