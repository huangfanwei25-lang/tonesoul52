import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
CONTROL_WHITELIST = {9, 10, 13}
DEFAULT_IGNORES = {
    "reports/WHITEPAPER_recovered_utf8_raw.md",
}


def _count_cjk(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def _latin1_to_utf8(text: str) -> Optional[str]:
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None


def _should_apply_latin1_fix(original: str, converted: str) -> bool:
    if converted == original:
        return False
    orig_cjk = _count_cjk(original)
    conv_cjk = _count_cjk(converted)
    if conv_cjk < orig_cjk + 20:
        return False
    if conv_cjk / max(len(converted), 1) < 0.05:
        return False
    if converted.count("\ufffd") > original.count("\ufffd"):
        return False
    return True


def _scan_file(path: Path) -> Dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"decode_error": "utf-8"}
    replacement_count = text.count("\ufffd")
    control_count = sum(
        1 for ch in text if ord(ch) < 32 and ord(ch) not in CONTROL_WHITELIST
    )
    return {
        "replacement_count": replacement_count,
        "control_count": control_count,
        "text": text,
    }


def _sync_whitepaper(
    recovered_path: Path,
    source_path: Path,
    apply_fixes: bool,
) -> Tuple[bool, Optional[str]]:
    if not source_path.exists():
        return False, "source_missing"
    if not recovered_path.exists():
        return False, "recovered_missing"
    try:
        source_text = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, "source_decode_error"
    if apply_fixes:
        recovered_path.write_text(source_text, encoding="utf-8")
    return True, "synced"


def _default_whitepaper_source(root: Path) -> Optional[Path]:
    candidate = root / "reports" / "WHITEPAPER_cleaned.md"
    return candidate if candidate.exists() else None


def _relative_path(root: Path, path: Path) -> str:
    try:
        rel = path.resolve().relative_to(root.resolve())
        return rel.as_posix()
    except ValueError:
        return path.as_posix()


def _iter_files(root: Path, ignores: set) -> List[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        rel = _relative_path(root, path)
        if rel in ignores:
            continue
        files.append(path)
    return files


def run_scan(
    root: Path,
    apply_fixes: bool,
    heuristic_fix: bool,
    whitepaper_source: Optional[Path],
    ignores: set,
) -> Dict[str, object]:
    flagged: List[Dict[str, object]] = []
    fixes: List[Dict[str, object]] = []
    scanned = 0

    recovered_whitepaper = root / "reports" / "WHITEPAPER_recovered_utf8.md"
    if recovered_whitepaper.exists():
        scan = _scan_file(recovered_whitepaper)
        if scan.get("replacement_count", 0) > 0:
            source = whitepaper_source or _default_whitepaper_source(root)
            if source:
                ok, reason = _sync_whitepaper(recovered_whitepaper, source, apply_fixes)
                fixes.append(
                    {
                        "path": str(recovered_whitepaper),
                        "action": "sync_whitepaper",
                        "source": str(source),
                        "applied": apply_fixes,
                        "result": reason,
                        "ok": ok,
                    }
                )

    ignored_files = sorted(ignores)
    for path in _iter_files(root, ignores):
        scanned += 1
        scan = _scan_file(path)
        if "decode_error" in scan:
            flagged.append({"path": str(path), **scan})
            continue
        replacement_count = int(scan.get("replacement_count", 0))
        control_count = int(scan.get("control_count", 0))
        text = scan.get("text", "")

        if heuristic_fix and apply_fixes:
            converted = _latin1_to_utf8(text)
            if converted and _should_apply_latin1_fix(text, converted):
                path.write_text(converted, encoding="utf-8")
                fixes.append(
                    {
                        "path": str(path),
                        "action": "latin1_utf8_fix",
                        "applied": True,
                    }
                )
                text = converted
                replacement_count = text.count("\ufffd")
                control_count = sum(
                    1 for ch in text if ord(ch) < 32 and ord(ch) not in CONTROL_WHITELIST
                )

        if replacement_count or control_count:
            flagged.append(
                {
                    "path": str(path),
                    "replacement_count": replacement_count,
                    "control_count": control_count,
                }
            )

    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root": str(root),
        "scanned": scanned,
        "flagged_count": len(flagged),
        "flagged_files": flagged,
        "fixes": fixes,
        "scan_suffixes": sorted(SUFFIXES),
        "heuristic_fix": heuristic_fix,
        "apply_fixes": apply_fixes,
        "ignored_files": ignored_files,
    }
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan and fix transcription issues in 5.2.")
    parser.add_argument("--root", default="5.2", help="Root directory to scan.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply fixes (otherwise report-only).",
    )
    parser.add_argument(
        "--heuristic-fix",
        action="store_true",
        help="Attempt latin1->utf8 heuristic fixes when safe.",
    )
    parser.add_argument(
        "--whitepaper-source",
        help="Optional source path for WHITEPAPER_recovered_utf8.md.",
    )
    parser.add_argument(
        "--ignore",
        action="append",
        help="Relative path to ignore (repeatable).",
    )
    parser.add_argument(
        "--report",
        help="Output report path (default: <root>/reports/transcription_fix_log.json).",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        parser.error(f"Root not found: {root}")
    whitepaper_source = Path(args.whitepaper_source).resolve() if args.whitepaper_source else None
    ignores = set(DEFAULT_IGNORES)
    if args.ignore:
        ignores.update(item.replace("\\", "/") for item in args.ignore)

    report = run_scan(
        root=root,
        apply_fixes=bool(args.apply),
        heuristic_fix=bool(args.heuristic_fix),
        whitepaper_source=whitepaper_source,
        ignores=ignores,
    )
    report_path = Path(args.report).resolve() if args.report else root / "reports" / "transcription_fix_log.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Scanned: {report['scanned']}")
    print(f"Flagged: {report['flagged_count']}")
    print(f"Report: {report_path}")
    if report["flagged_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
