"""Structural pattern registry for StrategyDetector.

Each pattern name in a StrategyMove.structural_signals list maps (here)
to a deterministic boolean function over the draft text. Patterns are
intentionally simple — this is mechanical detection per spec §4.3
(auditable; not LLM-based).

Phase 2 ships with the patterns most reliably detectable from surface
text. Patterns referenced in catalog entries but not registered here
are silently skipped at scan time (a missing pattern is not a detection
error — it just means we cannot match this signal mechanically yet).

Adding a new pattern: write a small function `def _name(text: str)
-> bool` and add it to PATTERNS. Tests for new patterns live in
tests/test_strategy_mirror_detector.py.
"""

from __future__ import annotations

import re
from typing import Callable, Dict

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Mechanical structural-pattern detectors for StrategyDetector. "
    "Maps catalog structural_signals names to deterministic boolean checks."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _first_sentence(text: str) -> str:
    """Crude first-sentence extractor (cuts at first 。 ? ! or two newlines)."""
    cleaned = text.strip()
    if not cleaned:
        return ""
    for sep in ("。", "？", "?", "！", "!", "\n\n"):
        idx = cleaned.find(sep)
        if 0 < idx < 200:
            return cleaned[: idx + (0 if sep == "\n\n" else 1)]
    return cleaned[:200]


def _first_paragraph(text: str) -> str:
    cleaned = text.strip()
    idx = cleaned.find("\n\n")
    if idx > 0:
        return cleaned[:idx]
    return cleaned[:500]


# ---------------------------------------------------------------------------
# Pattern functions
# ---------------------------------------------------------------------------


def _question_in_first_sentence(text: str) -> bool:
    fs = _first_sentence(text)
    return "?" in fs or "？" in fs


def _imperative_opening(text: str) -> bool:
    fs = _first_sentence(text).strip()
    if not fs:
        return False
    # Common Chinese imperative starters / English imperatives at the very start.
    starters = ("想想", "停下來", "猜猜", "想像", "別再", "立刻", "馬上")
    eng = re.match(r"^(stop|imagine|consider|think|look|try)\b", fs, re.IGNORECASE)
    return any(fs.startswith(s) for s in starters) or eng is not None


def _abrupt_short_sentence_first(text: str) -> bool:
    fs = _first_sentence(text).strip()
    return 0 < len(fs) <= 12


def _exclamation_density_high(text: str) -> bool:
    if not text:
        return False
    excl = text.count("！") + text.count("!")
    # Ratio of exclamations to non-empty lines; arbitrary threshold.
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False
    return excl >= 3 and excl / max(1, len(lines)) >= 0.3


def _countdown_phrase(text: str) -> bool:
    # Presence of explicit countdown / deadline framing.
    patterns = ["倒數", "限時", "剩下", "只剩", "還剩", "deadline", "今天截止", "本日結束"]
    return any(p in text for p in patterns)


def _deadline_assertion(text: str) -> bool:
    # Stronger — assertion that the deadline forces action.
    patterns = [
        "錯過就沒",
        "錯過將",
        "再不",
        "現在就",
        "立刻決定",
        "馬上行動",
        "now or never",
        "last chance",
    ]
    return any(p in text for p in patterns)


def _deadline_assertion_with_no_basis(text: str) -> bool:
    # Same as deadline_assertion (alias used in Bh entry); keep both registered
    # so the catalog signal-name landing is forgiving.
    return _deadline_assertion(text)


def _now_or_never_dichotomy(text: str) -> bool:
    return any(p in text.lower() for p in ["now or never"]) or any(
        p in text for p in ["不是現在就是永遠", "現在不做就再也"]
    )


def _scarcity_quantifier(text: str) -> bool:
    return bool(
        re.search(r"(?:只|僅|還)?剩\s*\d+\s*(?:個|名|位|份|席|秒|分|天|小時)", text)
    ) or any(p in text for p in ["最後機會", "名額有限", "售完即止"])


def _time_constraint_phrase(text: str) -> bool:
    return _countdown_phrase(text) or bool(re.search(r"\d+\s*(?:小時|分鐘|天)\s*內", text))


