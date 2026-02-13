"""
Local and optional web search helpers for chat retrieval.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import requests

ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".py"}
LOCAL_ENDPOINT_FILE = Path(__file__).parent.parent.parent / "runtime" / "local_search_endpoint.json"


def default_search_roots(workspace: Path) -> List[Path]:
    return [
        workspace / "spec",
        workspace / "docs",
        workspace / "reports",
        workspace / "memory",
    ]


def _read_text(path: Path, limit: int = 20000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    return text[:limit]


def _snippet(text: str, query: str, window: int = 80) -> str:
    lowered = text.lower()
    query_lower = query.lower()
    index = lowered.find(query_lower)
    if index == -1:
        return text[:window] + ("..." if len(text) > window else "")
    start = max(0, index - window)
    end = min(len(text), index + len(query) + window)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet.replace("\n", " ")


def search_local(
    query: str,
    roots: List[Path],
    limit: int = 6,
    max_files: int = 400,
) -> List[Dict[str, str]]:
    if not query:
        return []
    results: List[Dict[str, str]] = []
    scanned = 0
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if scanned >= max_files or len(results) >= limit:
                return results
            if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            scanned += 1
            text = _read_text(path)
            if not text:
                continue
            if query.lower() not in text.lower():
                continue
            results.append(
                {
                    "path": str(path),
                    "snippet": _snippet(text, query),
                }
            )
            if len(results) >= limit:
                return results
    return results


def search_web(query: str) -> List[Dict[str, str]]:
    endpoint = os.getenv("TS_WEB_SEARCH_ENDPOINT")
    timeout = 10
    if not endpoint:
        endpoint = _load_local_endpoint()
        timeout = 1
    if not endpoint or not query:
        return []
    try:
        response = requests.get(endpoint, params={"q": query}, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return []
    items = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return []
    results: List[Dict[str, str]] = []
    for item in items[:6]:
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "title": str(item.get("title", "")),
                "url": str(item.get("url", "")),
                "snippet": str(item.get("snippet", "")),
            }
        )
    return results


def _load_local_endpoint() -> Optional[str]:
    if not LOCAL_ENDPOINT_FILE.exists():
        return None
    try:
        payload = json.loads(LOCAL_ENDPOINT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None
    endpoint = payload.get("endpoint") if isinstance(payload, dict) else None
    if not isinstance(endpoint, str) or not endpoint:
        return None
    return endpoint


def build_search_context(
    query: str,
    roots: List[Path],
    enable_local: bool = True,
    enable_web: bool = False,
) -> str:
    lines: List[str] = []
    if enable_local:
        local_hits = search_local(query, roots)
        if local_hits:
            lines.append("Local search hits:")
            for idx, hit in enumerate(local_hits, 1):
                lines.append(f"[{idx}] {hit['path']}: {hit['snippet']}")
    if enable_web:
        web_hits = search_web(query)
        if web_hits:
            lines.append("Web search hits:")
            for idx, hit in enumerate(web_hits, 1):
                title = hit.get("title") or hit.get("url") or f"Result {idx}"
                snippet = hit.get("snippet") or ""
                lines.append(f"[{idx}] {title} - {snippet}")
    return "\n".join(lines).strip()
