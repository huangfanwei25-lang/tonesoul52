# DORMANT (as of 2026-07-03): unwired — only imported by tests/test_tech_trace_*.py; no live module, entry point, or script references this package. See docs/SUCCESSOR_MAP.md §6a / docs/status/repo_atlas_2026-07-03.md §2.7.
"""Tech-Trace ingestion helpers."""

from .capture import capture_record, load_text, normalize_tags
from .normalize import normalize_record

__ts_layer__ = "observability"
__ts_purpose__ = "Tech-trace package: technical event tracing and payload validation utilities."

__all__ = [
    "capture_record",
    "load_text",
    "normalize_record",
    "normalize_tags",
]
