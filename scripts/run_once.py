#!/usr/bin/env python3
"""Quick helper to launch a single PyMARL2 run from the project root."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYMARL2_MAIN = ROOT / "external" / "pymarl2" / "src" / "main.py"
PATCH_SCRIPT = ROOT / "scripts" / "apply_pymarl2_patches.sh"


def run(algo: str = "qmix", env_config: str = "sc2", with_args: list[str] | None = None) -> None:
    if PATCH_SCRIPT.exists():
        subprocess.run([str(PATCH_SCRIPT)], check=True)

    command: list[str] = [
        sys.executable,
        str(PYMARL2_MAIN),
        f"--config={algo}",
        f"--env-config={env_config}",
    ]

    args = list(with_args) if with_args else []
    if not any(token.startswith("local_results_path") for token in args):
        args.append('local_results_path="results/pymarl2"')
    if args:
        command.append("with")
        command.extend(args)

    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    run(
        algo="qmix",
        env_config="sc2v2",
        with_args=[
            'seed=1',
            'env_args.map_name="protoss_5_vs_5"',
            't_max=5000000',
        ],
    )
