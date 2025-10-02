#!/usr/bin/env python3
"""Load a MARLlib checkpoint and run a short evaluation/render pass."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATCH_SCRIPT = ROOT / "scripts" / "apply_marllib_patches.sh"

def ensure_patches() -> None:
    if PATCH_SCRIPT.exists() and PATCH_SCRIPT.is_file():
        subprocess.run([str(PATCH_SCRIPT)], check=True, capture_output=True, text=True)

# Ensure patches are applied before any marllib code is imported
ensure_patches()

# external/marllib 디렉터리를 경로에 추가하여, 그 안의 'marllib' 패키지를 찾도록 합니다.
sys.path.insert(0, str(ROOT / "external" / "marllib"))
sys.path.insert(0, str(ROOT))

from marllib.marl import api as marl

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate MARLlib checkpoints")
    parser.add_argument("--env", choices=["mpe", "overcooked"], required=True)
    parser.add_argument("--map", required=True, help="Scenario/layout name")
    parser.add_argument("--algo", required=True, help="Algorithm name used during training")
    parser.add_argument("--trial-dir", required=True, help="Ray Tune trial directory containing params.json")
    parser.add_argument("--checkpoint", help="Checkpoint directory or checkpoint file. Defaults to latest.")
    parser.add_argument("--local-mode", action="store_true", help="Run Ray in local debug mode")
    parser.add_argument("--num-workers", type=int, default=0, help="Override worker count during evaluation")
    parser.add_argument("--num-gpus", type=int, default=0, help="Override GPU usage during evaluation")
    parser.add_argument("--render", action="store_true", help="Enable environment rendering if supported")
    parser.add_argument("--evaluation-episodes", type=int, default=20, help="Number of evaluation episodes")
    parser.add_argument("--share-policy", default="group", help="Policy sharing used during training")
    parser.add_argument("--force-coop", action="store_true", help="Force global reward when rebuilding the environment")
    return parser.parse_args()


def choose_hyperparam_source(env_name: str) -> str:
    if env_name in {"mpe", "mamujoco", "smac"}:
        return env_name
    return "common"


def locate_checkpoint(trial_dir: Path, checkpoint: str | None) -> Path:
    if checkpoint:
        candidate = Path(checkpoint)
    else:
        checkpoints = sorted(trial_dir.glob("checkpoint_*/checkpoint-*"))
        if not checkpoints:
            raise SystemExit(f"{trial_dir} 에서 checkpoint-* 파일을 찾지 못했습니다.")
        candidate = checkpoints[-1]
    if candidate.is_dir():
        ckpt_files = sorted(candidate.glob("checkpoint-*"))
        if not ckpt_files:
            raise SystemExit(f"{candidate} 디렉터리에 checkpoint-* 파일이 없습니다.")
        candidate = ckpt_files[-1]
    if not candidate.exists():
        raise SystemExit(f"체크포인트를 찾을 수 없습니다: {candidate}")
    return candidate


def build_restore_dict(trial_dir: Path, checkpoint_file: Path, render: bool) -> Dict[str, str | bool]:
    params_path = trial_dir / "params.json"
    if not params_path.exists():
        raise SystemExit(f"params.json 을 찾을 수 없습니다: {params_path}")
    restore = {
        "model_path": str(checkpoint_file),
        "params_path": str(params_path),
    }
    if render:
        restore["render"] = True
    return restore


def main() -> None:
    args = parse_args()
    trial_dir = Path(args.trial_dir).expanduser().resolve()
    checkpoint_file = locate_checkpoint(trial_dir, args.checkpoint)
    restore = build_restore_dict(trial_dir, checkpoint_file, args.render)

    env = marl.make_env(environment_name=args.env, map_name=args.map, force_coop=args.force_coop or args.env == "mpe")
    hyper_source = choose_hyperparam_source(args.env)

    algo_builder = getattr(marl.algos, args.algo, None)
    if algo_builder is None:
        raise SystemExit(f"알 수 없는 알고리즘입니다: {args.algo}")

    algo = algo_builder(hyperparam_source=hyper_source)
    model = marl.build_model(env, algo, {"core_arch": "mlp", "encode_layer": "128-256"})

    stop_cfg = {"training_iteration": 1, "evaluation_num_episodes": args.evaluation_episodes}
    run_kwargs = {
        "share_policy": args.share_policy,
        "num_workers": args.num_workers,
        "num_gpus": args.num_gpus,
        "local_mode": args.local_mode,
        "local_dir": str((ROOT / "results" / "marllib_evals").resolve()),
        "checkpoint_freq": 0,
        "checkpoint_end": False,
        "restore_path": restore,
        "evaluation_interval": 1,
        "evaluation_num_episodes": args.evaluation_episodes,
        "evaluation_num_workers": 1,
        "evaluation_config": {
            "record_env": False,
            "render_env": args.render,
        },
    }

    print(f"[MARLlib] evaluate {args.env}/{args.map} with {args.algo}")
    print(f" checkpoint: {checkpoint_file}")
    algo.render(env, model, stop=stop_cfg, **run_kwargs)


if __name__ == "__main__":
    main()
