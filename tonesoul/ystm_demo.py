"""Compatibility wrapper for the YSTM demo pipeline."""

from .ystm.demo import DEFAULT_SEGMENTS, write_demo_outputs


__ts_layer__ = "domain"
__ts_purpose__ = "YSTM demo runner: top-level entry point for YSTM terrain pipeline demo execution."

__all__ = ["DEFAULT_SEGMENTS", "write_demo_outputs"]
