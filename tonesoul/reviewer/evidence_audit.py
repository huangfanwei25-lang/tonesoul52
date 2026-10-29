#!/usr/bin/env python3
"""Offline, deterministic citation audit. Python 3.10+, standard library only."""
import argparse
import hashlib
import html
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

__ts_layer__ = "surface"
__ts_purpose__ = "Offline quotation and declared semantic-review integrity."


EVIDENCE_LEVELS = {"unspecified": -1, "metadata": 0, "excerpt": 1, "full_text": 2}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode())


def identity(source):
    """Recognize arXiv aliases, without treating work identity as independence."""
    url = urlsplit(source["url"])
    if url.hostname in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"}:
        match = re.fullmatch(r"/(?:abs|pdf|html)/(\d{4}\.\d{4,5})(v\d+)?(?:\.pdf)?/?",
                             url.path)
        if match:
            return "arxiv:" + match[1], match[2] or source.get("version", "unspecified")
    return source["url"], source.get("version", "unspecified")


def validate(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    for group in ("sources", "claims"):
        if not isinstance(data.get(group), list):
            raise ValueError(f"{group} must be a list")
        if any(not isinstance(row, dict) for row in data[group]):
            raise ValueError(f"{group}: each entry must be an object")
        ids = [row.get("id") for row in data[group]]
        if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
            raise ValueError(f"{group}: nonempty, unique IDs required")
    for source in data["sources"]:
        if not isinstance(source.get("url"), str) or not source["url"]:
            raise ValueError("source URL required")
        if source.get("evidence_kind", "unspecified") not in EVIDENCE_LEVELS:
            raise ValueError("unknown evidence_kind")
    for claim in data["claims"]:
        for key in ("answer_id", "comparison_key", "text", "source_id"):
            if not isinstance(claim.get(key), str) or not claim[key]:
                raise ValueError(f"claim {claim['id']}: {key} required")
        if not isinstance(claim.get("quote", ""), str):
            raise ValueError("quote must be text")
        if not isinstance(claim.get("reviews", []), list):
            raise ValueError("reviews must be a list")
        if claim.get("required_evidence", "excerpt") not in {"metadata", "excerpt", "full_text"}:
            raise ValueError("unknown required_evidence")


def inspect_source(source, root):
    work, version = identity(source)
    result = {"id": source["id"], "url": source["url"], "work": work,
              "version": version, "scope": source.get("scope", "unspecified"),
              "observations": source.get("observations", []),
              "integrity": "no_snapshot", "text": None, "sha256": None}
    result["evidence_kind"] = source.get("evidence_kind", "unspecified")
    result["version_conflict"] = bool(
        work.startswith("arxiv:") and source.get("version")
        and source["version"] != version)
    snapshot = source.get("snapshot")
    if not snapshot:
        return result
    try:
        path = (root / snapshot["path"]).resolve()
        if not path.is_relative_to(root.resolve()):
            result["integrity"] = "unsafe_path"
            return result
        raw = path.read_bytes()
        result["sha256"] = digest(raw)
        if result["sha256"] != snapshot["sha256"]:
            result["integrity"] = "hash_mismatch"
            return result
        result["text"] = raw.decode("utf-8")
        result["integrity"] = "verified_bytes"
    except (OSError, UnicodeError, KeyError, TypeError, ValueError):
        result["integrity"] = "snapshot_error"
    return result


def review_binding(claim, source):
    """Bind review to all claim context, source locator/version/scope and bytes."""
    payload = {k: v for k, v in claim.items() if k != "reviews"}
    return fingerprint({"binding_protocol": 2, "claim": payload, "source": {
        k: source[k] for k in ("id", "url", "work", "version", "scope", "sha256",
                               "evidence_kind", "version_conflict")}})


def inspect_claim(claim, source):
    result = {k: claim[k] for k in ("id", "answer_id", "comparison_key", "text", "source_id")}
    result.update(quote=claim.get("quote", ""), citation="source_missing",
                  semantic_support="unassessed", reviews=[], review_binding=None,
                  required_evidence=claim.get("required_evidence", "excerpt"),
                  evidence_scope="unavailable")
    if source is None:
        return result
    result.update(work=source["work"], version=source["version"],
                  source_integrity=source["integrity"], scope=source["scope"])
    result["evidence_kind"] = source["evidence_kind"]
    result["evidence_scope"] = (
        "version_conflict" if source["version_conflict"] else
        "kind_unspecified" if source["evidence_kind"] == "unspecified" else
        "insufficient_scope" if EVIDENCE_LEVELS[source["evidence_kind"]]
        < EVIDENCE_LEVELS[result["required_evidence"]] else "declared_scope_sufficient")
    binding = review_binding(claim, source)
    result["review_binding"] = binding
    quote, text = claim.get("quote", ""), source["text"]
    if text is None:
        result["citation"] = "unverifiable"
    elif not quote:
        result["citation"] = "quote_missing"
    elif "span" in claim:
        span = claim["span"]
        valid = (isinstance(span, list) and len(span) == 2
                 and all(type(x) is int for x in span)
                 and 0 <= span[0] < span[1] <= len(text))
        result["citation"] = ("exact" if valid and text[span[0]:span[1]] == quote
                              else "span_mismatch")
    else:
        matches = [m.start() for m in re.finditer("(?=" + re.escape(quote) + ")", text)]
        result["citation"] = ("quote_mismatch" if not matches else
                              "exact" if len(matches) == 1 else "ambiguous")
        result["matches"] = matches
    verdicts = set()
    for review in claim.get("reviews", []):
        if not isinstance(review, dict):
            result["reviews"].append({"status": "invalid"})
            continue
        valid = (review.get("verdict") in {"supports", "contradicts", "insufficient"}
                 and isinstance(review.get("reviewer"), str) and bool(review["reviewer"].strip())
                 and isinstance(review.get("reason"), str) and bool(review["reason"].strip()))
        status = ("invalid" if not valid else "stale" if review.get("binding") != binding
                  else "blocked_by_citation" if result["citation"] != "exact"
                  else "blocked_by_evidence_scope" if result["evidence_scope"] != "declared_scope_sufficient"
                  else "current")
        result["reviews"].append({**review, "status": status})
        if status == "current":
            verdicts.add(review["verdict"])
    if len(verdicts) > 1:
        result["semantic_support"] = "reviewer_disagreement"
    elif verdicts:
        result["semantic_support"] = "reviewed_" + next(iter(verdicts))
    return result


def audit(data, root):
    validate(data)
    sources = {s["id"]: inspect_source(s, Path(root)) for s in data["sources"]}
    claims = [inspect_claim(c, sources.get(c["source_id"])) for c in data["claims"]]
    groups = defaultdict(list)
    for claim in claims:
        groups[claim["comparison_key"]].append(claim)
    comparisons = []
    for key, rows in groups.items():
        flags = []
        if len({r["answer_id"] for r in rows}) < 2:
            flags.append("missing_second_answer")
        if len({r.get("source_integrity") == "verified_bytes" for r in rows}) > 1:
            flags.append("snapshot_access_asymmetry")
        by_work = defaultdict(set)
        for row in rows:
            if row.get("work"):
                by_work[row["work"]].add(row["version"])
        if any(len(v) > 1 for v in by_work.values()):
            flags.append("source_version_difference")
        if any(r["citation"] != "exact" for r in rows):
            flags.append("citation_needs_attention")
        if len({r["semantic_support"] for r in rows if r["semantic_support"] != "unassessed"}) > 1 or any(
                r["semantic_support"] == "reviewer_disagreement" for r in rows):
            flags.append("review_difference")
        if any(r["semantic_support"] == "unassessed" for r in rows):
            flags.append("semantic_review_needed")
        comparisons.append({"key": key, "claim_ids": [r["id"] for r in rows], "flags": flags})
    aliases = defaultdict(list)
    for sid, source in sources.items():
        aliases[source["work"]].append(sid)
    tasks = []
    for missing in data.get("missing_inputs", []):
        tasks.append({"action": "provide_missing_input", "detail": missing})
    for row in claims:
        actions = []
        if row["citation"] in {"source_missing", "unverifiable"}:
            actions.append("obtain_verified_snapshot")
        elif row["citation"] != "exact":
            actions.append("locate_exact_quote")
        if row["evidence_scope"] != "declared_scope_sufficient":
            actions.append("resolve_version_conflict" if row["evidence_scope"] == "version_conflict"
                           else "supply_required_evidence_scope")
        if any(r["status"] == "stale" for r in row["reviews"]):
            actions.append("reassess_stale_review")
        if row["citation"] == "exact" and row["evidence_scope"] == "declared_scope_sufficient":
            if row["semantic_support"] == "unassessed":
                actions.append("review_semantic_support")
            elif row["semantic_support"] == "reviewer_disagreement":
                actions.append("inspect_reviewer_disagreement")
        tasks.extend({"claim_id": row["id"], "action": action} for action in actions)
    return {"schema_version": 1, "engine_version": "0.2", "case": data.get("case", "untitled"),
            "limitations": ["Exact quotation does not establish truth or entailment.",
                            "Reviewer identity and source provenance are declared, not authenticated.",
                            "A retrieval failure does not establish source nonexistence.",
                            "Work identity is not proof of independent evidence."],
            "next_actions": tasks,
            "missing_inputs": data.get("missing_inputs", []),
            "comparison_status": "no_claims" if not claims else "see_comparison_flags",
            "sources": [{k: v for k, v in s.items() if k != "text"} for s in sources.values()],
            "source_aliases": [v for v in aliases.values() if len(v) > 1],
            "claims": claims, "comparisons": comparisons}


def render(report):
    e = html.escape
    rows = "".join("<tr>" + "".join(f"<td>{e(str(c.get(k, '')))}</td>" for k in
                    ("id", "text", "citation", "evidence_scope", "semantic_support")) + "</tr>" for c in report["claims"])
    tasks = "".join("<li>" + e(str(t.get("claim_id", "個案"))) + ": "
                    + e(t["action"]) + " " + e(str(t.get("detail", ""))) + "</li>"
                    for t in report["next_actions"])
    return ("<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>主張與證據核對報告</title><style>body{font:17px system-ui;max-width:1100px;"
            "margin:40px auto;padding:0 24px;color:#203040;background:#f6f8fb}"
            "table{border-collapse:collapse;width:100%;background:white}td,th{padding:12px;"
            "border:1px solid #ccd5df;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}"
            "</style><h1>主張與證據核對報告</h1><p>" + e(report["case"]) + "</p>"
            "<p>引用對上 ≠ 主張成立。語義判斷保留審閱者與理由；本工具不認證真相。</p>"
            "<p>缺少資料：" + e("；".join(report["missing_inputs"]) or "無登記") + "</p>"
            "<table><tr><th>主張</th><th>內容</th><th>引用核對</th><th>資料範圍</th><th>語義審閱</th></tr>"
            + rows + "</table><h2>下一步待辦</h2><ul>" + tasks + "</ul><h2>完整稽核資料</h2><pre>"
            + e(json.dumps(report, ensure_ascii=False, indent=2)) + "</pre></html>")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="New output directory")
    args = parser.parse_args()
    try:
        report = audit(json.loads(args.case.read_text(encoding="utf-8")), args.case.parent)
        args.out.mkdir(parents=True, exist_ok=False)
        (args.out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (args.out / "report.html").write_text(render(report), encoding="utf-8")
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, f"Audit error: {error}\n")
    print(args.out / "report.html")


if __name__ == "__main__":
    main()
