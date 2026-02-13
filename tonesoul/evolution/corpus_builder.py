"""Corpus builder for conversion from conversations to structured entries."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .corpus_schema import CorpusEntry


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_str(value: Any) -> str:
    return str(value or "").strip()


def _normalize_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in values:
        clean = str(item).strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        result.append(clean)
    return result


class CorpusBuilder:
    """Build distillation-ready corpus entries from persisted conversations."""

    def __init__(self, persistence: Any):
        self.persistence = persistence

    def build_from_conversation(self, conversation_id: str) -> list[CorpusEntry]:
        get_fn = getattr(self.persistence, "get_conversation", None)
        if not callable(get_fn):
            return []

        conversation_id = _normalize_str(conversation_id)
        if not conversation_id:
            return []

        conversation = get_fn(conversation_id)
        if not isinstance(conversation, dict):
            return []

        messages = conversation.get("messages")
        if not isinstance(messages, list):
            return []
        normalized_messages = [message for message in messages if isinstance(message, dict)]
        if not normalized_messages:
            return []

        audit_logs = self._load_conversation_audit_logs(conversation_id)
        turn_pairs = self._build_turn_pairs(normalized_messages)
        entries: list[CorpusEntry] = []
        for pair_index, pair in enumerate(turn_pairs):
            user_message = pair["user"]
            assistant_message = pair["assistant"]
            next_user_message = pair.get("next_user")

            deliberation = assistant_message.get("deliberation")
            if not isinstance(deliberation, dict):
                deliberation = {}
            transcript = deliberation.get("transcript")
            if not isinstance(transcript, dict):
                transcript = {}

            votes = transcript.get("votes")
            if not isinstance(votes, list):
                votes = []

            philosopher_stance = self._extract_perspective_reason(votes, "philosopher")
            engineer_approach = self._extract_perspective_reason(votes, "engineer")
            guardian_risk = self._extract_perspective_reason(votes, "guardian")

            synthesizer_decision = (
                _normalize_str(deliberation.get("summary"))
                or _normalize_str(deliberation.get("verdict"))
                or _normalize_str(transcript.get("summary"))
                or _normalize_str(transcript.get("final_decision"))
            )

            values_invoked = _normalize_str_list(deliberation.get("emergent_values"))
            commitments_made = _normalize_str_list(deliberation.get("self_commits"))
            risks_identified = _normalize_str_list(deliberation.get("ruptures"))
            if guardian_risk:
                risks_identified = _unique(risks_identified + [guardian_risk])

            tension_level = self._resolve_tension_level(deliberation, audit_logs, pair_index)
            context = self._build_context_window(normalized_messages, pair["user_index"])

            user_satisfaction = self._classify_user_satisfaction(next_user_message)
            quality_score = self._estimate_quality_score(
                deliberation=deliberation,
                tension_level=tension_level,
                user_satisfaction=user_satisfaction,
            )
            tags = self._infer_tags(
                user_text=_normalize_str(user_message.get("content")),
                tension_level=tension_level,
                risks=risks_identified,
                commitments=commitments_made,
                user_satisfaction=user_satisfaction,
            )

            entry = CorpusEntry(
                user_message=_normalize_str(user_message.get("content")),
                conversation_context=context,
                philosopher_stance=philosopher_stance,
                engineer_approach=engineer_approach,
                guardian_risk=guardian_risk,
                synthesizer_decision=synthesizer_decision,
                tension_level=tension_level,
                values_invoked=values_invoked,
                commitments_made=commitments_made,
                risks_identified=risks_identified,
                final_response=_normalize_str(assistant_message.get("content")),
                user_satisfaction=user_satisfaction,
                timestamp=(
                    _normalize_str(assistant_message.get("created_at"))
                    or _normalize_str(user_message.get("created_at"))
                    or _utc_now()
                ),
                conversation_id=conversation_id,
                quality_score=quality_score,
                tags=tags,
            )
            entries.append(entry)
        return entries

    def build_batch(self, limit: int = 100) -> list[CorpusEntry]:
        list_fn = getattr(self.persistence, "list_conversations", None)
        if not callable(list_fn):
            return []

        safe_limit = max(1, min(int(limit or 100), 500))
        page = list_fn(limit=safe_limit, offset=0)
        rows = page.get("conversations") if isinstance(page, dict) else None
        if not isinstance(rows, list):
            return []

        result: list[CorpusEntry] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            conversation_id = _normalize_str(row.get("id"))
            if not conversation_id:
                continue
            if not self._has_audit_logs(conversation_id):
                continue
            result.extend(self.build_from_conversation(conversation_id))
        return result

    def export_jsonl(self, entries: list[CorpusEntry], path: str) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            for entry in entries:
                handle.write(json.dumps(entry.to_dict(), ensure_ascii=False))
                handle.write("\n")

    def _build_turn_pairs(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        pairs: list[dict[str, Any]] = []
        index = 0
        while index < len(messages):
            message = messages[index]
            role = _normalize_str(message.get("role")).lower()
            if role != "user":
                index += 1
                continue

            assistant_index = None
            for candidate in range(index + 1, len(messages)):
                candidate_role = _normalize_str(messages[candidate].get("role")).lower()
                if candidate_role == "assistant":
                    assistant_index = candidate
                    break
                if candidate_role == "user":
                    break
            if assistant_index is None:
                index += 1
                continue

            next_user = None
            for candidate in range(assistant_index + 1, len(messages)):
                candidate_role = _normalize_str(messages[candidate].get("role")).lower()
                if candidate_role == "user":
                    next_user = messages[candidate]
                    break

            pairs.append(
                {
                    "user_index": index,
                    "assistant_index": assistant_index,
                    "user": messages[index],
                    "assistant": messages[assistant_index],
                    "next_user": next_user,
                }
            )
            index = assistant_index + 1
        return pairs

    def _load_conversation_audit_logs(self, conversation_id: str) -> list[dict[str, Any]]:
        list_fn = getattr(self.persistence, "list_audit_logs", None)
        if not callable(list_fn):
            return []
        try:
            page = list_fn(limit=200, offset=0, conversation_id=conversation_id)
        except Exception:
            return []
        rows = page.get("logs") if isinstance(page, dict) else None
        if not isinstance(rows, list):
            return []
        audit_rows = [row for row in rows if isinstance(row, dict)]
        audit_rows.sort(key=lambda row: _normalize_str(row.get("created_at")))
        return audit_rows

    def _has_audit_logs(self, conversation_id: str) -> bool:
        list_fn = getattr(self.persistence, "list_audit_logs", None)
        if not callable(list_fn):
            return False
        try:
            page = list_fn(limit=1, offset=0, conversation_id=conversation_id)
        except Exception:
            return False
        if not isinstance(page, dict):
            return False
        total = page.get("total")
        if isinstance(total, int):
            return total > 0
        logs = page.get("logs")
        return isinstance(logs, list) and len(logs) > 0

    def _build_context_window(self, messages: list[dict[str, Any]], user_index: int) -> str:
        start = max(0, user_index - 3)
        slice_rows = messages[start : user_index + 1]
        lines: list[str] = []
        for row in slice_rows:
            role = _normalize_str(row.get("role")) or "unknown"
            content = _normalize_str(row.get("content")).replace("\n", " ")
            if len(content) > 180:
                content = f"{content[:180]}..."
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _extract_perspective_reason(self, votes: list[Any], perspective: str) -> str:
        target = perspective.strip().lower()
        for vote in votes:
            if not isinstance(vote, dict):
                continue
            current = _normalize_str(vote.get("perspective")).lower()
            if current != target:
                continue
            return _normalize_str(vote.get("reasoning")) or _normalize_str(vote.get("decision"))
        return ""

    def _resolve_tension_level(
        self,
        deliberation: dict[str, Any],
        audit_logs: list[dict[str, Any]],
        pair_index: int,
    ) -> float:
        candidates = [
            deliberation.get("delta_t"),
            deliberation.get("poav_score"),
            deliberation.get("uncertainty_level"),
        ]
        if pair_index < len(audit_logs):
            candidates.append(audit_logs[pair_index].get("delta_t"))
            candidates.append(audit_logs[pair_index].get("poav_score"))
        for value in candidates:
            parsed = _to_float(value)
            if parsed is not None:
                return _clamp01(parsed)
        return 0.0

    def _classify_user_satisfaction(self, next_user_message: dict[str, Any] | None) -> str | None:
        if not isinstance(next_user_message, dict):
            return None
        text = _normalize_str(next_user_message.get("content")).lower()
        if not text:
            return None

        positive_tokens = ("thanks", "thank", "helpful", "clear", "works", "resolved")
        negative_tokens = ("still", "not", "wrong", "bad", "error", "broken", "unsafe")
        if any(token in text for token in positive_tokens):
            return "positive"
        if any(token in text for token in negative_tokens):
            return "negative"
        return "neutral"

    def _estimate_quality_score(
        self,
        *,
        deliberation: dict[str, Any],
        tension_level: float,
        user_satisfaction: str | None,
    ) -> float | None:
        score = 0.5
        verdict = _normalize_str(deliberation.get("verdict")).lower()
        if verdict == "approve":
            score += 0.08
        elif verdict in {"block", "declare_stance"}:
            score -= 0.04

        if user_satisfaction == "positive":
            score += 0.24
        elif user_satisfaction == "negative":
            score -= 0.22
        elif user_satisfaction == "neutral":
            score += 0.03

        if tension_level >= 0.75 and user_satisfaction == "positive":
            score += 0.06
        if tension_level >= 0.75 and user_satisfaction == "negative":
            score -= 0.06

        return round(_clamp01(score), 3)

    def _infer_tags(
        self,
        *,
        user_text: str,
        tension_level: float,
        risks: list[str],
        commitments: list[str],
        user_satisfaction: str | None,
    ) -> list[str]:
        tags: list[str] = []
        lower = user_text.lower()
        if tension_level >= 0.75:
            tags.append("high_tension")
        if risks:
            tags.append("risk_sensitive")
        if commitments:
            tags.append("commitment_tracking")
        if any(token in lower for token in ("ethic", "safety", "risk", "harm")):
            tags.append("ethical_dilemma")
        if any(token in lower for token in ("anxious", "sad", "help", "support", "emotion")):
            tags.append("emotional_support")
        if user_satisfaction == "positive":
            tags.append("resolved")
        elif user_satisfaction == "negative":
            tags.append("follow_up_needed")
        return _unique(tags)
