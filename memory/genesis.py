"""Deprecated location shim — canonical module is ``tonesoul.shared.genesis``.

Relocated 2026-06-13 (Reality Sync PR1, packaging truth): the module must
ship inside the ``tonesoul`` package so pip-only installs can import the
council subsystem. This shim keeps repo-local consumers (tools/, tests/,
sibling memory modules) working. New code should import from
``tonesoul.shared.genesis``.
"""

from tonesoul.shared.genesis import (  # noqa: F401
    RESPONSIBILITY_TIER,
    Genesis,
    resolve_responsibility_tier,
)
