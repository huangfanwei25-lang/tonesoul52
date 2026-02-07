import json
import math
import os
import re
from typing import Dict, Iterable, Optional

import yaml

from .ystm.schema import utc_now

DEFAULT_LEXICON = {
    "positive": {
        "advance",
        "build",
        "create",
        "enable",
        "allow",
        "proceed",
        "support",
        "improve",
        "optimize",
        "maintain",
        "stabilize",
        "secure",
    },
    "negative": {
        "avoid",
        "block",
        "deny",
        "halt",
        "stop",
        "prevent",
        "refuse",
        "reject",
        "limit",
        "restrict",
        "warn",
    },
    "strong_modals": {
        "must",
        "should",
        "need",
        "required",
        "require",
        "ensure",
        "shall",
        "enforce",
    },
    "caution": {
        "risk",
        "uncertain",
        "may",
        "might",
        "caution",
        "warning",
    },
}

DEFAULT_TENSION = {
    "base": 0.15,
    "length_weight": 0.35,
    "modal_weight": 0.25,
    "caution_weight": 0.15,
    "punctuation_weight": 0.1,
    "length_tokens": 180.0,
    "modal_hits": 6.0,
    "caution_hits": 6.0,
    "punctuation_hits": 8.0,
}
DEFAULT_VARIABILITY = {
    "unique_ratio_target": 0.6,
    "length_tokens": 30.0,
}


def _default_policy_path() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "spec", "metrics", "tsr_policy.yaml")
    )


