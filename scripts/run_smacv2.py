#!/usr/bin/env python3
"""Register SMACv2 with PyMARL2 on the fly and forward command-line args."""
from __future__ import annotations

import runpy
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYMARL2_SRC = PROJECT_ROOT / "external" / "pymarl2" / "src"
PATCH_SCRIPT = PROJECT_ROOT / "scripts" / "apply_pymarl2_patches.sh"

# Ensure local packages and PyMARL2 are importable
for path in (PROJECT_ROOT, PYMARL2_SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from wrappers.smacv2_env import register_smacv2_env

if PATCH_SCRIPT.exists():
    subprocess.run([str(PATCH_SCRIPT)], check=True)

register_smacv2_env()

MAIN_PATH = PYMARL2_SRC / "main.py"

if __name__ == "__main__":
    sys.argv = [str(MAIN_PATH)] + sys.argv[1:]
    runpy.run_path(str(MAIN_PATH), run_name="__main__")
