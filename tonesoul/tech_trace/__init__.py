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
