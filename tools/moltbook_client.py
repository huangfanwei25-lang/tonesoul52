from __future__ import annotations

from typing import Dict, Optional

import requests

from memory.genesis import Genesis
from tools.api_client import CredentialsResolver, MoltbookClient
from tools.schema import ToolErrorCode, tool_error, tool_success, enforce_responsibility_tier


def _extract_post_id(payload: dict) -> str | None:
    if not isinstance(payload, dict):
        return None
    return (
        payload.get("id")
        or payload.get("comment", {}).get("id")
        or payload.get("post", {}).get("id")
    )


def _client(
    resolver: Optional[CredentialsResolver] = None,
    base_url: str = "https://www.moltbook.com/api/v1",
    timeout: int = 60,
) -> MoltbookClient:
    return MoltbookClient(resolver or CredentialsResolver(), base_url=base_url, timeout=timeout)


def create_post(
    account: str,
    submolt: str,
    title: str,
    content: str,
    client: Optional[MoltbookClient] = None,
    genesis: Genesis = Genesis.REACTIVE_SOCIAL,
) -> Dict[str, object]:
    client = client or _client()
    gate = enforce_responsibility_tier(
        genesis=genesis,
        minimum="TIER_2",
        action="moltbook_create_post",
    )
    if gate:
        return gate
    try:
        data = client.create_post(account, submolt, title, content)
    except ValueError as exc:
        return tool_error(
            code=ToolErrorCode.MISSING_CREDENTIALS,
            message=str(exc),
            genesis=genesis,
            details={"account": account},
        )
    except requests.RequestException as exc:
        return tool_error(
            code=ToolErrorCode.NETWORK_ERROR,
            message=str(exc),
            genesis=genesis,
        )
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=genesis,
        )

    if not isinstance(data, dict):
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Invalid response payload.",
            genesis=genesis,
        )

    if data.get("error"):
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Upstream API error.",
            genesis=genesis,
            details={"status": data.get("status"), "error": data.get("error")},
        )

    post_id = _extract_post_id(data)
    intent_id = f"moltbook:{post_id}" if post_id else None
    return tool_success(
        data={"payload": data, "post_id": post_id, "submolt": submolt, "account": account},
        genesis=genesis,
        intent_id=intent_id,
    )


def create_comment(
    account: str,
    post_id: str,
    content: str,
    client: Optional[MoltbookClient] = None,
    genesis: Genesis = Genesis.REACTIVE_SOCIAL,
) -> Dict[str, object]:
    client = client or _client()
    gate = enforce_responsibility_tier(
        genesis=genesis,
        minimum="TIER_2",
        action="moltbook_create_comment",
    )
    if gate:
        return gate
    try:
        data = client.create_comment(account, post_id, content)
    except ValueError as exc:
        return tool_error(
            code=ToolErrorCode.MISSING_CREDENTIALS,
            message=str(exc),
            genesis=genesis,
            details={"account": account},
        )
    except requests.RequestException as exc:
        return tool_error(
            code=ToolErrorCode.NETWORK_ERROR,
            message=str(exc),
            genesis=genesis,
        )
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=genesis,
        )

    if not isinstance(data, dict):
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Invalid response payload.",
            genesis=genesis,
        )

    if data.get("error"):
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Upstream API error.",
            genesis=genesis,
            details={"status": data.get("status"), "error": data.get("error")},
        )

    comment_id = _extract_post_id(data)
    intent_id = f"moltbook:{comment_id}" if comment_id else None
    return tool_success(
        data={"payload": data, "comment_id": comment_id, "account": account, "post_id": post_id},
        genesis=genesis,
        intent_id=intent_id,
    )


def get_posts(
    account: str,
    submolt: Optional[str] = None,
    sort: Optional[str] = None,
    query: Optional[str] = None,
    client: Optional[MoltbookClient] = None,
) -> Dict[str, object]:
    client = client or _client()
    try:
        data = client.get_posts(account, submolt=submolt, sort=sort, query=query)
    except ValueError as exc:
        return tool_error(
            code=ToolErrorCode.MISSING_CREDENTIALS,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
            details={"account": account},
        )
    except requests.RequestException as exc:
        return tool_error(
            code=ToolErrorCode.NETWORK_ERROR,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
        )
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
        )

    if not isinstance(data, dict):
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Invalid response payload.",
            genesis=Genesis.REACTIVE_SOCIAL,
        )

    if data.get("error"):
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Upstream API error.",
            genesis=Genesis.REACTIVE_SOCIAL,
            details={"status": data.get("status"), "error": data.get("error")},
        )

    intent_id = f"moltbook:list:{submolt}" if submolt else None
    return tool_success(
        data={"payload": data, "submolt": submolt, "sort": sort, "query": query},
        genesis=Genesis.REACTIVE_SOCIAL,
        intent_id=intent_id,
    )


def get_post(
    account: str,
    post_id: str,
    client: Optional[MoltbookClient] = None,
) -> Dict[str, object]:
    client = client or _client()
    try:
        data = client.get_post(account, post_id)
    except ValueError as exc:
        return tool_error(
            code=ToolErrorCode.MISSING_CREDENTIALS,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
            details={"account": account},
        )
    except requests.RequestException as exc:
        return tool_error(
            code=ToolErrorCode.NETWORK_ERROR,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
        )
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
        )

    if not isinstance(data, dict):
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Invalid response payload.",
            genesis=Genesis.REACTIVE_SOCIAL,
        )

    if data.get("error"):
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Upstream API error.",
            genesis=Genesis.REACTIVE_SOCIAL,
            details={"status": data.get("status"), "error": data.get("error")},
        )

    intent_id = f"moltbook:post:{post_id}" if post_id else None
    return tool_success(
        data={"payload": data, "post_id": post_id},
        genesis=Genesis.REACTIVE_SOCIAL,
        intent_id=intent_id,
    )
