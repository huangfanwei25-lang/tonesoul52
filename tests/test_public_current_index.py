"""Contract tests for the public ToneSoul current-orientation projection.

The projection is deliberately static and closed.  It helps people and tools
find reviewed public sources without becoming a second architecture truth or a
place to publish private continuity data.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from xml.etree import ElementTree

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HUMAN_PATH = REPO_ROOT / "site" / "current" / "index.html"
MACHINE_PATH = REPO_ROOT / "site" / "current.json"
SCHEMA_PATH = REPO_ROOT / "spec" / "governance" / "public_current_index_v0.schema.json"

HUMAN_URL = "https://huangfanwei25-lang.github.io/tonesoul52/current/"
MACHINE_URL = "https://huangfanwei25-lang.github.io/tonesoul52/current.json"
SCHEMA_URL = (
    "https://raw.githubusercontent.com/huangfanwei25-lang/tonesoul52/"
    "master/spec/governance/public_current_index_v0.schema.json"
)

TOP_LEVEL_KEYS = {
    "$schema",
    "format",
    "artifact_type",
    "as_of",
    "reviewed_revision",
    "canonical",
    "projection",
    "project",
    "scope",
    "sources",
    "source_routes",
    "entrypoints",
    "known_limits",
    "open_tensions",
    "history",
    "does_not_claim",
    "change_conditions",
}


class _PublicCurrentHTMLParser(HTMLParser):
    _BOUND_ATTRIBUTES = {
        "data-source-route-id": "source_route",
        "data-limit-id": "limit",
        "data-tension-id": "tension",
        "data-entrypoint-id": "entrypoint",
        "data-history-reference-id": "history_reference",
    }
    _VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.html_lang: str | None = None
        self.links: list[dict[str, str]] = []
        self.metas: list[dict[str, str]] = []
        self.section_ids: set[str] = set()
        self.source_route_ids: set[str] = set()
        self.limit_ids: set[str] = set()
        self.tension_ids: set[str] = set()
        self.entrypoint_ids: set[str] = set()
        self.history_reference_ids: set[str] = set()
        self.as_of: str | None = None
        self.reviewed_revision: str | None = None
        self.bound_text: dict[str, dict[str, list[str]]] = {
            kind: {} for kind in self._BOUND_ATTRIBUTES.values()
        }
        self.bound_text["history_principle"] = {}
        self.binding_counts: dict[str, dict[str, int]] = {
            kind: {} for kind in self.bound_text
        }
        self.bound_source_refs: dict[str, dict[str, set[str]]] = {
            kind: {} for kind in self.bound_text
        }
        self.source_hrefs: dict[str, str] = {}
        self.entrypoint_hrefs: dict[str, str] = {}
        self.history_reference_hrefs: dict[str, str] = {}
        self._active_bindings: list[tuple[str, str]] = []
        self._element_stack: list[tuple[str, list[tuple[str, str]]]] = []

    def text_for(self, kind: str, identifier: str) -> str:
        chunks = self.bound_text[kind][identifier]
        return " ".join("".join(chunks).split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = attributes.get("lang")
        elif tag == "link":
            self.links.append(attributes)
        elif tag == "meta":
            self.metas.append(attributes)
        elif tag == "section" and attributes.get("id"):
            self.section_ids.add(attributes["id"])

        if attributes.get("data-source-route-id"):
            self.source_route_ids.add(attributes["data-source-route-id"])
        if attributes.get("data-limit-id"):
            self.limit_ids.add(attributes["data-limit-id"])
        if attributes.get("data-tension-id"):
            self.tension_ids.add(attributes["data-tension-id"])
        if attributes.get("data-entrypoint-id"):
            self.entrypoint_ids.add(attributes["data-entrypoint-id"])
        if attributes.get("data-history-reference-id"):
            self.history_reference_ids.add(attributes["data-history-reference-id"])
        if attributes.get("data-as-of"):
            self.as_of = attributes["data-as-of"]
        if attributes.get("data-reviewed-revision"):
            self.reviewed_revision = attributes["data-reviewed-revision"]

        started: list[tuple[str, str]] = []
        for attribute, kind in self._BOUND_ATTRIBUTES.items():
            identifier = attributes.get(attribute)
            if identifier:
                started.append((kind, identifier))
        if "data-history-principle" in attributes:
            started.append(("history_principle", "principle"))

        for kind, identifier in started:
            self.binding_counts[kind][identifier] = (
                self.binding_counts[kind].get(identifier, 0) + 1
            )
            self.bound_text[kind].setdefault(identifier, [])
            self._active_bindings.append((kind, identifier))
            if source_refs := attributes.get("data-source-refs"):
                self.bound_source_refs[kind][identifier] = set(source_refs.split())
            elif source_ref := attributes.get("data-source-ref"):
                self.bound_source_refs[kind][identifier] = {source_ref}

        if source_id := attributes.get("data-source-id"):
            self.source_hrefs[source_id] = attributes.get("href", "")
        if tag == "a":
            for kind, identifier in self._active_bindings:
                if kind == "entrypoint":
                    self.entrypoint_hrefs[identifier] = attributes.get("href", "")
                elif kind == "history_reference":
                    self.history_reference_hrefs[identifier] = attributes.get("href", "")

        if tag not in self._VOID_TAGS:
            self._element_stack.append((tag, started))

    def handle_data(self, data: str) -> None:
        for kind, identifier in self._active_bindings:
            self.bound_text[kind][identifier].append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._element_stack:
            return
        open_tag, started = self._element_stack.pop()
        assert open_tag == tag, f"malformed nesting: expected </{open_tag}>, got </{tag}>"
        for binding in reversed(started):
            assert self._active_bindings[-1] == binding
            self._active_bindings.pop()


def _load_machine() -> dict[str, Any]:
    return json.loads(MACHINE_PATH.read_text(encoding="utf-8"))


def _paths_at_revision(revision: str) -> set[str]:
    if shutil.which("git") is None:
        pytest.skip("git is unavailable; cannot verify reviewed_revision locators")
    inside = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        check=False,
        text=True,
    )
    if inside.returncode != 0:
        pytest.skip("test checkout has no git history")
    tree = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-tree", "-r", "--name-only", revision],
        capture_output=True,
        check=False,
        text=True,
    )
    assert tree.returncode == 0, tree.stderr
    return set(tree.stdout.splitlines())


def _walk_json(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child)


def _assert_closed_object_schemas(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            assert value.get("additionalProperties") is False, (
                f"object schema at {path} must set additionalProperties=false"
            )
        for key, child in value.items():
            _assert_closed_object_schemas(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_closed_object_schemas(child, f"{path}[{index}]")


def _validate_schema_instance(
    instance: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str = "$",
) -> None:
    """Validate the JSON-Schema subset used by this small public contract.

    Keeping this validator local avoids adding a runtime or CI dependency while
    still proving that the instance satisfies required fields, closed objects,
    nested types, constants, enums, patterns, and collection bounds.
    """

    reference = schema.get("$ref")
    if reference:
        assert reference.startswith("#/$defs/"), f"unsupported ref at {path}: {reference}"
        definition = reference.removeprefix("#/$defs/")
        _validate_schema_instance(instance, root_schema["$defs"][definition], root_schema, path)
        return

    if "const" in schema:
        assert instance == schema["const"], f"const mismatch at {path}"
    if "enum" in schema:
        assert instance in schema["enum"], f"enum mismatch at {path}"

    expected_type = schema.get("type")
    if expected_type == "object":
        assert isinstance(instance, dict), f"expected object at {path}"
        required = set(schema.get("required", []))
        assert required <= set(instance), f"missing keys at {path}: {required - set(instance)}"
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            assert set(instance) <= set(properties), (
                f"unexpected keys at {path}: {set(instance) - set(properties)}"
            )
        for key, value in instance.items():
            if key in properties:
                _validate_schema_instance(
                    value, properties[key], root_schema, f"{path}.{key}"
                )
    elif expected_type == "array":
        assert isinstance(instance, list), f"expected array at {path}"
        assert len(instance) >= schema.get("minItems", 0), f"too few items at {path}"
        if schema.get("uniqueItems"):
            normalized = [
                json.dumps(item, ensure_ascii=False, sort_keys=True) for item in instance
            ]
            assert len(normalized) == len(set(normalized)), f"duplicate items at {path}"
        item_schema = schema.get("items")
        if item_schema:
            for index, value in enumerate(instance):
                _validate_schema_instance(
                    value, item_schema, root_schema, f"{path}[{index}]"
                )
    elif expected_type == "string":
        assert isinstance(instance, str), f"expected string at {path}"
        assert len(instance) >= schema.get("minLength", 0), f"string too short at {path}"
        if pattern := schema.get("pattern"):
            assert re.search(pattern, instance), f"pattern mismatch at {path}"
        if schema.get("format") == "date":
            date.fromisoformat(instance)
        elif schema.get("format") == "uri":
            parsed = urlsplit(instance)
            assert parsed.scheme and parsed.netloc, f"invalid URI at {path}"
    elif expected_type == "boolean":
        assert isinstance(instance, bool), f"expected boolean at {path}"


def test_public_current_artifacts_exist() -> None:
    assert HUMAN_PATH.is_file()
    assert MACHINE_PATH.is_file()
    assert SCHEMA_PATH.is_file()


def test_public_current_machine_contract_is_closed_and_typed() -> None:
    document = _load_machine()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert set(document) == TOP_LEVEL_KEYS
    assert set(schema["properties"]) == TOP_LEVEL_KEYS
    assert schema["additionalProperties"] is False
    _assert_closed_object_schemas(schema)
    _validate_schema_instance(document, schema, schema)

    assert document["$schema"] == SCHEMA_URL
    assert document["format"] == "tonesoul/public-current-index-v0"
    assert document["artifact_type"] == "public_current_projection"
    date.fromisoformat(document["as_of"])
    assert re.fullmatch(r"[0-9a-f]{40}", document["reviewed_revision"])

    assert document["canonical"] == {
        "human": HUMAN_URL,
        "machine": MACHINE_URL,
    }
    assert document["projection"] == {
        "kind": "public_navigation",
        "derived": True,
        "writable": False,
        "source_of_truth": False,
    }

    assert document["project"]["name"] == "ToneSoul / 語魂"
    assert document["project"]["summary_zh"]
    assert document["project"]["summary_en"]
    assert document["scope"]["includes"]
    assert document["scope"]["excludes"]
    assert document["sources"]
    assert document["source_routes"]
    assert document["entrypoints"]
    assert document["known_limits"]
    assert document["open_tensions"]
    assert document["does_not_claim"]
    assert document["change_conditions"]

    allowed_source_roles = {
        "canonical_intent",
        "runtime_source",
        "test",
        "generated_measurement",
        "historical_context",
        "proposed_external_contract",
    }
    source_ids = {source["id"] for source in document["sources"]}
    assert len(source_ids) == len(document["sources"])
    reviewed_paths = _paths_at_revision(document["reviewed_revision"])
    for source in document["sources"]:
        assert source["projection_role"] in allowed_source_roles
        assert source["revision"] == document["reviewed_revision"]
        locator = Path(source["locator"])
        assert not locator.is_absolute()
        assert ".." not in locator.parts
        assert (REPO_ROOT / locator).exists(), source["locator"]
        assert source["locator"] in reviewed_paths

    route_ids = {route["id"] for route in document["source_routes"]}
    assert len(route_ids) == len(document["source_routes"])
    for route in document["source_routes"]:
        assert route["question_zh"] and route["question_en"]
        assert route["summary_zh"] and route["summary_en"]
        assert route["source_refs"]
        assert set(route["source_refs"]) <= source_ids
        assert route["caveats_zh"] and route["caveats_en"]

    for note in [*document["known_limits"], *document["open_tensions"]]:
        assert note["summary_zh"] and note["summary_en"]
        assert note["source_refs"]
        assert set(note["source_refs"]) <= source_ids

    limit_ids = [note["id"] for note in document["known_limits"]]
    tension_ids = [note["id"] for note in document["open_tensions"]]
    assert len(limit_ids) == len(set(limit_ids))
    assert len(tension_ids) == len(set(tension_ids))

    history_refs = document["history"]["references"]
    assert history_refs
    history_ids = [reference["id"] for reference in history_refs]
    assert len(history_ids) == len(set(history_ids))
    assert {reference["source_ref"] for reference in history_refs} <= source_ids

    entrypoint_ids = {entrypoint["id"] for entrypoint in document["entrypoints"]}
    assert len(entrypoint_ids) == len(document["entrypoints"])
    assert all(entrypoint["url"].startswith("https://") for entrypoint in document["entrypoints"])

    serialized = json.dumps(document, ensure_ascii=False).lower()
    assert '"status"' not in serialized
    assert '"authority"' not in serialized
    assert '"record_type"' not in serialized


def test_public_current_html_advertises_one_canonical_pair() -> None:
    document = _load_machine()
    html = HUMAN_PATH.read_text(encoding="utf-8")
    parser = _PublicCurrentHTMLParser()
    parser.feed(html)

    assert parser.html_lang == "zh-Hant"
    assert [
        link
        for link in parser.links
        if "canonical" in link.get("rel", "").split()
    ] == [{"rel": "canonical", "href": HUMAN_URL}]
    assert [
        link
        for link in parser.links
        if "alternate" in link.get("rel", "").split()
        and link.get("type") == "application/json"
    ] == [{"rel": "alternate", "type": "application/json", "href": MACHINE_URL}]
    assert [
        meta.get("content")
        for meta in parser.metas
        if meta.get("property") == "og:url"
    ] == [HUMAN_URL]
    assert document["canonical"] == {"human": HUMAN_URL, "machine": MACHINE_URL}
    assert parser.as_of == document["as_of"]
    assert parser.reviewed_revision == document["reviewed_revision"]

    assert {
        "what-it-is",
        "current-posture",
        "evidence",
        "limits",
        "open-tensions",
        "history",
        "for-machines",
    } <= parser.section_ids
    assert parser.source_route_ids == {
        route["id"] for route in document["source_routes"]
    }
    assert parser.limit_ids == {item["id"] for item in document["known_limits"]}
    assert parser.tension_ids == {
        item["id"] for item in document["open_tensions"]
    }
    assert parser.entrypoint_ids == {
        item["id"] for item in document["entrypoints"]
    }
    assert parser.history_reference_ids == {
        item["id"] for item in document["history"]["references"]
    }

    for route in document["source_routes"]:
        route_text = parser.text_for("source_route", route["id"])
        assert parser.binding_counts["source_route"][route["id"]] == 1
        assert parser.bound_source_refs["source_route"][route["id"]] == set(
            route["source_refs"]
        )
        assert route["question_zh"] in route_text
        assert route["question_en"] in route_text
        assert route["summary_zh"] in route_text
        assert route["summary_en"] in route_text
        assert all(caveat in route_text for caveat in route["caveats_zh"])
        assert all(caveat in route_text for caveat in route["caveats_en"])
    for kind, lane in (
        ("limit", document["known_limits"]),
        ("tension", document["open_tensions"]),
    ):
        for item in lane:
            item_text = parser.text_for(kind, item["id"])
            assert parser.binding_counts[kind][item["id"]] == 1
            assert parser.bound_source_refs[kind][item["id"]] == set(
                item["source_refs"]
            )
            assert item["summary_zh"] in item_text
            assert item["summary_en"] in item_text
    for entrypoint in document["entrypoints"]:
        entrypoint_text = parser.text_for("entrypoint", entrypoint["id"])
        assert parser.binding_counts["entrypoint"][entrypoint["id"]] == 1
        assert parser.entrypoint_hrefs[entrypoint["id"]] == entrypoint["url"]
        assert entrypoint["note_zh"] in entrypoint_text
        assert entrypoint["note_en"] in entrypoint_text
    history_text = parser.text_for("history_principle", "principle")
    assert parser.binding_counts["history_principle"]["principle"] == 1
    assert document["history"]["principle_zh"] in history_text
    assert document["history"]["principle_en"] in history_text
    history_by_id = {
        reference["id"]: reference for reference in document["history"]["references"]
    }
    sources_by_id = {source["id"]: source for source in document["sources"]}
    expected_source_hrefs = {
        source["id"]: (
            "https://github.com/huangfanwei25-lang/tonesoul52/blob/"
            f"{source['revision']}/{source['locator']}"
        )
        for source in document["sources"]
    }
    for identifier, reference in history_by_id.items():
        reference_text = parser.text_for("history_reference", identifier)
        assert parser.binding_counts["history_reference"][identifier] == 1
        assert parser.bound_source_refs["history_reference"][identifier] == {
            reference["source_ref"]
        }
        assert reference["label_zh"] in reference_text
        assert reference["label_en"] in reference_text
        source = sources_by_id[reference["source_ref"]]
        expected_history_href = (
            "https://github.com/huangfanwei25-lang/tonesoul52/blob/"
            f"{source['revision']}/{source['locator']}"
        )
        assert parser.history_reference_hrefs[identifier] == expected_history_href

    assert parser.source_hrefs == expected_source_hrefs
    assert document["project"]["summary_zh"] in html
    assert document["project"]["summary_en"] in html


def test_public_current_is_discoverable_from_home_readmes_and_sitemap() -> None:
    home = (REPO_ROOT / "site" / "index.html").read_text(encoding="utf-8")
    root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    zh_readme = (REPO_ROOT / "README.zh-TW.md").read_text(encoding="utf-8")
    robots = (REPO_ROOT / "site" / "robots.txt").read_text(encoding="utf-8")
    sitemap_path = REPO_ROOT / "site" / "sitemap.xml"

    assert 'href="current/"' in home
    assert HUMAN_URL in root_readme
    assert HUMAN_URL in zh_readme
    assert (
        "Sitemap: https://huangfanwei25-lang.github.io/tonesoul52/sitemap.xml"
        in robots
    )

    sitemap = ElementTree.parse(sitemap_path)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    url_entries = sitemap.findall("sm:url", namespace)
    locations = [entry.findtext("sm:loc", namespaces=namespace) for entry in url_entries]
    assert locations.count(HUMAN_URL) == 1
    assert MACHINE_URL not in locations
    current_entry = next(
        entry
        for entry in url_entries
        if entry.findtext("sm:loc", namespaces=namespace) == HUMAN_URL
    )
    assert current_entry.findtext("sm:lastmod", namespaces=namespace) == _load_machine()[
        "as_of"
    ]


def test_interactive_app_links_out_without_copying_the_projection() -> None:
    site_urls = (REPO_ROOT / "apps" / "web" / "src" / "lib" / "siteUrl.ts").read_text(
        encoding="utf-8"
    )
    app_home = (REPO_ROOT / "apps" / "web" / "src" / "app" / "page.tsx").read_text(
        encoding="utf-8"
    )
    app_source_root = REPO_ROOT / "apps" / "web" / "src"
    app_docs = (app_source_root / "app" / "docs" / "page.tsx").read_text(
        encoding="utf-8"
    )

    assert HUMAN_URL in site_urls
    assert "PUBLIC_CURRENT_URL" in app_home
    assert "現行公開索引" in app_home
    assert "PUBLIC_CURRENT_URL" in app_docs
    public_app_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in app_source_root.rglob("*")
        if path.suffix in {".ts", ".tsx"}
    )
    assert "https://github.com/Fan1234-1/tonesoul52" not in public_app_source
    assert not (REPO_ROOT / "apps" / "web" / "src" / "app" / "current").exists()
    assert not (REPO_ROOT / "apps" / "web" / "public" / "current.json").exists()


def test_public_current_projection_rejects_private_or_ambiguous_fields() -> None:
    document = _load_machine()
    forbidden_keys = {
        "raw_dialogue",
        "hidden_reasoning",
        "internal_monologue",
        "system_prompt",
        "personal_context",
        "local_path",
        "api_key",
        "password",
        "secret",
        "token",
        "status",
        "authority",
        "record_type",
    }

    for value in _walk_json(document):
        if isinstance(value, dict):
            assert not (set(value) & forbidden_keys)


def test_public_current_contains_no_private_locator_or_embedded_credentials() -> None:
    payloads = [
        HUMAN_PATH.read_text(encoding="utf-8"),
        MACHINE_PATH.read_text(encoding="utf-8"),
    ]
    forbidden_fragments = {
        ".codex",
        "self_journal.jsonl",
        "continuity/receipts/",
        "github.com/huangfanwei25-lang/memory",
        "file://",
    }

    for payload in payloads:
        lowered = payload.lower().replace("\\", "/")
        assert not re.search(r"[a-z]:/users/[^/]+/", lowered)
        for fragment in forbidden_fragments:
            assert fragment not in lowered

        for candidate in re.findall(r"https?://[^\s\"'<>]+", payload):
            parsed = urlsplit(candidate.rstrip("),.;"))
            assert parsed.username is None
            assert parsed.password is None
