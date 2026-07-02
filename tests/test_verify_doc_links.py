"""Tests for scripts/verify_doc_links.py (hermetic: injected tracked-set + tmp repo root)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.verify_doc_links import check_file, evaluate, iter_links  # noqa: E402


def _repo(tmp_path: Path, files: dict[str, str]) -> tuple[Path, set[str]]:
    for rel, content in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
    return tmp_path, set(files)


def test_clean_relative_link_passes(tmp_path: Path) -> None:
    root, tracked = _repo(tmp_path, {"docs/a.md": "[b](b.md)\n", "docs/b.md": "x\n"})
    payload = evaluate(repo_root=root, tracked=tracked)
    assert payload["overall_ok"] is True
    assert payload["summary"]["violation_count"] == 0


def test_missing_target_fails(tmp_path: Path) -> None:
    root, tracked = _repo(tmp_path, {"docs/a.md": "[gone](nope.md)\n"})
    payload = evaluate(repo_root=root, tracked=tracked)
    assert payload["overall_ok"] is False
    assert payload["violations"][0]["kind"] == "missing"


def test_untracked_target_fails(tmp_path: Path) -> None:
    # target exists on disk but is not in the tracked set -> dead in a fresh clone
    root, tracked = _repo(tmp_path, {"docs/a.md": "[b](b.md)\n"})
    (root / "docs" / "b.md").write_text("x\n", encoding="utf-8")
    payload = evaluate(repo_root=root, tracked=tracked)
    assert payload["overall_ok"] is False
    assert payload["violations"][0]["kind"] == "untracked"


def test_absolute_path_fails(tmp_path: Path) -> None:
    root, tracked = _repo(
        tmp_path,
        {"docs/a.md": "[leak](/C:/Users/someone/Desktop/repo/x.py)\n[u](/home/x/y.md)\n"},
    )
    payload = evaluate(repo_root=root, tracked=tracked)
    assert payload["summary"]["absolute"] == 2


def test_code_fences_and_web_links_ignored(tmp_path: Path) -> None:
    content = (
        "```\n[not a link](broken.md)\n```\n"
        "[web](https://example.com)\n[mail](mailto:a@b.c)\n[anchor](#x)\n"
    )
    root, tracked = _repo(tmp_path, {"docs/a.md": content})
    payload = evaluate(repo_root=root, tracked=tracked)
    assert payload["overall_ok"] is True


def test_anchor_suffix_on_real_target_ok(tmp_path: Path) -> None:
    root, tracked = _repo(tmp_path, {"docs/a.md": "[b sec](b.md#section)\n", "docs/b.md": "x\n"})
    payload = evaluate(repo_root=root, tracked=tracked)
    assert payload["overall_ok"] is True


def test_exempt_mirror_prefix_skipped(tmp_path: Path) -> None:
    root, tracked = _repo(
        tmp_path,
        {"docs/design/tonesoul-reference/sources/x.md": "[broken](docs/never.md)\n"},
    )
    payload = evaluate(repo_root=root, tracked=tracked)
    assert payload["overall_ok"] is True
    assert payload["summary"]["md_files_exempt"] == 1


def test_iter_links_line_numbers() -> None:
    text = "a\n[x](y.md) and [z](w.md)\n"
    found = list(iter_links(text))
    assert found == [(2, "y.md"), (2, "w.md")]


def test_check_file_reports_locations(tmp_path: Path) -> None:
    root, tracked = _repo(tmp_path, {"docs/a.md": "x\n[gone](nope.md)\n"})
    violations = check_file(
        "docs/a.md", (root / "docs/a.md").read_text(encoding="utf-8"), tracked, root
    )
    assert violations[0].line == 2 and violations[0].kind == "missing"