def load_tsr_policy(path: Optional[str] = None) -> Dict[str, object]:
    policy_path = path or _default_policy_path()
    if not policy_path or not os.path.exists(policy_path):
        return {}
    with open(policy_path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def resolve_tsr_policy(policy: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    policy = policy or {}
    tension = dict(DEFAULT_TENSION)
    tension.update(policy.get("tension", {}) if isinstance(policy.get("tension"), dict) else {})
    variability = dict(DEFAULT_VARIABILITY)
    variability.update(
        policy.get("variability", {}) if isinstance(policy.get("variability"), dict) else {}
    )
    lexicon_policy = policy.get("lexicon", {}) if isinstance(policy.get("lexicon"), dict) else {}
    lexicon: Dict[str, set] = {}
    for key, default_words in DEFAULT_LEXICON.items():
        values = lexicon_policy.get(key)
        if isinstance(values, list):
            lexicon[key] = {str(item).lower() for item in values if str(item).strip()}
        else:
            lexicon[key] = set(default_words)
    return {
        "tension": tension,
        "variability": variability,
        "lexicon": lexicon,
    }


def _tokenize(text: str) -> Iterable[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


def _count_hits(tokens: Iterable[str], vocab: set) -> int:
    return sum(1 for token in tokens if token in vocab)


def _safe_scale(value: float) -> float:
    return value if value > 0 else 1.0


def score(text: str, policy: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    if policy is None:
        policy = resolve_tsr_policy(load_tsr_policy())
    else:
        policy = resolve_tsr_policy(policy)
    tension_cfg = policy["tension"]
    variability_cfg = policy["variability"]
    lexicon = policy["lexicon"]
    tokens = list(_tokenize(text))
    token_count = len(tokens)
    unique_ratio = len(set(tokens)) / max(token_count, 1)
    exclam_count = text.count("!")
    question_count = text.count("?")

    positive_hits = _count_hits(tokens, lexicon["positive"])
    negative_hits = _count_hits(tokens, lexicon["negative"])
    strong_hits = _count_hits(tokens, lexicon["strong_modals"])
    caution_hits = _count_hits(tokens, lexicon["caution"])

    length_factor = min(1.0, token_count / _safe_scale(float(tension_cfg["length_tokens"])))
    modal_factor = min(1.0, strong_hits / _safe_scale(float(tension_cfg["modal_hits"])))
    caution_factor = min(1.0, caution_hits / _safe_scale(float(tension_cfg["caution_hits"])))
    punct_factor = min(
        1.0,
        (exclam_count + question_count) / _safe_scale(float(tension_cfg["punctuation_hits"])),
    )

    tension = min(
        1.0,
        float(tension_cfg["base"])
        + float(tension_cfg["length_weight"]) * length_factor
        + float(tension_cfg["modal_weight"]) * modal_factor
        + float(tension_cfg["caution_weight"]) * caution_factor
        + float(tension_cfg["punctuation_weight"]) * punct_factor,
    )

    direction = 0.0
    direction_hits = positive_hits + negative_hits
    if direction_hits:
        direction = (positive_hits - negative_hits) / direction_hits
    direction_norm = (direction + 1.0) / 2.0

    diversity_factor = min(
        1.0, unique_ratio / _safe_scale(float(variability_cfg["unique_ratio_target"]))
    )
    length_balance = min(1.0, token_count / _safe_scale(float(variability_cfg["length_tokens"])))
    variability = min(1.0, diversity_factor * length_balance)

    energy_radius = math.sqrt(tension**2 + direction_norm**2 + variability**2)

    return {
        "tsr": {
            "T": round(tension, 4),
            "S": round(direction, 4),
            "S_norm": round(direction_norm, 4),
            "R": round(variability, 4),
            "energy_radius": round(energy_radius, 4),
        },
        "signals": {
            "token_count": token_count,
            "unique_ratio": round(unique_ratio, 4),
            "positive_hits": positive_hits,
            "negative_hits": negative_hits,
            "strong_modal_hits": strong_hits,
            "caution_hits": caution_hits,
            "exclamation_count": exclam_count,
            "question_count": question_count,
        },
    }


def build_tsr_metrics(
    text: str,
    run_id: Optional[str] = None,
    source_path: Optional[str] = None,
    baseline_entry: Optional[Dict[str, object]] = None,
    policy: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    metrics = score(text, policy=policy)
    payload: Dict[str, object] = {
        "generated_at": utc_now(),
        "run_id": run_id,
        "source": {"type": "execution_report", "path": source_path},
        "tsr": metrics.get("tsr"),
        "signals": metrics.get("signals"),
        "delta": {"available": False},
        "notes": "Heuristic TSR metrics for demo use only.",
    }
    baseline_tsr = None
    if baseline_entry and isinstance(baseline_entry.get("tsr"), dict):
        baseline_tsr = baseline_entry.get("tsr")
    if baseline_tsr:
        current = payload["tsr"]
        if isinstance(current, dict):
            delta_t = float(current.get("T", 0.0)) - float(baseline_tsr.get("T", 0.0))
            delta_s = float(current.get("S", 0.0)) - float(baseline_tsr.get("S", 0.0))
            delta_s_norm = float(current.get("S_norm", 0.0)) - float(
                baseline_tsr.get("S_norm", 0.0)
            )
            delta_r = float(current.get("R", 0.0)) - float(baseline_tsr.get("R", 0.0))
            delta_norm = math.sqrt(delta_t**2 + delta_s_norm**2 + delta_r**2)
            payload["delta"] = {
                "available": True,
                "baseline_run_id": baseline_entry.get("run_id"),
                "baseline_metrics_path": baseline_entry.get("metrics_path"),
                "T": round(delta_t, 4),
                "S": round(delta_s, 4),
                "S_norm": round(delta_s_norm, 4),
                "R": round(delta_r, 4),
                "delta_norm": round(delta_norm, 4),
            }
    return payload


def load_index(path: str) -> Dict[str, object]:
    if not path or not os.path.exists(path):
        return {"generated_at": utc_now(), "entries": []}
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return {"generated_at": utc_now(), "entries": []}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        payload["entries"] = []
    return payload


def latest_entry(index_payload: Dict[str, object]) -> Optional[Dict[str, object]]:
    entries = index_payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return None
    return entries[-1] if isinstance(entries[-1], dict) else None


def update_index(
    path: str,
    run_id: str,
    metrics_path: str,
    payload: Dict[str, object],
    max_entries: int = 200,
) -> None:
    index = load_index(path)
    entries = [entry for entry in index.get("entries", []) if entry.get("run_id") != run_id]
    entry = {
        "run_id": run_id,
        "generated_at": payload.get("generated_at"),
        "metrics_path": metrics_path,
        "tsr": payload.get("tsr"),
        "delta_norm": payload.get("delta", {}).get("delta_norm"),
    }
    entries.append(entry)
    if max_entries > 0 and len(entries) > max_entries:
        entries = entries[-max_entries:]
    index["entries"] = entries
    index["generated_at"] = utc_now()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2)


def write_tsr_metrics(path: str, payload: Dict[str, object]) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return path
