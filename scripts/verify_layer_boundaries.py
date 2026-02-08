"""
Layer boundary verifier.

Blocks forbidden imports across top-level architecture layers.
Default policy:
- Files under tonesoul/tools/memory MUST NOT import from apps.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_ROOTS = ("tonesoul", "tools", "memory")
DEFAULT_FORBIDDEN_PREFIXES = ("apps",)
DEFAULT_ALLOWED_IMPORTS = {
    ("memory/contradiction_detector.py", "apps.core.memory_semantic_search"),
}


@dataclass
class Violation:
    path: str
    line: int
    import_path: str
    reason: str


def _iter_python_files(project_root: Path, roots: Sequence[str]) -> Iterable[Path]:
    seen: set[Path] = set()
    for root in roots:
        base = (project_root / root).resolve()
        if not base.exists() or not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            if path in seen:
                continue
            seen.add(path)
            yield path


def _is_forbidden_import(import_path: str, forbidden_prefixes: Sequence[str]) -> bool:
    for prefix in forbidden_prefixes:
        if import_path == prefix or import_path.startswith(prefix + "."):
            return True
    return False


def _collect_imports(source: str) -> list[tuple[int, str]]:
    imports: list[tuple[int, str]] = []
    for lineno, raw in enumerate(source.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        from_match = re.match(r"^from\s+([A-Za-z_][\w\.]*)\s+import\s+", line)
        if from_match:
            imports.append((lineno, from_match.group(1)))
            continue
        import_match = re.match(r"^import\s+(.+)$", line)
        if not import_match:
            continue
        modules_part = import_match.group(1).split("#", maxsplit=1)[0]
        for part in modules_part.split(","):
            module = part.strip().split(" as ", maxsplit=1)[0].strip()
            if module:
                imports.append((lineno, module))
    return imports


def find_violations(
    project_root: Path,
    roots: Sequence[str] = DEFAULT_ROOTS,
    forbidden_prefixes: Sequence[str] = DEFAULT_FORBIDDEN_PREFIXES,
    allowed_imports: set[tuple[str, str]] = DEFAULT_ALLOWED_IMPORTS,
) -> list[Violation]:
    violations: list[Violation] = []
    for path in _iter_python_files(project_root, roots):
        relative = path.relative_to(project_root).as_posix()
        source = path.read_text(encoding="utf-8-sig", errors="replace")
        for line, import_path in _collect_imports(source):
            if _is_forbidden_import(import_path, forbidden_prefixes):
                if (relative, import_path) in allowed_imports:
                    continue
                violations.append(
                    Violation(
                        path=relative,
                        line=line,
                        import_path=import_path,
                        reason="forbidden cross-layer import",
                    )
                )
    return violations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify architecture layer boundaries.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Repository root to scan.",
    )
    parser.add_argument(
        "--roots",
        nargs="+",
        default=list(DEFAULT_ROOTS),
        help="Top-level roots that are forbidden to import app-layer modules.",
    )
    parser.add_argument(
        "--forbidden-prefixes",
        nargs="+",
        default=list(DEFAULT_FORBIDDEN_PREFIXES),
        help="Forbidden import prefixes.",
    )
    parser.add_argument(
        "--allow-import",
        action="append",
        default=[],
        help="Allowed exception in 'path:import.path' format. Can repeat.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    project_root = Path(args.project_root).resolve()
    allowed_imports = set(DEFAULT_ALLOWED_IMPORTS)
    for rule in args.allow_import:
        if ":" not in rule:
            continue
        relative, import_path = rule.split(":", maxsplit=1)
        allowed_imports.add((relative.strip(), import_path.strip()))
    violations = find_violations(
        project_root=project_root,
        roots=args.roots,
        forbidden_prefixes=args.forbidden_prefixes,
        allowed_imports=allowed_imports,
    )
    payload = {
        "ok": len(violations) == 0,
        "project_root": str(project_root),
        "roots": args.roots,
        "forbidden_prefixes": args.forbidden_prefixes,
        "allowed_imports": sorted(f"{p}:{m}" for p, m in allowed_imports),
        "violations": [asdict(v) for v in violations],
        "violation_count": len(violations),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
