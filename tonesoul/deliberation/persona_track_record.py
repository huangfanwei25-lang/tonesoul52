"""
PersonaTrackRecord

Tracks perspective performance over time and returns dynamic weight multipliers
for Muse/Logos/Aegis during deliberation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _default_stat() -> Dict[str, float]:
    return {
        "total": 0,
        "success_sum": 0.0,
        "approve": 0,
        "refine": 0,
        "declare_stance": 0,
        "block": 0,
        "unknown": 0,
    }


def _verdict_score(verdict: str) -> float:
    v = str(verdict or "").strip().lower()
    if v == "approve":
        return 1.0
    if v == "refine":
        return 0.75
    if v == "declare_stance":
        return 0.5
    if v.startswith("block"):
        return 0.0
    return 0.5


@dataclass
class PersonaTrackRecord:
    path: Path
    global_stats: Dict[str, Dict[str, float]]
    resonance_stats: Dict[str, Dict[str, Dict[str, float]]]

    @classmethod
    def create(cls, path: Path) -> "PersonaTrackRecord":
        return cls(
            path=path,
            global_stats={
                "muse": _default_stat(),
                "logos": _default_stat(),
                "aegis": _default_stat(),
            },
            resonance_stats={},
        )

    @classmethod
    def load_or_create(cls, path: Path) -> "PersonaTrackRecord":
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return cls(
                    path=path,
                    global_stats=data.get("global_stats", {}),
                    resonance_stats=data.get("resonance_stats", {}),
                )
            except Exception:
                pass
        return cls.create(path)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": _utc_iso(),
            "global_stats": self.global_stats,
            "resonance_stats": self.resonance_stats,
            "summary": self.summary(),
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def record_outcome(
        self,
        perspective: str,
        verdict: str,
        resonance_state: str = "unknown",
        loop_detected: bool = False,
    ) -> None:
        p = self._normalize_perspective(perspective)
        if not p:
            return

        verdict_key = self._normalize_verdict_key(verdict)
        score = _verdict_score(verdict_key)

        self._apply_stat(self.global_stats.setdefault(p, _default_stat()), verdict_key, score)

        r_key = self._normalize_resonance(resonance_state, loop_detected)
        bucket = self.resonance_stats.setdefault(r_key, {})
        self._apply_stat(bucket.setdefault(p, _default_stat()), verdict_key, score)

        self.save()

    def get_multiplier(
        self,
        perspective: str,
        resonance_state: str = "unknown",
        loop_detected: bool = False,
    ) -> float:
        p = self._normalize_perspective(perspective)
        if not p:
            return 1.0

        g = self.global_stats.get(p, _default_stat())
        r_key = self._normalize_resonance(resonance_state, loop_detected)
        r = self.resonance_stats.get(r_key, {}).get(p, _default_stat())

        g_score = self._score(g)
        r_score = self._score(r)
        g_total = float(g.get("total", 0) or 0)
        r_total = float(r.get("total", 0) or 0)

        score = (g_score * 0.6) + (r_score * 0.4)
        sample_factor = min(1.0, (g_total + r_total) / 20.0)
        shift = (score - 0.5) * 0.4 * sample_factor
        multiplier = 1.0 + shift
        return max(0.85, min(1.15, multiplier))

    def summary(self) -> Dict[str, Dict[str, float]]:
        out: Dict[str, Dict[str, float]] = {}
        for p in ("muse", "logos", "aegis"):
            stat = self.global_stats.get(p, _default_stat())
            out[p] = {
                "total": int(stat.get("total", 0) or 0),
                "score": round(self._score(stat), 4),
            }
        return out

    @staticmethod
    def _apply_stat(stat: Dict[str, float], verdict_key: str, score: float) -> None:
        stat["total"] = int(stat.get("total", 0) or 0) + 1
        stat["success_sum"] = float(stat.get("success_sum", 0.0) or 0.0) + score
        stat[verdict_key] = int(stat.get(verdict_key, 0) or 0) + 1

    @staticmethod
    def _score(stat: Dict[str, float]) -> float:
        total = float(stat.get("total", 0) or 0)
        if total <= 0:
            return 0.5
        return max(0.0, min(1.0, float(stat.get("success_sum", 0.0) or 0.0) / total))

    @staticmethod
    def _normalize_perspective(perspective: str) -> Optional[str]:
        p = str(perspective or "").strip().lower()
        if p in {"muse", "logos", "aegis"}:
            return p
        return None

    @staticmethod
    def _normalize_verdict_key(verdict: str) -> str:
        v = str(verdict or "").strip().lower()
        if v in {"approve", "refine", "declare_stance"}:
            return v
        if v.startswith("block"):
            return "block"
        return "unknown"

    @staticmethod
    def _normalize_resonance(resonance_state: str, loop_detected: bool) -> str:
        state = str(resonance_state or "unknown").strip().lower() or "unknown"
        if loop_detected:
            return f"{state}:loop"
        return state


def default_track_record_path() -> Path:
    return (
        Path(__file__).resolve().parents[2] / "docs" / "status" / "persona_track_record_latest.json"
    )


def create_persona_track_record(path: Optional[Path] = None) -> PersonaTrackRecord:
    return PersonaTrackRecord.load_or_create(path or default_track_record_path())
