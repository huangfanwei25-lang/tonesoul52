import json

from tools.api_client import CredentialsResolver, MoltbookClient


def _extract_post_id(payload: dict) -> str | None:
    if not isinstance(payload, dict):
        return None
    return (
        payload.get("id")
        or payload.get("comment", {}).get("id")
        or payload.get("post", {}).get("id")
    )


def post_to_moltbook(account_name, submolt, title, content, parent_id=None, client=None):
    client = client or MoltbookClient(CredentialsResolver())
    target = f"post {parent_id}" if parent_id else submolt
    print(f"? {account_name} posting to {target}...")

    try:
        if parent_id:
            data = client.create_comment(account_name, parent_id, content)
        else:
            data = client.create_post(account_name, submolt, title, content)
    except Exception as exc:
        print(f"? Error: {exc}")
        return None

    if isinstance(data, dict) and data.get("error"):
        print(f"??Failed: {data.get('error')}")
        return None

    post_id = _extract_post_id(data)
    if post_id:
        print(f"??Success! ID: {post_id}")
    return data


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

    if result and output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
