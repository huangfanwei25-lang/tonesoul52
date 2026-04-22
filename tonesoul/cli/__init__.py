"""ToneSoul CLI package — unified operator command surface.

Entry point: ``python -m tonesoul.cli <command>``
"""

__ts_layer__ = "surface"
__ts_purpose__ = "CLI entry surface: unified operator command interface for ToneSoul."

from .main import main

__all__ = ["main"]
