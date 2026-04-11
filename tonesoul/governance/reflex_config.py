"""
Reflex Arc configuration — load from JSON, provide defaults.

Separates policy (thresholds, modes) from mechanism (reflex.py).
Operator can change behavior without touching code.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_NAME = "reflex_config.json"


@dataclass
class ReflexConfig:
    """Configuration for the Governance Reflex Arc."""

    # Master switch — controls soul-band gate modifiers and drift reactions.
    # Even when disabled, vow enforcement and council BLOCK are always active
    # (minimum governance floor — cannot be fully turned off).
    enabled: bool = True

    # Vow enforcement: "hard" = block on violation, "soft" = warn only
    # NOTE: "off" is no longer accepted — minimum is "soft"
    vow_enforcement_mode: str = "hard"

    # Council BLOCK enforcement: always True (cannot be disabled)
    council_block_enforcement: bool = True

    # Soul band thresholds (soul_integral boundaries)
    soul_band_thresholds: Dict[str, float] = field(
        default_factory=lambda: {
            "alert": 0.30,
            "strained": 0.55,
            "critical": 0.80,
        }
    )

    # Drift thresholds
    caution_prompt_threshold: float = 0.60
    risk_prompt_threshold: float = 0.75

    # Tension + soul_integral combined reflection trigger
    tension_reflection_threshold: float = 0.70
    soul_integral_reflection_threshold: float = 0.55

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "vow_enforcement_mode": self.vow_enforcement_mode,
            "council_block_enforcement": self.council_block_enforcement,
            "soul_band_thresholds": dict(self.soul_band_thresholds),
            "caution_prompt_threshold": self.caution_prompt_threshold,
            "risk_prompt_threshold": self.risk_prompt_threshold,
            "tension_reflection_threshold": self.tension_reflection_threshold,
            "soul_integral_reflection_threshold": self.soul_integral_reflection_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReflexConfig:
        thresholds = data.get("soul_band_thresholds")
        if not isinstance(thresholds, dict):
            thresholds = None
        # Governance floor: vow enforcement minimum is "soft", council block is always on
        vow_mode = str(data.get("vow_enforcement_mode", "soft"))
        if vow_mode == "off":
            logger.warning("vow_enforcement_mode='off' rejected — minimum is 'soft'")
            vow_mode = "soft"
        return cls(
            enabled=bool(data.get("enabled", True)),
            vow_enforcement_mode=vow_mode,
            council_block_enforcement=True,  # cannot be disabled
            soul_band_thresholds=thresholds
            or {
                "alert": 0.30,
                "strained": 0.55,
                "critical": 0.80,
            },
            caution_prompt_threshold=float(data.get("caution_prompt_threshold", 0.60)),
            risk_prompt_threshold=float(data.get("risk_prompt_threshold", 0.75)),
            tension_reflection_threshold=float(data.get("tension_reflection_threshold", 0.70)),
            soul_integral_reflection_threshold=float(
                data.get("soul_integral_reflection_threshold", 0.55)
            ),
        )


def load_reflex_config(repo_root: Optional[Path] = None) -> ReflexConfig:
    """Load ReflexConfig from reflex_config.json in repo root.

    Falls back to defaults if file doesn't exist or is malformed.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    config_path = repo_root / _DEFAULT_CONFIG_NAME

    if not config_path.exists():
        logger.debug("reflex_config.json not found at %s, using defaults", config_path)
        return ReflexConfig()

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        config = ReflexConfig.from_dict(data)
        logger.debug("Loaded reflex config from %s", config_path)
        return config
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        logger.warning("Failed to load reflex config from %s: %s", config_path, exc)
        return ReflexConfig()
