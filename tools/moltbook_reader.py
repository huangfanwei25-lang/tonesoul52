import io
import json
import os
import sys

# Ensure we can import from repository root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from memory.genesis import Genesis
from tools.api_client import CredentialsResolver, MoltbookClient
from tools.schema import ToolErrorCode, tool_error, tool_success

# Fix for Windows encoding issues
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def fetch_posts(client, account, submolt=None, sort="new", query=None):
    try:
        result = client.get_posts(account, submolt=submolt, sort=sort, query=query)
    except ValueError as exc:
        print(f"[!] Error: {exc}")
        return tool_error(
            code=ToolErrorCode.MISSING_CREDENTIALS,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
            details={"account": account},
        )
    except requests.RequestException as exc:
        print(f"[!] Error: {exc}")
        return tool_error(
            code=ToolErrorCode.NETWORK_ERROR,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
        )
    except Exception as exc:
        print(f"[!] Error: {exc}")
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
        )
    if isinstance(result, dict) and result.get("error"):
        print(f"[!] Failed: {result.get('status')} - {result.get('error')}")
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Upstream API error.",
            genesis=Genesis.REACTIVE_SOCIAL,
            details={"status": result.get("status"), "error": result.get("error")},
        )
    intent_id = f"moltbook:list:{submolt}" if submolt else None
    return tool_success(
        data={"payload": result, "submolt": submolt, "sort": sort, "query": query},
        genesis=Genesis.REACTIVE_SOCIAL,
        intent_id=intent_id,
    )


def fetch_post_details(client, account, post_id):
    try:
        result = client.get_post(account, post_id)
    except ValueError as exc:
        print(f"[!] Error: {exc}")
        return tool_error(
            code=ToolErrorCode.MISSING_CREDENTIALS,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
            details={"account": account},
        )
    except requests.RequestException as exc:
        print(f"[!] Error: {exc}")
        return tool_error(
            code=ToolErrorCode.NETWORK_ERROR,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
        )
    except Exception as exc:
        print(f"[!] Error: {exc}")
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=Genesis.REACTIVE_SOCIAL,
        )
    if isinstance(result, dict) and result.get("error"):
        print(f"[!] Failed: {result.get('status')} - {result.get('error')}")
        return tool_error(
            code=ToolErrorCode.UPSTREAM_ERROR,
            message="Upstream API error.",
            genesis=Genesis.REACTIVE_SOCIAL,
            details={"status": result.get("status"), "error": result.get("error")},
        )
    intent_id = f"moltbook:post:{post_id}" if post_id else None
    return tool_success(
        data={"payload": result, "post_id": post_id},
        genesis=Genesis.REACTIVE_SOCIAL,
        intent_id=intent_id,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python moltbook_reader.py <cmd> [args]")
        print("Cmds: list [submolt] [sort] [output_file] [query] [account]")
        print("      get <post_id> [output_file] [account]")
        sys.exit(1)

    account_default = os.getenv("MOLTBOOK_ACCOUNT", "ToneSoul")
    client = MoltbookClient(CredentialsResolver())

    cmd = sys.argv[1]
    if cmd == "list":
        sub = sys.argv[2] if len(sys.argv) > 2 else "whatami"
        sort = sys.argv[3] if len(sys.argv) > 3 else "new"
        output_file = sys.argv[4] if len(sys.argv) > 4 else None
        query = sys.argv[5] if len(sys.argv) > 5 else None
        account = sys.argv[6] if len(sys.argv) > 6 else account_default

        result = fetch_posts(client, account, sub, sort, query)
        if result and result.get("success"):
            output = json.dumps(result, indent=2, ensure_ascii=False)
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"[*] Results saved to {output_file}")
            else:
                print(output)

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: python moltbook_reader.py get <post_id> [output_file] [account]")
            sys.exit(1)

        post_id = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        account = sys.argv[4] if len(sys.argv) > 4 else account_default

        res = fetch_post_details(client, account, post_id)
        if res and res.get("success"):
            output = json.dumps(res, indent=2, ensure_ascii=False)
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"[*] Details saved to {output_file}")
            else:
                print(output)
