# scripts/run_once.py
import os, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# epymarl/src 를 먼저, 그 다음 plugins 를 path 앞쪽에 추가
sys.path.insert(0, str(ROOT / "external" / "epymarl" / "src"))

# plugins 다음 (registry를 찾기 위해 필요)
sys.path.insert(1, str(ROOT))

from plugins import registry as _plugins_registry  # noqa: F401  # ensures hooks load

def run(algo="qmix", env="sc2v2", with_args=None):
    cmd = [
        "python",
        str(ROOT / "external" / "epymarl" / "src" / "main.py"),
        f"--config={algo}",
        f"--env-config=sc2v2",
        "with",
    ]
    with_args = with_args or []
    cmd += with_args
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    run(
        algo="qmix",
        env="sc2v2",
        with_args=[
            'seed=1',
            'env_args.map_name="3m"',
        ],
    )