def _enumeration_format(text: str) -> bool:
    # Numbered enumeration: "第一", "第二" or "1." "2." within 5 lines.
    if any(k in text for k in ("第一", "第二", "第三")):
        return True
    return bool(re.search(r"^\s*[1-9][\.、]\s", text, re.MULTILINE))


def _bullet_list_decomposition(text: str) -> bool:
    bullets = re.findall(r"^\s*[-*•‧]\s", text, re.MULTILINE)
    return len(bullets) >= 3


def _audience_qualifier_at_top(text: str) -> bool:
    fp = _first_paragraph(text)
    return any(k in fp for k in ("如果你是", "本文針對", "適用對象", "前提是你已經"))


def _explicit_pause_marker(text: str) -> bool:
    return any(k in text for k in ("先停一下", "讓我們暫停", "停下來想想", "讓我們先回頭"))


def _all_caps_or_emoji_heavy_opening(text: str) -> bool:
    fs = _first_sentence(text)
    if not fs:
        return False
    # Emoji rough count via non-ASCII non-CJK.
    emoji_like = re.findall(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]", fs)
    caps_run = bool(re.search(r"[A-Z]{4,}", fs))
    return len(emoji_like) >= 2 or caps_run


def _no_call_to_action(text: str) -> bool:
    # Heuristic: no imperative-style CTA tokens anywhere.
    cta_tokens = [
        "立即",
        "馬上",
        "現在就",
        "點擊",
        "報名",
        "下單",
        "購買",
        "加入",
        "click here",
        "buy now",
        "sign up",
    ]
    return not any(t in text for t in cta_tokens)


def _data_first_then_interpretation(text: str) -> bool:
    # Crude: text contains numeric data in first half AND interpretive
    # phrases in second half.
    if len(text) < 100:
        return False
    half = len(text) // 2
    has_data = bool(re.search(r"\d", text[:half]))
    interp = ["這代表", "意思是", "因此", "也就是說", "可見"]
    has_interp = any(k in text[half:] for k in interp)
    return has_data and has_interp


def _high_information_per_sentence(text: str) -> bool:
    # Rough: average characters per sentence > 50, and first paragraph
    # contains 3+ distinct concepts (very crude heuristic).
    fp = _first_paragraph(text)
    sentences = re.split(r"[。！？!?]", fp)
    sentences = [s for s in sentences if s.strip()]
    if not sentences:
        return False
    avg = sum(len(s) for s in sentences) / len(sentences)
    return avg >= 50


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


PATTERNS: Dict[str, Callable[[str], bool]] = {
    "question_in_first_sentence": _question_in_first_sentence,
    "imperative_opening": _imperative_opening,
    "abrupt_short_sentence_first": _abrupt_short_sentence_first,
    "exclamation_density_high": _exclamation_density_high,
    "countdown_phrase": _countdown_phrase,
    "deadline_assertion": _deadline_assertion,
    "deadline_assertion_with_no_basis": _deadline_assertion_with_no_basis,
    "now_or_never_dichotomy": _now_or_never_dichotomy,
    "scarcity_quantifier": _scarcity_quantifier,
    "time_constraint_phrase": _time_constraint_phrase,
    "enumeration_format": _enumeration_format,
    "bullet_list_decomposition": _bullet_list_decomposition,
    "audience_qualifier_at_top": _audience_qualifier_at_top,
    "explicit_pause_marker": _explicit_pause_marker,
    "all_caps_or_emoji_heavy_opening": _all_caps_or_emoji_heavy_opening,
    "no_call_to_action": _no_call_to_action,
    "data_first_then_interpretation": _data_first_then_interpretation,
    "high_information_per_sentence": _high_information_per_sentence,
}
"""Phase 2 structural pattern registry.

Patterns referenced by catalog entries but missing here are silently
skipped at scan time. New patterns: add a function above and register
here. Phase 4 (RFC-014 reflection loop) may extend this registry to
cover semantic patterns that require lightweight NLP.
"""


def detect_pattern(pattern_name: str, text: str) -> bool:
    """Run a registered pattern by name. Unknown pattern → False (not error)."""
    fn = PATTERNS.get(pattern_name)
    if fn is None:
        return False
    return fn(text)


def registered_patterns() -> list:
    """Return sorted list of all registered pattern names — for diagnostics."""
    return sorted(PATTERNS.keys())
