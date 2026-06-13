"""Deprecated location shim — canonical module is ``tonesoul.memory.journal_consolidator``.

Relocated and renamed 2026-06-13 (Reality Sync PR1, packaging truth): the
canonical name avoids colliding with the pre-existing
``tonesoul.memory.consolidator`` (reviewed-promotion consolidation), which
is a different module. This shim keeps repo-local consumers working; new
code should import from ``tonesoul.memory.journal_consolidator``.
"""

from tonesoul.memory.journal_consolidator import *  # noqa: F401,F403
