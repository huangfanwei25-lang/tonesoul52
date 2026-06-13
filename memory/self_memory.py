"""Deprecated location shim — canonical module is ``tonesoul.memory.self_memory``.

Relocated 2026-06-13 (Reality Sync PR1, packaging truth). This shim keeps
repo-local consumers working; new code should import from
``tonesoul.memory.self_memory``. Note: monkeypatching through this shim does
NOT affect consumers bound to the canonical path — patch the canonical
module (or the consuming module) instead.
"""

from tonesoul.memory.self_memory import *  # noqa: F401,F403
