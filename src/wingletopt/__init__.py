from pathlib import Path

import avlwrapper as avl
import pkg_resources

from .geometry import TrapezoidalLiftingSurface

__all__ = ["avl", "TrapezoidalLiftingSurface"]

# Monkeypatch avlwrapper default_config
bin_path = Path(pkg_resources.resource_filename("wingletopt", "bin/avl.exe"))
avl.default_config["avl_bin"] = bin_path
avl.default_config["show_stdout"] = False
