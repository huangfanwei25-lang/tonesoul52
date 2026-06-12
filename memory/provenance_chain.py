"""Deprecated location shim — canonical module is ``tonesoul.memory.provenance_chain``.

Relocated 2026-06-13 (Reality Sync PR1, packaging truth). This shim keeps
repo-local consumers working; new code should import from
``tonesoul.memory.provenance_chain``.
"""

from tonesoul.memory.provenance_chain import *  # noqa: F401,F403
