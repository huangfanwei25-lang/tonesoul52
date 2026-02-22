"""Supabase-backed persistence for ToneSoul API server.

The API server keeps its existing response contract and treats persistence as
best-effort. If Supabase is not configured or temporarily unavailable, request
handling continues without blocking user flows.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any

import requests

DEFAULT_TIMEOUT_SECONDS = 8.0
MAX_RATIONALE_LENGTH = 3000
MAX_SESSION_LINK_SCAN = 1000
MAX_PAGE_LIMIT = 200


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _trim_text(value: Any, limit: int = MAX_RATIONALE_LENGTH) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[:limit]


class SupabasePersistence:
    """Minimal Supabase REST adapter for backend persistence."""

    def __init__(
        self,
        *,
        url: str | None,
        key: str | None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        session: requests.Session | None = None,
    ) -> None:
        self.url = (url or "").strip().rstrip("/")
        self.key = (key or "").strip()
        self.timeout = max(1.0, float(timeout))
        self._session = session or requests.Session()
        self._last_error: str | None = None

    @classmethod
    def from_env(cls) -> "SupabasePersistence":
        timeout_raw = os.environ.get("SUPABASE_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
        try:
            timeout = float(timeout_raw)
        except ValueError:
            timeout = DEFAULT_TIMEOUT_SECONDS

        key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
        return cls(
            url=os.environ.get("SUPABASE_URL", ""),
            key=key,
            timeout=timeout,
        )

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.key)

    def status_dict(self) -> dict[str, Any]:
        return {
            "provider": "supabase",
            "enabled": self.enabled,
            "configured": self.enabled,
            "last_error": self._last_error,
        }

    def list_conversations(
        self,
        limit: int = 20,
        offset: int = 0,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {"conversations": [], "total": 0}

        page_limit = _sanitize_limit(limit)
        page_offset = max(0, int(offset or 0))
        query_params = {
            "select": "id,title,created_at,updated_at",
            "order": "created_at.desc",
            "limit": str(page_limit),
            "offset": str(page_offset),
        }
        count_params: dict[str, str] | None = None
        if session_id is not None:
            session_value = str(session_id).strip()
            if not session_value:
                return {"conversations": [], "total": 0}
            session_conversation_ids = self._list_session_conversation_ids(session_value)
            if not session_conversation_ids:
                return {"conversations": [], "total": 0}
            # PostgREST `in` operator supports quoted strings: in.("a","b")
            quoted_ids = ",".join(
                json.dumps(str(external_id), ensure_ascii=False)
                for external_id in session_conversation_ids
                if str(external_id).strip()
            )
            if not quoted_ids:
                return {"conversations": [], "total": 0}
            in_clause = f"in.({quoted_ids})"
            query_params["title"] = in_clause
            count_params = {"title": in_clause}

        ok, payload = self._request(
            method="GET",
            table="conversations",
            params=query_params,
        )
        if not ok or not isinstance(payload, list):
            return {
                "conversations": [],
                "total": self._count_table_rows("conversations", params=count_params) or 0,
            }

        conversations: list[dict[str, Any]] = []
        for row in payload:
            if not isinstance(row, dict):
                continue
            external_id = str(row.get("title") or row.get("id") or "")
            if not external_id:
                continue
            conversations.append(
                {
                    "id": external_id,
                    "title": str(row.get("title") or external_id),
                    "internal_id": str(row.get("id") or ""),
                    "created_at": row.get("created_at"),
                    "updated_at": row.get("updated_at"),
                }
            )

        return {
            "conversations": conversations,
            "total": self._count_table_rows("conversations", params=count_params) or 0,
        }

    def get_conversation(self, external_id: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        external_id = (external_id or "").strip()
        if not external_id:
            return None

        internal_id = self._resolve_internal_conversation_id(external_id)
        if not internal_id:
            return None

        ok, conversation_payload = self._request(
            method="GET",
            table="conversations",
            params={
                "select": "id,title,created_at,updated_at",
                "id": f"eq.{internal_id}",
                "limit": "1",
            },
        )
        if not ok or not isinstance(conversation_payload, list) or not conversation_payload:
            return None
        conversation_row = conversation_payload[0]
        if not isinstance(conversation_row, dict):
            return None

        ok, message_payload = self._request(
            method="GET",
            table="messages",
            params={
                "select": "id,role,content,deliberation,created_at",
                "conversation_id": f"eq.{internal_id}",
                "order": "created_at.asc",
                "limit": str(MAX_PAGE_LIMIT * 10),
                "offset": "0",
            },
        )
        messages: list[dict[str, Any]] = []
        if ok and isinstance(message_payload, list):
            for row in message_payload:
                if not isinstance(row, dict):
                    continue
                messages.append(
                    {
                        "id": str(row.get("id") or ""),
                        "role": row.get("role"),
                        "content": row.get("content"),
                        "deliberation": row.get("deliberation"),
                        "created_at": row.get("created_at"),
                    }
                )

        return {
            "id": external_id,
            "title": str(conversation_row.get("title") or external_id),
            "internal_id": str(conversation_row.get("id") or internal_id),
            "created_at": conversation_row.get("created_at"),
            "updated_at": conversation_row.get("updated_at"),
            "messages": messages,
        }

    def delete_conversation(self, external_id: str) -> bool | None:
        if not self.enabled:
            return None
        external_id = (external_id or "").strip()
        if not external_id:
            return None
        internal_id = self._resolve_internal_conversation_id(external_id)
        if not internal_id:
            return None
        self._request(
            method="DELETE",
            table="audit_logs",
            params={"conversation_id": f"eq.{internal_id}"},
        )
        ok, _ = self._request(
            method="DELETE",
            table="conversations",
            params={"id": f"eq.{internal_id}"},
        )
        return ok

    def list_audit_logs(
        self,
        limit: int = 20,
        offset: int = 0,
        conversation_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {"logs": [], "total": 0}
        page_limit = _sanitize_limit(limit)
        page_offset = max(0, int(offset or 0))
        query_params = {
            "select": (
                "id,conversation_id,gate_decision,p_level_triggered,poav_score,"
                "delta_t,delta_s,delta_sigma,delta_r,rationale,created_at"
            ),
            "order": "created_at.desc",
            "limit": str(page_limit),
            "offset": str(page_offset),
        }
        count_params: dict[str, str] | None = None
        if conversation_id is not None:
            external_conversation_id = str(conversation_id).strip()
            if not external_conversation_id:
                return {"logs": [], "total": 0}
            internal_id = self._resolve_internal_conversation_id(external_conversation_id)
            if not internal_id:
                return {"logs": [], "total": 0}
            query_params["conversation_id"] = f"eq.{internal_id}"
            count_params = {"conversation_id": f"eq.{internal_id}"}
        elif session_id is not None:
            session_value = str(session_id).strip()
            if not session_value:
                return {"logs": [], "total": 0}
            internal_ids = self._list_session_internal_conversation_ids(session_value)
            if not internal_ids:
                return {"logs": [], "total": 0}
            in_values = ",".join(json.dumps(value, ensure_ascii=False) for value in internal_ids)
            in_clause = f"in.({in_values})"
            query_params["conversation_id"] = in_clause
            count_params = {"conversation_id": in_clause}

        ok, payload = self._request(
            method="GET",
            table="audit_logs",
            params=query_params,
        )
        logs = payload if ok and isinstance(payload, list) else []
        return {
            "logs": logs,
            "total": self._count_table_rows("audit_logs", params=count_params) or 0,
        }

    def list_memories(self, limit: int = 10, session_id: str | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        page_limit = _sanitize_limit(limit)
        query_params = {
            "select": "id,source,payload,tags,created_at",
            "order": "created_at.desc",
            "limit": str(page_limit),
            "offset": "0",
        }
        if session_id is not None:
            session_value = str(session_id).strip()
            if not session_value:
                return []
            query_params["tags"] = f"cs.{{session:{session_value}}}"
        ok, payload = self._request(
            method="GET",
            table="soul_memories",
            params=query_params,
        )
        if not ok or not isinstance(payload, list):
            return []
        result: list[dict[str, Any]] = []
        for row in payload:
            if not isinstance(row, dict):
                continue
            result.append(
                {
                    "id": row.get("id"),
                    "source": row.get("source"),
                    "payload": row.get("payload"),
                    "tags": row.get("tags") if isinstance(row.get("tags"), list) else [],
                    "created_at": row.get("created_at"),
                }
            )
        return result

    def get_counts(self) -> dict[str, int]:
        if not self.enabled:
            return {
                "memory_count": 0,
                "conversation_count": 0,
                "audit_log_count": 0,
                "message_count": 0,
            }
        return {
            "memory_count": self._count_table_rows("soul_memories") or 0,
            "conversation_count": self._count_table_rows("conversations") or 0,
            "audit_log_count": self._count_table_rows("audit_logs") or 0,
            "message_count": self._count_table_rows("messages") or 0,
        }

    def ensure_conversation(self, external_id: str, session_id: str | None = None) -> str | None:
        external_id = (external_id or "").strip()
        if not external_id or not self.enabled:
            return None

        internal_id = self._resolve_internal_conversation_id(external_id)
        if internal_id is None:
            internal_id = self._create_internal_conversation(external_id)
        if internal_id is None:
            return None

        if session_id:
            self._append_memory(
                source="session_conversation",
                payload={
                    "session_id": session_id,
                    "conversation_id": external_id,
                    "internal_conversation_id": internal_id,
                    "recorded_at": _utc_now(),
                },
                tags=[f"session:{session_id}", f"conversation:{external_id}"],
            )
        return internal_id

    def record_consent(self, session_id: str, consent_type: str) -> bool:
        if not self.enabled:
            return False
        return self._append_memory(
            source="consent_event",
            payload={
                "session_id": session_id,
                "consent_type": consent_type,
                "timestamp": _utc_now(),
            },
            tags=[f"session:{session_id}", f"consent:{consent_type}"],
        )

    def withdraw_consent(self, session_id: str) -> dict[str, int]:
        result = {
            "tracked_conversations": 0,
            "deleted_conversations": 0,
        }
        if not self.enabled:
            return result

        conversation_ids = self._list_session_conversation_ids(session_id)
        result["tracked_conversations"] = len(conversation_ids)

        for external_id in conversation_ids:
            internal_id = self._resolve_internal_conversation_id(external_id)
            if not internal_id:
                continue
            self._request(
                method="DELETE",
                table="audit_logs",
                params={"conversation_id": f"eq.{internal_id}"},
            )
            ok, _ = self._request(
                method="DELETE",
                table="conversations",
                params={"id": f"eq.{internal_id}"},
            )
            if ok:
                result["deleted_conversations"] += 1

        self._append_memory(
            source="consent_withdrawn",
            payload={
                "session_id": session_id,
                "deleted_conversations": result["deleted_conversations"],
                "tracked_conversations": result["tracked_conversations"],
                "timestamp": _utc_now(),
            },
            tags=[f"session:{session_id}", "consent:withdrawn"],
        )
        return result

    def record_chat_exchange(
        self,
        *,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
        deliberation: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> bool:
        if not self.enabled:
            return False
        internal_id = self.ensure_conversation(conversation_id, session_id=session_id)
        if not internal_id:
            return False

        user_ok = self._insert_message(
            internal_id=internal_id,
            role="user",
            content=user_message,
            deliberation=None,
        )
        assistant_ok = self._insert_message(
            internal_id=internal_id,
            role="assistant",
            content=assistant_message,
            deliberation=deliberation,
        )
        if user_ok or assistant_ok:
            self._touch_conversation(internal_id)
        return user_ok and assistant_ok

    def record_chat_audit(
        self,
        *,
        conversation_id: str,
        verdict: dict[str, Any] | None,
    ) -> bool:
        if not self.enabled:
            return False
        internal_id = self.ensure_conversation(conversation_id)
        if not internal_id:
            return False

        verdict = verdict or {}
        summary = verdict.get("summary")
        uncertainty = verdict.get("uncertainty_level")
        transcript = verdict.get("transcript")
        rationale = _trim_text(summary or json.dumps(transcript or {}, ensure_ascii=False))

        return self._insert_audit_log(
            conversation_id=internal_id,
            gate_decision=str(verdict.get("verdict") or "unknown"),
            p_level_triggered=None,
            poav_score=self._as_float(verdict.get("poav_score")),
            delta_t=self._as_float(verdict.get("delta_t")),
            delta_s=self._as_float(verdict.get("delta_s")),
            delta_sigma=self._as_float(verdict.get("delta_sigma")),
            delta_r=self._as_float(uncertainty),
            rationale=rationale,
        )

    def record_session_report(
        self,
        *,
        conversation_id: str | None,
        report: dict[str, Any],
    ) -> bool:
        if not self.enabled:
            return False

        external_conversation_id = (conversation_id or "").strip()
        internal_id = (
            self.ensure_conversation(external_conversation_id) if external_conversation_id else None
        )
        summary = _trim_text(
            report.get("summary_text")
            or report.get("closing_advice")
            or report.get("hidden_needs")
            or "session_report_recorded"
        )

        audit_ok = self._insert_audit_log(
            conversation_id=internal_id,
            gate_decision="session_report",
            p_level_triggered=None,
            poav_score=None,
            delta_t=None,
            delta_s=None,
            delta_sigma=None,
            delta_r=None,
            rationale=summary,
        )
        memory_ok = self._append_memory(
            source="session_report",
            payload={
                "conversation_id": external_conversation_id or None,
                "report": report,
                "timestamp": _utc_now(),
            },
            tags=[
                "session_report",
                f"conversation:{external_conversation_id}" if external_conversation_id else "",
            ],
        )
        return audit_ok or memory_ok

    def record_evolution_result(
        self,
        *,
        conversation_id: str | None,
        result_type: str,
        payload: dict[str, Any],
    ) -> bool:
        if not self.enabled:
            return False

        normalized_type = str(result_type or "").strip().lower() or "unspecified"
        external_conversation_id = str(conversation_id or "").strip()
        internal_id = (
            self.ensure_conversation(external_conversation_id) if external_conversation_id else None
        )
        evolution_payload = payload if isinstance(payload, dict) else {}

        ok, _ = self._request(
            method="POST",
            table="evolution_results",
            payload={
                "conversation_id": internal_id,
                "result_type": normalized_type,
                "payload": evolution_payload,
            },
        )
        return ok

    def _resolve_internal_conversation_id(self, external_id: str) -> str | None:
        ok, payload = self._request(
            method="GET",
            table="conversations",
            params={
                "select": "id,title",
                "title": f"eq.{external_id}",
                "limit": "1",
            },
        )
        if not ok or not isinstance(payload, list) or not payload:
            return None
        row = payload[0]
        value = row.get("id") if isinstance(row, dict) else None
        return str(value) if value else None

    def _create_internal_conversation(self, external_id: str) -> str | None:
        ok, payload = self._request(
            method="POST",
            table="conversations",
            payload={"title": external_id},
            prefer_representation=True,
        )
        if not ok or not isinstance(payload, list) or not payload:
            return None
        row = payload[0]
        value = row.get("id") if isinstance(row, dict) else None
        return str(value) if value else None

    def _insert_message(
        self,
        *,
        internal_id: str,
        role: str,
        content: str,
        deliberation: dict[str, Any] | None,
    ) -> bool:
        ok, _ = self._request(
            method="POST",
            table="messages",
            payload={
                "conversation_id": internal_id,
                "role": role,
                "content": content,
                "deliberation": deliberation,
            },
        )
        return ok

    def _touch_conversation(self, internal_id: str) -> bool:
        ok, _ = self._request(
            method="PATCH",
            table="conversations",
            params={"id": f"eq.{internal_id}"},
            payload={"updated_at": _utc_now()},
        )
        return ok

    def _insert_audit_log(
        self,
        *,
        conversation_id: str | None,
        gate_decision: str,
        p_level_triggered: str | None,
        poav_score: float | None,
        delta_t: float | None,
        delta_s: float | None,
        delta_sigma: float | None,
        delta_r: float | None,
        rationale: str,
    ) -> bool:
        payload = {
            "conversation_id": conversation_id,
            "gate_decision": gate_decision,
            "p_level_triggered": p_level_triggered,
            "poav_score": poav_score,
            "delta_t": delta_t,
            "delta_s": delta_s,
            "delta_sigma": delta_sigma,
            "delta_r": delta_r,
            "rationale": rationale,
        }
        ok, _ = self._request(method="POST", table="audit_logs", payload=payload)
        return ok

    def _append_memory(
        self,
        *,
        source: str,
        payload: dict[str, Any],
        tags: list[str] | None = None,
    ) -> bool:
        clean_tags = [tag for tag in (tags or []) if tag]
        ok, _ = self._request(
            method="POST",
            table="soul_memories",
            payload={
                "source": source,
                "payload": payload,
                "tags": clean_tags,
            },
        )
        return ok

    def _list_session_conversation_ids(self, session_id: str) -> list[str]:
        ok, payload = self._request(
            method="GET",
            table="soul_memories",
            params={
                "select": "payload",
                "source": "eq.session_conversation",
                "order": "created_at.desc",
                "limit": str(MAX_SESSION_LINK_SCAN),
            },
        )
        if not ok or not isinstance(payload, list):
            return []

        seen: set[str] = set()
        ordered: list[str] = []
        for row in payload:
            if not isinstance(row, dict):
                continue
            record_payload = row.get("payload")
            if not isinstance(record_payload, dict):
                continue
            if str(record_payload.get("session_id") or "") != session_id:
                continue
            external_id = str(record_payload.get("conversation_id") or "").strip()
            if not external_id or external_id in seen:
                continue
            seen.add(external_id)
            ordered.append(external_id)
        return ordered

    def _list_session_internal_conversation_ids(self, session_id: str) -> list[str]:
        external_ids = self._list_session_conversation_ids(session_id)
        internal_ids: list[str] = []
        seen_internal: set[str] = set()
        for external_id in external_ids:
            internal_id = self._resolve_internal_conversation_id(external_id)
            if not internal_id or internal_id in seen_internal:
                continue
            seen_internal.add(internal_id)
            internal_ids.append(internal_id)
        return internal_ids

    def _count_table_rows(
        self,
        table: str,
        params: dict[str, str] | None = None,
    ) -> int | None:
        if not self.enabled:
            return 0

        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "count=exact",
        }
        url = f"{self.url}/rest/v1/{table}"
        try:
            query_params = {"select": "id", "limit": "1"}
            if params:
                query_params.update(params)
            response = self._session.request(
                method="GET",
                url=url,
                params=query_params,
                json=None,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self._last_error = f"{table}:count:{exc.__class__.__name__}:{exc}"
            print(f"[WARN] Supabase count failed: {self._last_error}", file=sys.stderr)
            return None

        if not response.ok:
            self._last_error = f"{table}:count:http_{response.status_code}"
            print(f"[WARN] Supabase count failed: {self._last_error}", file=sys.stderr)
            return None

        content_range = response.headers.get("Content-Range", "")
        if content_range:
            match = re.search(r"/(\d+)$", content_range)
            if match:
                self._last_error = None
                return int(match.group(1))

        try:
            payload = response.json()
        except ValueError:
            payload = None
        self._last_error = None
        if isinstance(payload, list):
            return len(payload)
        return 0

    def _request(
        self,
        *,
        method: str,
        table: str,
        params: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        prefer_representation: bool = False,
    ) -> tuple[bool, Any]:
        if not self.enabled:
            return False, None

        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation" if prefer_representation else "return=minimal",
        }
        url = f"{self.url}/rest/v1/{table}"
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self._last_error = f"{table}:{exc.__class__.__name__}:{exc}"
            print(f"[WARN] Supabase request failed: {self._last_error}", file=sys.stderr)
            return False, None

        if not response.ok:
            body_preview = _trim_text(response.text, 500)
            self._last_error = (
                f"{table}:http_{response.status_code}:{body_preview or 'empty_response'}"
            )
            print(f"[WARN] Supabase request failed: {self._last_error}", file=sys.stderr)
            return False, None

        text = response.text.strip()
        if not text:
            self._last_error = None
            return True, None
        try:
            data = response.json()
        except ValueError:
            self._last_error = None
            return True, None

        self._last_error = None
        return True, data

    @staticmethod
    def _as_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


def _sanitize_limit(limit: int, default: int = 20, maximum: int = MAX_PAGE_LIMIT) -> int:
    try:
        parsed = int(limit)
    except (TypeError, ValueError):
        return default
    if parsed <= 0:
        return default
    return min(parsed, maximum)
