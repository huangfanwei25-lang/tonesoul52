"""
Local and optional web search helpers for chat retrieval.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    local_hits = search_local(query, roots) if enable_local else []
    web_hits = search_web(query) if enable_web else []
    return build_search_context_from_hits(local_hits=local_hits, web_hits=web_hits)


def build_search_context_from_hits(
    *,
    local_hits: List[Dict[str, str]] | None,
    web_hits: List[Dict[str, str]] | None,
) -> str:
    lines: List[str] = []
    for idx, hit in enumerate(list(local_hits or []), 1):
        lines.append("Local search hits:" if idx == 1 else "")
        lines.append(f"[{idx}] {hit['path']}: {hit['snippet']}")
    for idx, hit in enumerate(list(web_hits or []), 1):
        if idx == 1:
            lines.append("Web search hits:")
        title = hit.get("title") or hit.get("url") or f"Result {idx}"
        snippet = hit.get("snippet") or ""
        lines.append(f"[{idx}] {title} - {snippet}")
    return "\n".join(line for line in lines if line).strip()


def build_search_context_boundary_cue(
    *,
    enable_local: bool,
    enable_web: bool,
) -> Dict[str, str]:
    if enable_local and enable_web:
        mode = "local+web"
        summary = "Search is active for auxiliary repo + web context."
        boundary = (
            "Use search hits as secondary context only. They do not outrank readiness, short-board truth, closeout attention, or bounded runtime surfaces."
        )
    elif enable_local:
        mode = "local"
        summary = "Local retrieval is active for auxiliary repo context."
        boundary = (
            "Local search can widen repo context, but it still stays below Tier 0 / Tier 1 operator truth."
        )
    elif enable_web:
        mode = "web"
        summary = "Web retrieval is active for external context."
        boundary = (
            "Web search is the weakest surface here. Treat it as external context that must be re-checked against current runtime and canonical sources."
        )
    else:
        mode = "off"
        summary = "Search is off by default."
        boundary = (
            "Start from Tier 0 / Tier 1 first. Turn search on only when operator truth is not enough and extra context is actually needed."
        )
    return {
        "mode": mode,
        "summary": summary,
        "boundary": boundary,
    }


def build_search_preview_model(
    *,
    query: str,
    local_hits: List[Dict[str, str]] | None,
    web_hits: List[Dict[str, str]] | None,
) -> Dict[str, Any]:
    query_text = str(query or "").strip()
    local_items = list(local_hits or [])
    web_items = list(web_hits or [])
    if not query_text or (not local_items and not web_items):
        return {
            "present": False,
            "query": query_text,
            "summary_text": "No auxiliary retrieval preview is currently visible.",
            "operator_rule": (
                "Search preview stays auxiliary. Tier 0 / Tier 1 / Tier 2 operator truth still outranks anything shown here."
            ),
            "items": [],
        }

    preview_items: List[Dict[str, str]] = []
    for hit in local_items[:3]:
        path_text = str(hit.get("path", "")).strip()
        preview_items.append(
            {
                "source": "local",
                "label": Path(path_text).name or path_text or "local-hit",
                "detail": path_text,
                "snippet": str(hit.get("snippet", "")).strip(),
            }
        )
    for hit in web_items[:3]:
        title = str(hit.get("title", "")).strip()
        url = str(hit.get("url", "")).strip()
        preview_items.append(
            {
                "source": "web",
                "label": title or url or "web-hit",
                "detail": url,
                "snippet": str(hit.get("snippet", "")).strip(),
            }
        )

    return {
        "present": True,
        "query": query_text,
        "summary_text": f"retrieval_preview local={len(local_items)} web={len(web_items)}",
        "operator_rule": (
            "This preview shows auxiliary retrieval context only. Re-check against Tier 0 / Tier 1 / Tier 2 before treating anything here as current operator truth."
        ),
        "items": preview_items[:6],
    }
