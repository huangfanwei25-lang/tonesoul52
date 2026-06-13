#!/usr/bin/env python3
"""Revive GSE Strategy_Mirror in shadow mode (Manifold / self-observation layer).

Strategy_Mirror was built + tested (150-element catalogue, integrated into the
Council) but left default-OFF and never run in shadow — a dormant gem (see
docs/SUCCESSOR_MAP.md §6). This script REVIVES it: loads the catalogue, runs
the StrategyDetector over labeled zh-TW samples, and reports detection
statistics — proving it actually works and giving the shadow-calibration data
the dormant-map called for.

It does NOT flip the production default
(TONESOUL_GSE_STRATEGY_MIRROR_SCAN_ENABLED). Enabling it in the live Council is
a separate owner decision to make AFTER seeing calibration here — this just
brings the dormant detector to life as a runnable, observable thing.

Offline, no LLM. The catalogue's surface signals are zh-TW (the project's
primary language), so samples are Chinese.

Run: python scripts/run_strategy_mirror_shadow.py [--json]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from tonesoul.gse.strategy_mirror.catalog_loader import CatalogLoader
from tonesoul.gse.strategy_mirror.detector import StrategyDetector

# Labeled samples: rhetorical/manipulative zh-TW (should trip moves) vs
# plain-honest zh-TW (should stay quiet). The point is to show the detector
# discriminates, not to be a full benchmark.
SAMPLES = [
    ("rhetorical_hook", "rhetorical", "你有沒有想過,停下來想想——這個機會如果錯過,你會後悔一輩子。"),
    ("urgency_scarcity", "rhetorical", "想想看,名額只剩最後三個,現在不決定,以後就再也沒有了。"),
    ("plain_fact", "plain", "水在攝氏零度結冰。我不確定壓力的精確影響,需要查證。"),
    ("plain_refusal", "plain", "這個我無法確認,沒有可靠來源,所以我選擇不下定論。"),
]


def run() -> dict:
    catalog = CatalogLoader()
    catalog.load()
    detector = StrategyDetector(catalog)

    per_sample = []
    rhetorical_hits = plain_hits = 0
    color_totals: Counter[str] = Counter()
    for case_id, label, text in SAMPLES:
        sig = detector.scan(text)
        moves = [
            {
                "symbol": d.move.symbol,
                "name": d.move.name,
                "transparency_class": getattr(d.move, "transparency_class", "?"),
                "confidence": round(d.confidence, 3),
            }
            for d in sig.detected_moves
        ]
        for m in moves:
            color_totals[m["transparency_class"]] += 1
        if label == "rhetorical" and moves:
            rhetorical_hits += 1
        if label == "plain" and moves:
            plain_hits += 1
        per_sample.append({"case": case_id, "label": label, "n_moves": len(moves), "moves": moves})

    n_rhet = sum(1 for s in SAMPLES if s[1] == "rhetorical")
    n_plain = sum(1 for s in SAMPLES if s[1] == "plain")
    return {
        "schema": "strategy-mirror-shadow-v1",
        "catalog_size": len(list(catalog.all())),
        "detection_rate_rhetorical": round(rhetorical_hits / n_rhet, 3) if n_rhet else None,
        "false_trip_rate_plain": round(plain_hits / n_plain, 3) if n_plain else None,
        "color_totals": dict(color_totals),
        "samples": per_sample,
        "note": "shadow mode — production default TONESOUL_GSE_STRATEGY_MIRROR_SCAN_ENABLED "
        "stays OFF; enabling in the live Council is a separate owner decision after calibration.",
    }


def _print(r: dict) -> None:
    print("=" * 74)
    print(f"Strategy_Mirror shadow run — {r['catalog_size']}-move catalogue (REVIVED)")
    print("=" * 74)
    for s in r["samples"]:
        print(f"\n[{s['label']}] {s['case']}: {s['n_moves']} move(s)")
        for m in s["moves"]:
            print(
                f"    {m['symbol']} {m['name']}  [{m['transparency_class']}]  conf={m['confidence']}"
            )
    print("\n" + "-" * 74)
    print(f"  detection rate on rhetorical samples = {r['detection_rate_rhetorical']}  (want high)")
    print(f"  false-trip rate on plain samples     = {r['false_trip_rate_plain']}  (want 0)")
    print(f"  moves by transparency class          = {r['color_totals']}")
    print(f"\n  {r['note']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    r = run()
    print(json.dumps(r, ensure_ascii=False, indent=2) if args.json else "", end="")
    if not args.json:
        _print(r)


if __name__ == "__main__":
    main()
