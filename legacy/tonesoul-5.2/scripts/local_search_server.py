import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse


ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".py"}
DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "runtime",
    "temp",
    "_archive",
}
DEFAULT_IGNORE_PREFIXES = {
    "pytest-cache-files-",
    ".pytest_cache",
}


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


def _should_ignore_dir(name: str) -> bool:
    if name in DEFAULT_IGNORE_DIRS:
        return True
    for prefix in DEFAULT_IGNORE_PREFIXES:
        if name.startswith(prefix):
            return True
    if name.startswith("."):
        return True
    return False


class LocalSearchIndex:
    def __init__(self, root: Path, max_files: int):
        self.root = root
        self.max_files = max_files
        self.files: List[Path] = []

    def build(self) -> None:
        self.files = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if not _should_ignore_dir(d)]
            for filename in filenames:
                if len(self.files) >= self.max_files:
                    return
                path = Path(dirpath) / filename
                if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                    continue
                self.files.append(path)

    def search(self, query: str, limit: int) -> List[Dict[str, str]]:
        if not query:
            return []
        results: List[Dict[str, str]] = []
        query_lower = query.lower()
        for path in self.files:
            if len(results) >= limit:
                break
            text = _read_text(path)
            if not text:
                continue
            if query_lower not in text.lower():
                continue
            results.append(
                {
                    "title": path.name,
                    "url": str(path),
                    "snippet": _snippet(text, query),
                }
            )
        return results


class LocalSearchHandler(BaseHTTPRequestHandler):
    index: Optional[LocalSearchIndex] = None

    def _send_json(self, payload: Dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/search", "/health"}:
            self._send_json({"error": "not_found"}, status=404)
            return
        if parsed.path == "/health":
            self._send_json({"status": "ok"})
            return

        params = parse_qs(parsed.query)
        query = (params.get("q") or [""])[0]
        limit_raw = (params.get("limit") or ["6"])[0]
        try:
            limit = max(1, min(20, int(limit_raw)))
        except ValueError:
            limit = 6

        index = self.index
        if not index:
            self._send_json({"results": [], "error": "index_missing"})
            return
        results = index.search(query, limit)
        payload = {
            "query": query,
            "count": len(results),
            "results": results,
        }
        self._send_json(payload)

    def log_message(self, format: str, *args) -> None:
        return


def _write_endpoint_file(endpoint: str, root: Path) -> None:
    runtime_dir = Path(__file__).resolve().parents[1] / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "endpoint": endpoint,
        "health": endpoint.replace("/search", "/health"),
        "root": str(root),
    }
    path = runtime_dir / "local_search_endpoint.json"
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        return


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local search server (HTTP JSON).")
    parser.add_argument("--root", help="Root directory to index.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind.")
    parser.add_argument("--max-files", type=int, default=1200, help="Max files to index.")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path.cwd()
    if not root.exists():
        print(f"Root not found: {root}")
        return 1

    endpoint = f"http://127.0.0.1:{args.port}/search"
    _write_endpoint_file(endpoint, root)

    index = LocalSearchIndex(root, max_files=args.max_files)
    index.build()

    LocalSearchHandler.index = index
    server = ThreadingHTTPServer(("127.0.0.1", args.port), LocalSearchHandler)
    print(f"Local search server running on http://127.0.0.1:{args.port}/search")
    print(f"Indexed root: {root} (files: {len(index.files)})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
