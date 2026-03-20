from __future__ import annotations

from collections import deque
from typing import Optional, Protocol, runtime_checkable

from .types import NegotiationOutcome, RuptureNotice, SovereigntyBoundary, TensionPacket


def _clone_packet(packet: TensionPacket) -> TensionPacket:
    return TensionPacket.from_dict(packet.to_dict())


def _clone_notice(notice: RuptureNotice) -> RuptureNotice:
    return RuptureNotice.from_dict(notice.to_dict())


@runtime_checkable
class InterSoulBridge(Protocol):
    def share_tension(self, packet: TensionPacket) -> None: ...

    def receive_tension(self) -> Optional[TensionPacket]: ...

    def propagate_rupture(self, notice: RuptureNotice) -> None: ...

    def negotiate(
        self,
        local: TensionPacket,
        remote: TensionPacket,
        boundary: SovereigntyBoundary,
    ) -> NegotiationOutcome: ...


class LocalInterSoulBridge:
    """In-memory bridge that preserves a visible audit trail of exchanged tension."""

    def __init__(self) -> None:
        self._pending_packets: deque[TensionPacket] = deque()
        self._tension_history: list[TensionPacket] = []
        self._rupture_history: list[RuptureNotice] = []

    @property
    def tension_history(self) -> list[TensionPacket]:
        return [_clone_packet(packet) for packet in self._tension_history]

    @property
    def rupture_history(self) -> list[RuptureNotice]:
        return [_clone_notice(notice) for notice in self._rupture_history]

    def share_tension(self, packet: TensionPacket) -> None:
        stored = _clone_packet(packet)
        self._pending_packets.append(stored)
        self._tension_history.append(_clone_packet(stored))

    def receive_tension(self) -> Optional[TensionPacket]:
        if not self._pending_packets:
            return None
        return _clone_packet(self._pending_packets.popleft())

    def propagate_rupture(self, notice: RuptureNotice) -> None:
        self._rupture_history.append(_clone_notice(notice))

    def negotiate(
        self,
        local: TensionPacket,
        remote: TensionPacket,
        boundary: SovereigntyBoundary,
    ) -> NegotiationOutcome:
        from .negotiation import TensionNegotiator

        return TensionNegotiator(boundary).negotiate(local, remote).outcome
