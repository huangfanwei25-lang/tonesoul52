from __future__ import annotations

import json

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


def post_to_moltbook(
    account_name,
    submolt,
    title,
    content,
    parent_id=None,
    client=None,
    genesis: Genesis = Genesis.REACTIVE_SOCIAL,
):
    client = client or MoltbookClient(CredentialsResolver())
    target = f"post {parent_id}" if parent_id else submolt
    print(f"[moltbook] {account_name} posting to {target}...")

    if not account_name:
        return tool_error(
            code=ToolErrorCode.INVALID_INPUT,
            message="Missing account name.",
            genesis=genesis,
            details={"field": "account_name"},
        )
    if not content:
        return tool_error(
            code=ToolErrorCode.INVALID_INPUT,
            message="Missing content.",
            genesis=genesis,
            details={"field": "content"},
        )
    if not parent_id and not submolt:
        return tool_error(
            code=ToolErrorCode.INVALID_INPUT,
            message="Missing submolt for new post.",
            genesis=genesis,
            details={"field": "submolt"},
        )

    gate = enforce_responsibility_tier(
        genesis=genesis,
        minimum="TIER_2",
        action="moltbook_post" if not parent_id else "moltbook_comment",
    )
    if gate:
        return gate

    try:
        if parent_id:
            data = client.create_comment(account_name, parent_id, content)
        else:
            data = client.create_post(account_name, submolt, title, content)
    except ValueError as exc:
        print(f"[moltbook] Error: {exc}")
        return tool_error(
            code=ToolErrorCode.MISSING_CREDENTIALS,
            message=str(exc),
            genesis=genesis,
            details={"account": account_name},
        )
    except requests.RequestException as exc:
        print(f"[moltbook] Error: {exc}")
        return tool_error(
            code=ToolErrorCode.NETWORK_ERROR,
            message=str(exc),
            genesis=genesis,
        )
    except Exception as exc:
        print(f"[moltbook] Error: {exc}")
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
        print(f"[moltbook] Failed: {data.get('error')}")
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Upstream API error.",
            genesis=genesis,
            details={"status": data.get("status"), "error": data.get("error")},
        )

    post_id = _extract_post_id(data)
    if post_id:
        print(f"[moltbook] Success. ID: {post_id}")

    intent_id = f"moltbook:{post_id}" if post_id else None
    return tool_success(
        data={
            "payload": data,
            "post_id": post_id,
            "account": account_name,
            "submolt": submolt,
            "parent_id": parent_id,
        },
        genesis=genesis,
        intent_id=intent_id,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 5:
        print(
            "Usage: python moltbook_poster.py <account_name> <submolt> <title> <content> [output_json] [parent_id]"
        )
        sys.exit(1)

    account_name = sys.argv[1]
    submolt = sys.argv[2]
    title = sys.argv[3]
    content = sys.argv[4]
    output_json = sys.argv[5] if len(sys.argv) > 5 else None
    parent_id = sys.argv[6] if len(sys.argv) > 6 else None

    result = post_to_moltbook(account_name, submolt, title, content, parent_id)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
