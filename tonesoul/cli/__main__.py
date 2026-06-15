"""Enable ``python -m tonesoul.cli <command>``."""

import sys

__ts_layer__ = "surface"
__ts_purpose__ = "CLI __main__ entry: allows `python -m tonesoul.cli <command>` invocation."

from .main import main

if __name__ == "__main__":
    sys.exit(main())
