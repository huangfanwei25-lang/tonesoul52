"""Compatibility wrapper for the YSTM demo pipeline."""

from .ystm.demo import DEFAULT_SEGMENTS, write_demo_outputs

__ts_layer__ = "domain"
__ts_purpose__ = (
    "YSTM demo runner: end-to-end terrain visualization entry point."
)

__all__ = ["DEFAULT_SEGMENTS", "write_demo_outputs"]
