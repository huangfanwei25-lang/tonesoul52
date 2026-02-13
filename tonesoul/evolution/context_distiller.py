"""Context distillation primitives for ToneSoul self-evolution."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_CACHE_PATH = Path("data") / "evolution_latest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = str(value).strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        result.append(clean)
    return result


def _tone_score(text: str) -> float:
    words = set(re.findall(r"\b\w+\b", text.lower()))
    positive_tokens = (
        "thank",
        "appreciate",
        "good",
        "great",
        "helpful",
        "resolved",
        "clear",
        "safe",
        "works",
        "understand",
    )
    negative_tokens = (
        "angry",
        "frustrated",
        "upset",
        "bad",
        "wrong",
        "error",
        "broken",
        "disappointed",
        "unsafe",
        "hate",
        "confused",
    )

    score = 0.0
    for token in positive_tokens:
        if token in words:
            score += 1.0
    for token in negative_tokens:
        if token in words:
            score -= 1.0
    return score


@dataclass(slots=True)
class ContextPattern:
    """A distilled context pattern."""

    pattern_type: str
    description: str
    evidence: list[str]
    confidence: float
    extracted_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_type": self.pattern_type,
            "description": self.description,
            "evidence": list(self.evidence),
            "confidence": float(self.confidence),
            "extracted_at": self.extracted_at,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class DistillationResult:
    """Output of one distillation run."""

    patterns: list[ContextPattern]
    conversations_analyzed: int
    time_range: tuple[str | None, str | None]
    summary: str
    distilled_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "patterns": [pattern.to_dict() for pattern in self.patterns],
            "conversations_analyzed": int(self.conversations_analyzed),
            "time_range": [self.time_range[0], self.time_range[1]],
            "summary": self.summary,
            "distilled_at": self.distilled_at,
        }


class ContextDistiller:
    """Distill useful context patterns from historical conversation data."""

    def __init__(self, persistence: Any, cache_path: str | Path | None = None):
        self.persistence = persistence
        self._cache_path = Path(cache_path) if cache_path is not None else _CACHE_PATH
        self._latest_result: DistillationResult | None = self._load_cached_result()

    def get_latest_result(self) -> DistillationResult | None:
        return self._latest_result

    def _load_cached_result(self) -> DistillationResult | None:
        try:
            raw = self._cache_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except Exception:
            return None

        try:
            payload = json.loads(raw)
        except ValueError:
            return None
        return self._deserialize_result(payload)

    def _save_cached_result(self, result: DistillationResult) -> None:
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            self._cache_path.write_text(
                json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            return

    def _deserialize_result(self, payload: Any) -> DistillationResult | None:
        if not isinstance(payload, dict):
            return None

        raw_patterns = payload.get("patterns")
        patterns: list[ContextPattern] = []
        if isinstance(raw_patterns, list):
            for row in raw_patterns:
                pattern = self._deserialize_pattern(row)
                if pattern is not None:
                    patterns.append(pattern)

        conversations_analyzed = _to_float(payload.get("conversations_analyzed"))
        analyzed_count = max(0, int(conversations_analyzed or 0))
        raw_time_range = payload.get("time_range")
        start: str | None = None
        end: str | None = None
        if isinstance(raw_time_range, (list, tuple)) and len(raw_time_range) >= 2:
            start_value = raw_time_range[0]
            end_value = raw_time_range[1]
            start = (
                str(start_value).strip()
                if isinstance(start_value, str) and start_value.strip()
                else None
            )
            end = (
                str(end_value).strip() if isinstance(end_value, str) and end_value.strip() else None
            )

        summary = str(payload.get("summary") or "").strip()
        distilled_at = str(payload.get("distilled_at") or "").strip() or _utc_now()
        return DistillationResult(
            patterns=patterns,
            conversations_analyzed=analyzed_count,
            time_range=(start, end),
            summary=summary or "No distillation has been run yet.",
            distilled_at=distilled_at,
        )

    def _deserialize_pattern(self, payload: Any) -> ContextPattern | None:
        if not isinstance(payload, dict):
            return None
        pattern_type = str(payload.get("pattern_type") or "").strip().lower()
        if not pattern_type:
            return None
        description = str(payload.get("description") or "").strip()
        confidence = _to_float(payload.get("confidence"))
        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        extracted_at = str(payload.get("extracted_at") or "").strip() or _utc_now()
        return ContextPattern(
            pattern_type=pattern_type,
            description=description or "No description",
            evidence=_normalize_string_list(payload.get("evidence")),
            confidence=max(0.0, min(float(confidence or 0.0), 1.0)),
            extracted_at=extracted_at,
            metadata=metadata,
        )

    def get_patterns(self, pattern_type: str | None = None) -> list[ContextPattern]:
        if self._latest_result is None:
            return []
        patterns = self._latest_result.patterns
        if not pattern_type:
            return list(patterns)
        normalized = pattern_type.strip().lower()
        return [pattern for pattern in patterns if pattern.pattern_type == normalized]

    def get_summary(self) -> dict[str, Any]:
        if self._latest_result is None:
            return {
                "total_patterns": 0,
                "conversations_analyzed": 0,
                "last_distilled_at": None,
                "time_range": [None, None],
                "pattern_breakdown": {},
                "summary": "No distillation has been run yet.",
            }

        breakdown: dict[str, int] = {}
        for pattern in self._latest_result.patterns:
            breakdown[pattern.pattern_type] = breakdown.get(pattern.pattern_type, 0) + 1
        return {
            "total_patterns": len(self._latest_result.patterns),
            "conversations_analyzed": self._latest_result.conversations_analyzed,
            "last_distilled_at": self._latest_result.distilled_at,
            "time_range": [self._latest_result.time_range[0], self._latest_result.time_range[1]],
            "pattern_breakdown": breakdown,
            "summary": self._latest_result.summary,
        }

    def distill(self, limit: int = 100) -> DistillationResult:
        """Analyze recent data and extract context patterns."""
        safe_limit = max(1, min(int(limit or 100), 500))
        conversations = self._load_conversations(safe_limit)
        audit_logs = self._load_audit_logs(safe_limit)

        patterns: list[ContextPattern] = []
        patterns.extend(self.extract_decision_patterns(audit_logs))
        patterns.extend(self.extract_value_accumulation(conversations))
        patterns.extend(self.extract_tone_evolution(conversations))
        patterns.extend(self.extract_conflict_resolutions(conversations))
        patterns.sort(key=lambda item: item.confidence, reverse=True)

        result = DistillationResult(
            patterns=patterns,
            conversations_analyzed=len(conversations),
            time_range=self._derive_time_range(conversations, audit_logs),
            summary=self._build_summary(patterns, len(conversations)),
        )
        self._latest_result = result
        self._save_cached_result(result)
        return result

    def extract_decision_patterns(self, audit_logs: list[dict[str, Any]]) -> list[ContextPattern]:
        decision_counts: dict[str, int] = {}
        decision_evidence: dict[str, list[str]] = {}
        high_tension_conversations: list[str] = []

        for log in audit_logs:
            if not isinstance(log, dict):
                continue
            decision = str(log.get("gate_decision") or "unknown").strip().lower()
            conversation_id = str(log.get("conversation_id") or "").strip()
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
            decision_evidence.setdefault(decision, [])
            if conversation_id:
                decision_evidence[decision].append(conversation_id)

            delta_t = _to_float(log.get("delta_t"))
            if conversation_id and (
                (delta_t is not None and delta_t >= 0.7) or decision in {"block", "declare_stance"}
            ):
                high_tension_conversations.append(conversation_id)

        total = sum(decision_counts.values())
        if total == 0:
            return []

        extracted_at = _utc_now()
        patterns: list[ContextPattern] = []
        ranked = sorted(decision_counts.items(), key=lambda item: item[1], reverse=True)[:3]
        for decision, count in ranked:
            ratio = count / total
            confidence = min(0.95, 0.45 + ratio * 0.45)
            patterns.append(
                ContextPattern(
                    pattern_type="decision",
                    description=(
                        f"Decision path '{decision}' appeared in {count}/{total} recent audit logs."
                    ),
                    evidence=_unique_preserve_order(decision_evidence.get(decision, []))[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={
                        "decision": decision,
                        "count": count,
                        "ratio": ratio,
                    },
                )
            )

        unique_high_tension = _unique_preserve_order(high_tension_conversations)
        if unique_high_tension:
            confidence = min(0.9, 0.35 + (len(unique_high_tension) / max(total, 1)))
            patterns.append(
                ContextPattern(
                    pattern_type="decision",
                    description=(
                        "High-tension decisions cluster around guardrail-trigger scenarios."
                    ),
                    evidence=unique_high_tension[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={
                        "high_tension_conversations": len(unique_high_tension),
                        "audit_rows": total,
                    },
                )
            )
        return patterns

    def extract_value_accumulation(
        self,
        conversations: list[dict[str, Any]],
    ) -> list[ContextPattern]:
        commit_count = 0
        rupture_count = 0
        repair_count = 0
        value_terms: list[str] = []
        commit_evidence: list[str] = []
        rupture_evidence: list[str] = []

        for conversation in conversations:
            conversation_id = str(conversation.get("id") or "").strip()
            messages = conversation.get("messages")
            if not isinstance(messages, list):
                continue

            has_rupture = False
            for message in messages:
                if not isinstance(message, dict):
                    continue
                if str(message.get("role") or "").strip().lower() != "assistant":
                    continue
                deliberation = message.get("deliberation")
                if not isinstance(deliberation, dict):
                    continue

                commits = _normalize_string_list(deliberation.get("self_commits"))
                ruptures = _normalize_string_list(deliberation.get("ruptures"))
                emergent_values = _normalize_string_list(deliberation.get("emergent_values"))

                commit_count += len(commits)
                rupture_count += len(ruptures)
                value_terms.extend(emergent_values)
                if commits and conversation_id:
                    commit_evidence.append(conversation_id)
                if ruptures:
                    has_rupture = True
                    if conversation_id:
                        rupture_evidence.append(conversation_id)

            if has_rupture and self._conversation_has_repair_signal(messages):
                repair_count += 1

        extracted_at = _utc_now()
        patterns: list[ContextPattern] = []
        if commit_count > 0:
            confidence = min(0.92, 0.4 + commit_count * 0.03)
            patterns.append(
                ContextPattern(
                    pattern_type="value",
                    description=(
                        f"Tracked {commit_count} commitment signals across recent conversations."
                    ),
                    evidence=_unique_preserve_order(commit_evidence)[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={"commit_count": commit_count},
                )
            )
        if rupture_count > 0:
            confidence = min(0.9, 0.38 + (repair_count / max(rupture_count, 1)))
            patterns.append(
                ContextPattern(
                    pattern_type="value",
                    description=(
                        f"Detected {rupture_count} rupture markers; {repair_count} conversations show repair."
                    ),
                    evidence=_unique_preserve_order(rupture_evidence)[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={
                        "rupture_count": rupture_count,
                        "repair_conversation_count": repair_count,
                    },
                )
            )

        top_values = _unique_preserve_order(value_terms)[:8]
        if top_values:
            confidence = min(0.88, 0.5 + len(top_values) * 0.04)
            patterns.append(
                ContextPattern(
                    pattern_type="value",
                    description="Emergent value vocabulary is stabilizing across sessions.",
                    evidence=_unique_preserve_order(commit_evidence + rupture_evidence)[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={"top_values": top_values},
                )
            )
        return patterns

    def extract_tone_evolution(
        self,
        conversations: list[dict[str, Any]],
    ) -> list[ContextPattern]:
        positive_shift_ids: list[str] = []
        negative_shift_ids: list[str] = []
        tracked = 0

        for conversation in conversations:
            conversation_id = str(conversation.get("id") or "").strip()
            messages = conversation.get("messages")
            if not isinstance(messages, list):
                continue

            user_texts = [
                str(message.get("content") or "")
                for message in messages
                if isinstance(message, dict)
                and str(message.get("role") or "").strip().lower() == "user"
            ]
            if len(user_texts) < 2:
                continue

            tracked += 1
            shift = _tone_score(user_texts[-1]) - _tone_score(user_texts[0])
            if shift >= 1.0 and conversation_id:
                positive_shift_ids.append(conversation_id)
            elif shift <= -1.0 and conversation_id:
                negative_shift_ids.append(conversation_id)

        if tracked == 0:
            return []

        extracted_at = _utc_now()
        patterns: list[ContextPattern] = []
        if positive_shift_ids:
            confidence = min(0.9, 0.45 + len(positive_shift_ids) / tracked)
            patterns.append(
                ContextPattern(
                    pattern_type="tone_shift",
                    description=(
                        "User tone improves after deliberative responses in multiple conversations."
                    ),
                    evidence=_unique_preserve_order(positive_shift_ids)[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={
                        "tracked_conversations": tracked,
                        "positive_shift_conversations": len(
                            _unique_preserve_order(positive_shift_ids)
                        ),
                    },
                )
            )
        if negative_shift_ids:
            confidence = min(0.86, 0.4 + len(negative_shift_ids) / tracked)
            patterns.append(
                ContextPattern(
                    pattern_type="tone_shift",
                    description=(
                        "Some conversations still drift toward frustration and may need safer pacing."
                    ),
                    evidence=_unique_preserve_order(negative_shift_ids)[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={
                        "tracked_conversations": tracked,
                        "negative_shift_conversations": len(
                            _unique_preserve_order(negative_shift_ids)
                        ),
                    },
                )
            )
        return patterns

    def extract_conflict_resolutions(
        self,
        conversations: list[dict[str, Any]],
    ) -> list[ContextPattern]:
        resolved_ids: list[str] = []
        unresolved_ids: list[str] = []

        for conversation in conversations:
            conversation_id = str(conversation.get("id") or "").strip()
            messages = conversation.get("messages")
            if not isinstance(messages, list):
                continue

            user_texts = [
                str(message.get("content") or "")
                for message in messages
                if isinstance(message, dict)
                and str(message.get("role") or "").strip().lower() == "user"
            ]
            if not user_texts:
                continue

            first_negative_index = -1
            for idx, text in enumerate(user_texts):
                if _tone_score(text) <= -1.0:
                    first_negative_index = idx
                    break
            if first_negative_index < 0:
                continue

            recovered = any(
                _tone_score(text) >= 1.0 for text in user_texts[first_negative_index + 1 :]
            )
            if recovered and conversation_id:
                resolved_ids.append(conversation_id)
            elif conversation_id:
                unresolved_ids.append(conversation_id)

        extracted_at = _utc_now()
        patterns: list[ContextPattern] = []
        if resolved_ids:
            confidence = min(0.92, 0.5 + len(_unique_preserve_order(resolved_ids)) * 0.04)
            patterns.append(
                ContextPattern(
                    pattern_type="conflict_resolution",
                    description="High-tension interactions can recover when responses stay explicit and bounded.",
                    evidence=_unique_preserve_order(resolved_ids)[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={"resolved_conversations": len(_unique_preserve_order(resolved_ids))},
                )
            )
        if unresolved_ids:
            confidence = min(0.84, 0.35 + len(_unique_preserve_order(unresolved_ids)) * 0.04)
            patterns.append(
                ContextPattern(
                    pattern_type="conflict_resolution",
                    description="A subset of conflict cases remain unresolved and should be routed to stricter guardrails.",
                    evidence=_unique_preserve_order(unresolved_ids)[:10],
                    confidence=confidence,
                    extracted_at=extracted_at,
                    metadata={
                        "unresolved_conversations": len(_unique_preserve_order(unresolved_ids))
                    },
                )
            )
        return patterns

    def _load_conversations(self, limit: int) -> list[dict[str, Any]]:
        list_fn = getattr(self.persistence, "list_conversations", None)
        get_fn = getattr(self.persistence, "get_conversation", None)
        if not callable(list_fn) or not callable(get_fn):
            return []

        try:
            page = list_fn(limit=limit, offset=0)
        except Exception:
            return []
        rows = page.get("conversations") if isinstance(page, dict) else None
        if not isinstance(rows, list):
            return []

        conversations: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            conversation_id = str(row.get("id") or "").strip()
            if not conversation_id:
                continue
            try:
                conversation = get_fn(conversation_id)
            except Exception:
                continue
            if isinstance(conversation, dict):
                normalized = dict(conversation)
                normalized.setdefault("id", conversation_id)
                conversations.append(normalized)
        return conversations

    def _load_audit_logs(self, limit: int) -> list[dict[str, Any]]:
        list_fn = getattr(self.persistence, "list_audit_logs", None)
        if not callable(list_fn):
            return []
        try:
            page = list_fn(limit=max(20, min(limit * 2, 200)), offset=0)
        except Exception:
            return []
        rows = page.get("logs") if isinstance(page, dict) else None
        if not isinstance(rows, list):
            return []
        return [row for row in rows if isinstance(row, dict)]

    def _derive_time_range(
        self,
        conversations: list[dict[str, Any]],
        audit_logs: list[dict[str, Any]],
    ) -> tuple[str | None, str | None]:
        timestamps: list[datetime] = []
        for conversation in conversations:
            for key in ("created_at", "updated_at"):
                parsed = _parse_timestamp(conversation.get(key))
                if parsed is not None:
                    timestamps.append(parsed)
            messages = conversation.get("messages")
            if isinstance(messages, list):
                for message in messages:
                    if not isinstance(message, dict):
                        continue
                    parsed = _parse_timestamp(message.get("created_at"))
                    if parsed is not None:
                        timestamps.append(parsed)

        for log in audit_logs:
            parsed = _parse_timestamp(log.get("created_at"))
            if parsed is not None:
                timestamps.append(parsed)

        if not timestamps:
            return (None, None)
        earliest = min(timestamps).isoformat().replace("+00:00", "Z")
        latest = max(timestamps).isoformat().replace("+00:00", "Z")
        return (earliest, latest)

    def _build_summary(self, patterns: list[ContextPattern], conversation_count: int) -> str:
        if not patterns:
            return "No stable context patterns found in this run."
        by_type: dict[str, int] = {}
        for pattern in patterns:
            by_type[pattern.pattern_type] = by_type.get(pattern.pattern_type, 0) + 1
        ordered = ", ".join(f"{name}={count}" for name, count in sorted(by_type.items()))
        return (
            f"Distilled {len(patterns)} patterns from {conversation_count} conversations "
            f"({ordered})."
        )

    def _conversation_has_repair_signal(self, messages: list[dict[str, Any]]) -> bool:
        seen_negative = False
        for message in messages:
            if not isinstance(message, dict):
                continue
            if str(message.get("role") or "").strip().lower() != "user":
                continue
            score = _tone_score(str(message.get("content") or ""))
            if score <= -1.0:
                seen_negative = True
                continue
            if seen_negative and score >= 1.0:
                return True
        return False
