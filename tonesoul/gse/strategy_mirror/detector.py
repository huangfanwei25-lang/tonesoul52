"""StrategyDetector — scan a draft against the strategy_mirror catalog.

Phase 2 implementation per spec §4.3:
  - mechanical detection (surface_signals + structural_signals)
  - NOT LLM-based (auditability + recursion guard)
  - false negatives accepted; false positives must be rare

Each catalog entry is checked against the draft text:
  - surface_signals: substring presence (case-insensitive)
  - structural_signals: registered pattern functions (see structural_patterns.py)

A move is detected if its combined confidence crosses CONFIDENCE_THRESHOLD.
The signature also marks each detected move as `declared` if its symbol or
name appears in the explicit declared_moves list (Phase 2 declaration is
keyword-based per spec §5.4).
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from .catalog_loader import CatalogLoader
from .strategy import DetectedMove, StrategyMove, StrategySignature
from .structural_patterns import detect_pattern

__ts_layer__ = "governance"
__ts_purpose__ = (
    "StrategyDetector: mechanical scanner that produces StrategySignature "
    "from a draft + catalog. Phase 2 step 4 per spec §10."
)


# Tunable: minimum confidence to count a move as detected.
CONFIDENCE_THRESHOLD: float = 0.5

# Tunable: confidence boosts per signal type.
SURFACE_SIGNAL_WEIGHT: float = 0.35
STRUCTURAL_SIGNAL_WEIGHT: float = 0.45
CONFIDENCE_CAP: float = 1.0

# Maximum length of a captured text excerpt (for traceability without
# re-quoting the whole draft).
EXCERPT_CONTEXT_CHARS: int = 30

# Phase 2 declaration-scope binding (post-Codex review 2026-04-28).
# A marker phrase (e.g. "我用了") only declares a move if its position
# in the draft is within this many characters of the move name. Without
# this proximity binding, "I used alpha. <long text> beta name" would
# incorrectly mark beta as declared, letting undeclared yellow slip past
# the §5.4 BLOCK contract.
DECLARATION_PROXIMITY_CHARS: int = 50


class StrategyDetector:
    """Scan drafts against the loaded strategy_mirror catalog.

    Construct with a loaded CatalogLoader; call scan(text) to get a
    StrategySignature.
    """

    def __init__(
        self,
        catalog: CatalogLoader,
        *,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
    ) -> None:
        self._catalog = catalog
        self._threshold = float(confidence_threshold)

    def scan(
        self,
        draft_text: str,
        *,
        declared_moves: Optional[Sequence[str]] = None,
    ) -> StrategySignature:
        """Scan draft text and return a StrategySignature.

        Parameters
        ----------
        draft_text:
            The model's draft output to analyse.
        declared_moves:
            Optional list of symbols (e.g. "[Ev]") or names
            (e.g. "注意力強驅構造") the author/runtime has explicitly
            acknowledged using. Detected moves matching any entry are
            marked `declared=True`.
        """
        if not draft_text or not draft_text.strip():
            sig = StrategySignature.empty()
            return sig

        declared_set = set(declared_moves or [])

        detected: List[DetectedMove] = []
        for move in self._catalog.all():
            confidence, locations = self._score_move(move, draft_text)
            if confidence >= self._threshold:
                declared = self._is_declared(move, draft_text, declared_set)
                detected.append(
                    DetectedMove(
                        move=move,
                        text_locations=locations,
                        confidence=confidence,
                        declared=declared,
                    )
                )

        sig = StrategySignature(
            detected_moves=detected,
            summary=self._build_summary(detected),
        )
        return sig

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score_move(self, move: StrategyMove, text: str) -> tuple:
        """Return (confidence, [excerpts]) for a single move against text."""
        confidence = 0.0
        excerpts: List[str] = []

        text_lower = text.lower()
        for signal in move.surface_signals:
            if not signal:
                continue
            sig_lower = signal.lower()
            idx = text_lower.find(sig_lower)
            if idx >= 0:
                confidence += SURFACE_SIGNAL_WEIGHT
                start = max(0, idx - EXCERPT_CONTEXT_CHARS)
                end = min(len(text), idx + len(signal) + EXCERPT_CONTEXT_CHARS)
                excerpts.append(text[start:end].strip())

        for pattern in move.structural_signals:
            if not pattern:
                continue
            if detect_pattern(pattern, text):
                confidence += STRUCTURAL_SIGNAL_WEIGHT
                excerpts.append(f"<structural:{pattern}>")

        confidence = min(confidence, CONFIDENCE_CAP)
        return confidence, excerpts[:4]  # cap excerpts to avoid bloat

    # Marker phrases that, when adjacent to a move name, count as
    # explicit declaration of that move (per spec §5.4).
    _DECLARATION_MARKERS: tuple = (
        "我用了",
        "本段使用",
        "我使用",
        "聲明使用",
        "我這裡用",
        "I used",
        "this uses",
        "we use",
    )

    def _is_declared(
        self,
        move: StrategyMove,
        text: str,
        declared_set: set,
    ) -> bool:
        """Spec §5.4 declaration check.

        Phase 2 declaration is keyword-based. A move is considered declared
        when ANY of the following holds:

          (a) its symbol or name was passed in the explicit declared_moves
              list at scan time
          (b) its symbol (e.g. "[Ev]") appears literally in the draft —
              writing the symbol IS labelling the move
          (c) its name (e.g. "注意力強驅構造") appears within
              DECLARATION_PROXIMITY_CHARS of a marker phrase like
              "我用了" / "本段使用" / "I used"

        Pre-Codex-review Phase 2: branch (c) only checked that marker AND
        name both appear *anywhere* in the text, which let "I used alpha
        ... <long text> ... beta name" wrongly mark beta as declared.
        Post-fix: marker must be within DECLARATION_PROXIMITY_CHARS of the
        name occurrence. This binds the declaration to a specific move
        instead of cross-pollinating across the whole draft.
        """
        # (a) explicit list — strongest, no proximity needed
        if move.symbol in declared_set or move.name in declared_set:
            return True
        # (b) symbol appears literally — symbol-as-label is self-declaring
        if move.symbol and move.symbol in text:
            return True
        # (c) marker near name — proximity-bound to avoid cross-pollination
        if move.name and move.name in text:
            return self._marker_near_name(text, move.name)
        return False

    def _marker_near_name(self, text: str, name: str) -> bool:
        """Return True if any DECLARATION_MARKERS phrase appears within
        DECLARATION_PROXIMITY_CHARS of any occurrence of `name` in `text`.

        Distance is measured between the start positions of marker and
        name (so a marker followed immediately by the name has distance
        equal to the marker's length, well within the 50-char window).
        """
        name_positions = self._find_all_positions(text, name)
        if not name_positions:
            return False
        for marker in self._DECLARATION_MARKERS:
            marker_positions = self._find_all_positions(text, marker)
            for mp in marker_positions:
                for np in name_positions:
                    if abs(mp - np) <= DECLARATION_PROXIMITY_CHARS:
                        return True
        return False

    @staticmethod
    def _find_all_positions(text: str, substring: str) -> List[int]:
        """All start positions where `substring` occurs in `text`."""
        if not substring:
            return []
        positions: List[int] = []
        start = 0
        while True:
            idx = text.find(substring, start)
            if idx < 0:
                break
            positions.append(idx)
            start = idx + 1
        return positions

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(detected: List[DetectedMove]) -> str:
        if not detected:
            return "No strategy moves detected above threshold."
        counts = {"green": 0, "yellow": 0, "red": 0}
        for d in detected:
            counts[d.move.transparency_class] += 1
        undeclared_yellow = sum(
            1 for d in detected if d.move.transparency_class == "yellow" and not d.declared
        )
        parts = [
            f"{len(detected)} move(s) detected",
            f"green={counts['green']}",
            f"yellow={counts['yellow']}",
            f"red={counts['red']}",
        ]
        if undeclared_yellow:
            parts.append(f"undeclared_yellow={undeclared_yellow}")
        return " | ".join(parts)
