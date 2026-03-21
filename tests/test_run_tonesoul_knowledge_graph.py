from __future__ import annotations

import json
from pathlib import Path

import scripts.run_tonesoul_knowledge_graph as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_extract_existing_paths_resolves_markdown_and_code_refs(tmp_path: Path) -> None:
    _write(tmp_path / "README.md", "# Root\n")
    _write(tmp_path / "docs" / "README.md", "# Docs\n")
    _write(
        tmp_path / "tonesoul" / "unified_pipeline.py",
        "from tonesoul.tension_engine import TensionEngine\n",
    )
    source = tmp_path / "docs" / "index.md"
    _write(
        source,
        "\n".join(
            [
                "[root](../README.md)",
                "`tonesoul/unified_pipeline.py`",
                "See docs/README.md for entrypoint.",
            ]
        ),
    )

    refs = runner.extract_existing_paths(
        source.read_text(encoding="utf-8"),
        "docs/index.md",
        tmp_path,
    )

    assert refs == [
        "README.md",
        "tonesoul/unified_pipeline.py",
        "docs/README.md",
    ]


def test_build_knowledge_graph_emits_lane_reference_and_verifier_edges(tmp_path: Path) -> None:
    _write(tmp_path / "README.md", "`tonesoul/unified_pipeline.py`\n")
    _write(tmp_path / "docs" / "README.md", "[pipe](../tonesoul/unified_pipeline.py)\n")
    _write(
        tmp_path / "tonesoul" / "unified_pipeline.py",
        "from tonesoul.tension_engine import TensionEngine\n",
    )
    _write(tmp_path / "tonesoul" / "tension_engine.py", "class TensionEngine:\n    pass\n")
    _write(
        tmp_path / "tests" / "test_pipeline.py",
        "from tonesoul.unified_pipeline import UnifiedPipeline\n",
    )

    payload = runner.build_knowledge_graph(
        repo_root=tmp_path,
        source_docs=("README.md", "docs/README.md"),
        lane_seeds=(
            {
                "id": "runtime",
                "label": "Runtime",
                "summary": "runtime lane",
                "members": ("tonesoul/unified_pipeline.py", "tonesoul/tension_engine.py"),
                "neighbors": ("verification",),
            },
            {
                "id": "verification",
                "label": "Verification",
                "summary": "verification lane",
                "members": ("tests/test_pipeline.py",),
                "neighbors": ("runtime",),
            },
        ),
        curated_flow_edges=(
            ("tonesoul/unified_pipeline.py", "tonesoul/tension_engine.py", "flows_to"),
        ),
    )

    edge_set = {(edge["source"], edge["target"], edge["type"]) for edge in payload["edges"]}
    assert ("lane:runtime", "file:tonesoul/unified_pipeline.py", "contains") in edge_set
    assert ("file:README.md", "file:tonesoul/unified_pipeline.py", "references") in edge_set
    assert (
        "file:tonesoul/unified_pipeline.py",
        "file:tonesoul/tension_engine.py",
        "imports",
    ) in edge_set
    assert (
        "file:tests/test_pipeline.py",
        "file:tonesoul/unified_pipeline.py",
        "verifies",
    ) in edge_set


def test_render_and_write_outputs(tmp_path: Path) -> None:
    payload = {
        "generated_at": "2026-03-21T00:00:00Z",
        "meta": {"node_count": 3, "edge_count": 2, "lane_count": 1},
        "retrieval_protocol": [{"id": "authority_first", "rule": "Open authority first."}],
        "lanes": [
            {
                "id": "authority",
                "label": "Authority",
                "summary": "Canonical docs.",
                "members": ["README.md"],
                "neighbors": [],
            }
        ],
        "nodes": [
            {
                "id": "file:README.md",
                "label": "README.md",
                "kind": "doc",
                "path": "README.md",
                "lanes": ["authority"],
            }
        ],
        "edges": [],
        "top_anchors": [
            {
                "id": "file:README.md",
                "path": "README.md",
                "label": "README.md",
                "kind": "doc",
                "degree": 2,
            }
        ],
    }

    markdown = runner.render_markdown(payload)
    mermaid = runner.render_mermaid(payload)
    written = runner.write_outputs(
        payload,
        markdown,
        mermaid,
        output_dir=tmp_path / "docs" / "status",
        repo_root=tmp_path,
    )

    assert "# ToneSoul Knowledge Graph Latest" in markdown
    assert "graph TD" in mermaid
    assert written["json"] == "docs/status/tonesoul_knowledge_graph_latest.json"
    json_payload = json.loads((tmp_path / written["json"]).read_text(encoding="utf-8"))
    assert json_payload["meta"]["lane_count"] == 1
