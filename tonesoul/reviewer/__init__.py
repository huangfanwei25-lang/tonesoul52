"""Claim-to-evidence reviewer utilities.

This package is a deterministic reviewer aid. It is not a runtime gate and does not decide truth,
ethics, intent, identity, or production readiness.
"""

from .report import SCHEMA_VERSION, review_text

__ts_layer__ = "surface"
__ts_purpose__ = "Claim-to-evidence reviewer package exports for advisory public-claim audits."

__all__ = ["SCHEMA_VERSION", "review_text"]
