"""ToneSoul 5.2 integration package.

For a per-module layer / purpose / coupling map of this package
(auto-generated from ``__ts_layer__`` and ``__ts_purpose__`` self-declarations
and import edges across all 254 modules), see
``docs/status/codebase_graph_latest.md``. It is produced by
``scripts/analyze_codebase_graph.py`` and is the canonical file-level index —
prefer it over ``docs/CORE_MODULES.md`` (which is a conceptual subsystem
reference, not a per-file lookup).

For import / layer boundary rules (what each of the 13 layers may depend on),
see ``docs/ARCHITECTURE_BOUNDARIES.md``.
"""

from .unified_controller import UnifiedController

__version__ = "1.0.0"
__author__ = "黃梵威 (Fan-Wei Huang) <Fan1234-1>"
__since__ = "2026-04 · 語魂系統 · principle engineering"
__lineage__ = (
    "born in a hospital basement — honesty over helpfulness, learned from medical equipment repair"
)
__all__ = ["UnifiedController", "__version__"]
