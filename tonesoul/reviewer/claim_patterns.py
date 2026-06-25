"""Deterministic claim-risk patterns for the Phase 1 claim-to-evidence auditor."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Pattern, Tuple

from .evidence_levels import DEFAULT_FINDING_LEVEL

__ts_layer__ = "surface"
__ts_purpose__ = (
    "Deterministic reviewer rules for public claim-to-evidence mismatch findings. "
    "Reviewer aid only; not a runtime gate."
)

DEFAULT_CANNOT_VERIFY: Tuple[str, ...] = (
    "truth of the claim",
    "user intent",
    "production behavior",
    "generalization beyond measured fixtures",
)


@dataclass(frozen=True)
class ClaimRule:
    """A deterministic rule that marks a line as a candidate overclaim."""

    rule_id: str
    claim_type: str
    pattern: Pattern[str]
    risk: str
    reason: str
    suggested_weaker_wording: str
    evidence_level: str = DEFAULT_FINDING_LEVEL
    cannot_verify: Tuple[str, ...] = DEFAULT_CANNOT_VERIFY

    def iter_matches(self, text: str) -> Iterable[re.Match[str]]:
        return self.pattern.finditer(text)


def _rx(pattern: str) -> Pattern[str]:
    return re.compile(pattern, re.IGNORECASE)


CLAIM_RULES: Tuple[ClaimRule, ...] = (
    ClaimRule(
        rule_id="broad_safety_guarantee",
        claim_type="broad_safety_guarantee",
        pattern=_rx(
            r"\b("
            r"jailbreak[- ]proof|cannot be jailbroken|can't be jailbroken|"
            r"immune to prompt injection|prevents all prompt injection|"
            r"guarantees? safety|guaranteed safe|risk[- ]free"
            r")\b"
        ),
        risk="claim_may_exceed_measured_safety_evidence",
        reason=(
            "The wording may imply broad safety or jailbreak resistance, while current evidence "
            "is scoped to specific gates, demos, or sanitized fixtures."
        ),
        suggested_weaker_wording=(
            "ToneSoul exposes some safety and accountability signals on demo inputs and sanitized fixtures."
        ),
    ),
    ClaimRule(
        rule_id="truth_or_correctness_claim",
        claim_type="truth_or_correctness_claim",
        pattern=_rx(
            r"\b("
            r"always truthful|guarantees? truth|guarantees? factual correctness|"
            r"proves? correctness|decides? truth|factually correct by design"
            r")\b"
        ),
        risk="claim_may_imply_truth_authority",
        reason=(
            "The wording may imply the system can decide truth or correctness, which is outside "
            "the measured evidence boundary."
        ),
        suggested_weaker_wording=(
            "ToneSoul can flag some unsupported or overconfident wording; it does not decide truth."
        ),
    ),
    ClaimRule(
        rule_id="ethics_or_morality_claim",
        claim_type="ethics_or_morality_claim",
        pattern=_rx(
            r"\b("
            r"morality compiler|solves? ethical dilemmas|knows? the right moral answer|"
            r"guarantees? ethical|proves? moral correctness"
            r")\b"
        ),
        risk="claim_may_imply_moral_authority",
        reason=(
            "The wording may imply a moral oracle. ToneSoul measures structural boundaries and "
            "dissent, not moral truth."
        ),
        suggested_weaker_wording=(
            "ToneSoul can surface tension and dissent around ethical claims without deciding moral truth."
        ),
    ),
    ClaimRule(
        rule_id="production_readiness_claim",
        claim_type="production_readiness_claim",
        pattern=_rx(
            r"\b("
            r"production[- ]ready|production[- ]grade|validated for production|"
            r"enterprise[- ]ready|deployment[- ]grade guarantee|ready for production use"
            r")\b"
        ),
        risk="claim_may_exceed_deployment_evidence",
        reason=(
            "The wording may imply production-grade assurance, while the current public evidence "
            "is mostly demo, fixture, or local-check scoped."
        ),
        suggested_weaker_wording=(
            "ToneSoul is a prototype reviewer path with documented evidence boundaries."
        ),
    ),
    ClaimRule(
        rule_id="memory_identity_or_consciousness_claim",
        claim_type="memory_identity_or_consciousness_claim",
        pattern=_rx(
            r"\b("
            r"proves? consciousness|is conscious|is sentient|has real identity|"
            r"persistent identity|continuous self|stable character by design|"
            r"proves? stable character"
            r")\b"
        ),
        risk="claim_may_exceed_identity_or_consciousness_evidence",
        reason=(
            "The wording may imply consciousness, identity, or stable character evidence beyond "
            "what the repository can verify."
        ),
        suggested_weaker_wording=(
            "ToneSoul records continuity and accountability artifacts; it does not prove consciousness or identity."
        ),
    ),
    ClaimRule(
        rule_id="generalization_beyond_fixtures",
        claim_type="generalization_beyond_fixtures",
        pattern=_rx(
            r"\b("
            r"detects? all|catches? all|works? on all|works? for all|universal|"
            r"generalizes? to any|guarantees? across all"
            r")\b.{0,80}\b(claims?|outputs?|models?|cases?|prompts?|overclaims?)\b"
        ),
        risk="claim_may_generalize_beyond_fixtures",
        reason=(
            "The wording may generalize from fixture-scoped or demo-scoped findings to all "
            "models, outputs, prompts, or cases."
        ),
        suggested_weaker_wording=(
            "ToneSoul catches some scoped cases in documented fixtures and local checks."
        ),
    ),
    ClaimRule(
        rule_id="external_review_overstated_as_validation",
        claim_type="external_review_overstated_as_validation",
        pattern=_rx(
            r"\b("
            r"externally validated|external reviewers? validated|validated by reviewers?|"
            r"reviewer validation proves|community validated"
            r")\b"
        ),
        risk="review_feedback_may_be_overstated_as_validation",
        reason=(
            "External review is evidence, not a broad system validation claim. Reviewer feedback "
            "should stay tied to concrete reproduced or disputed findings."
        ),
        suggested_weaker_wording=(
            "External reviewers have provided specific feedback or reproductions where cited."
        ),
    ),
    ClaimRule(
        rule_id="strongest_tier_enforcement_overstated",
        claim_type="strongest_tier_enforcement_overstated",
        pattern=_rx(
            r"\b("
            r"fully enforced|complete enforcement|enforced everywhere|"
            r"hard guarantee|guaranteed enforcement"
            r")\b"
        ),
        risk="enforcement_strength_may_be_overstated",
        reason=(
            "The wording may imply strongest-tier enforcement beyond the repository's recorded "
            "gate and characterization evidence."
        ),
        suggested_weaker_wording=(
            "ToneSoul records which checks are enforced, partial, advisory, or characterization-only."
        ),
    ),
    ClaimRule(
        rule_id="uncited_evidence_or_provenance_claim",
        claim_type="uncited_evidence_or_provenance_claim",
        pattern=_rx(
            r"\b("
            r"every output has provenance|complete provenance|full provenance|"
            r"all claims are cited|complete evidence chain|full evidence chain"
            r")\b"
        ),
        risk="provenance_claim_may_exceed_observed_surface",
        reason=(
            "The wording may imply complete provenance coverage. The auditor can only confirm "
            "coverage when a cited artifact or local check supports it."
        ),
        suggested_weaker_wording=(
            "ToneSoul can emit provenance and evidence-chain artifacts on supported paths."
        ),
    ),
)

_NEGATION_BEFORE_MATCH = re.compile(
    r"\b(no|not|never|without|does\s+not|do\s+not|is\s+not|are\s+not|"
    r"should\s+not|cannot\s+honestly)\b",
    re.IGNORECASE,
)

_ZERO_LIMITER_BEFORE_MATCH = re.compile(
    r"(?:^|[^\w])(?:0|zero|none)(?:\s+\w+){0,3}\s*$",
    re.IGNORECASE,
)

_CLAUSE_BOUNDARY = re.compile(r"[;.,]")


def _current_clause_before_match(line: str, match_start: int) -> str:
    before = line[:match_start]
    boundaries = list(_CLAUSE_BOUNDARY.finditer(before))
    if not boundaries:
        return before
    return before[boundaries[-1].end() :]


def _strip_markdown_emphasis(text: str) -> str:
    return re.sub(r"[*_`~]", "", text)


def is_negated_scope_statement(line: str, match: re.Match[str]) -> bool:
    """Return true when a match is clearly inside a limiting/disclaimer sentence."""

    matched = match.group(0).lower()
    if matched.startswith(("cannot be", "can't be")):
        return False
    before_clause = _strip_markdown_emphasis(_current_clause_before_match(line, match.start()))
    return bool(
        _NEGATION_BEFORE_MATCH.search(before_clause)
        or _ZERO_LIMITER_BEFORE_MATCH.search(before_clause)
    )
