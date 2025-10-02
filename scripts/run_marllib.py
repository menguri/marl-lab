#!/usr/bin/env python3
"""Unified MARLlib launcher for PettingZoo (Predator-Prey) and Overcooked tasks."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List

import subprocess

from marllib import marl

from wandb_utils import apply_wandb_env, load_wandb_config  # noqa: E402

try:
    from ray.tune.integration.wandb import WandbLoggerCallback
except ImportError:  # pragma: no cover
    WandbLoggerCallback = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_DIR = ROOT / "results" / "marllib"
DEFAULT_TIMESTEPS = 2_000_000
DEFAULT_STOP_REWARD = float("inf")
DEFAULT_CHECKPOINT_FREQ = 100
PATCH_SCRIPT = ROOT / "scripts" / "apply_marllib_patches.sh"

MPE_MAPS = {
    "simple_spread",
    "simple_tag",
    "simple_adversary",
    "simple_push",
    "simple_reference",
    "simple_crypto",
    "simple_world_comm",
    "simple_speaker_listener",
}

OVERCooked_MAPS = {
    "cramped_room",
    "asymmetric_advantages",
    "coordination_ring",
    "counter_circuit",
    "forced_coordination",
    "two_room_splittable",
    "two_room",
    "simple",
}


def login_to_wandb_if_possible() -> None:
    mode = os.environ.get("WANDB_MODE", "online").lower()
    if mode == "disabled":
        return
    try:
        import wandb  # type: ignore
    except ImportError:
        return

    api_key = os.environ.get("WANDB_API_KEY")
    if not api_key:
        return

    try:
        wandb.login(key=api_key, relogin=True)
    except Exception as exc:  # pragma: no cover - best effort only
        print(f"[wandb] 자동 로그인에 실패했습니다: {exc}")

def ensure_patches() -> None:
    if PATCH_SCRIPT.exists():
        subprocess.run([str(PATCH_SCRIPT)], check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MARLlib experiments from the project root")
    parser.add_argument("--env", choices=["mpe", "overcooked"], required=True, help="Environment family")
    parser.add_argument("--map", required=True, help="Scenario / layout name")
    parser.add_argument("--algo", default="mappo", help="Algorithm name (e.g., mappo, qmix, ippo)")
    parser.add_argument("--timesteps", type=int, default=DEFAULT_TIMESTEPS, help="Total training timesteps")
    parser.add_argument("--stop-reward", type=float, default=DEFAULT_STOP_REWARD, help="Stop when mean reward >= value")
    parser.add_argument("--share-policy", default="group", help="Policy sharing mode (all/group/individual)")
    parser.add_argument("--num-workers", type=int, default=4, help="Number of rollout workers")
    parser.add_argument("--num-gpus", type=int, default=0, help="GPUs for training")
    parser.add_argument("--local-mode", action="store_true", help="Run Ray in local debug mode")
    parser.add_argument("--local-dir", default=str(DEFAULT_LOCAL_DIR), help="Ray results directory")
    parser.add_argument("--checkpoint-freq", type=int, default=DEFAULT_CHECKPOINT_FREQ, help="Checkpoint frequency (training iterations)")
    parser.add_argument("--core-arch", default="mlp", help="Model core architecture (mlp or rnn)")
    parser.add_argument("--encode-layer", default="128-256", help="Encoder layer sizes, e.g. 128-256")
    parser.add_argument("--force-coop", action="store_true", help="Force global reward for PettingZoo envs")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for the run (0이면 기본값 사용)")
    parser.add_argument("--wandb-config", default=None, help="configs/wandb/ 아래 설정 파일 이름")
    return parser.parse_args()


def validate_map(args: argparse.Namespace) -> None:
    if args.env == "mpe" and args.map not in MPE_MAPS:
        raise SystemExit(f"지원하지 않는 MPE 맵입니다: {args.map}. 사용 가능: {sorted(MPE_MAPS)}")
    if args.env == "overcooked" and args.map not in OVERCooked_MAPS:
        raise SystemExit(f"지원하지 않는 Overcooked 레이아웃입니다: {args.map}. 사용 가능: {sorted(OVERCooked_MAPS)}")


def make_environment(args: argparse.Namespace):
    force_flag = args.force_coop or args.env == "mpe"
    env = marl.make_env(
        environment_name=args.env,
        map_name=args.map,
        force_coop=force_flag,
    )
    return env


def choose_hyperparam_source(env_name: str) -> str:
    if env_name in {"mpe", "mamujoco", "smac"}:
        return env_name
    return "common"


def main() -> None:
    args = parse_args()
    validate_map(args)

    wandb_settings, wandb_overrides = load_wandb_config(args.wandb_config)
    apply_wandb_env(wandb_settings)
    login_to_wandb_if_possible()
    ensure_patches()

    if PATCH_SCRIPT.exists():
        os.system(f'"{PATCH_SCRIPT}"')

    if "timesteps" in wandb_overrides and args.timesteps == DEFAULT_TIMESTEPS:
        args.timesteps = int(wandb_overrides["timesteps"])
    if "stop_reward" in wandb_overrides and args.stop_reward == DEFAULT_STOP_REWARD:
        args.stop_reward = float(wandb_overrides["stop_reward"])
    if "checkpoint_freq" in wandb_overrides and args.checkpoint_freq == DEFAULT_CHECKPOINT_FREQ:
        args.checkpoint_freq = int(wandb_overrides["checkpoint_freq"])
    if "local_dir" in wandb_overrides and args.local_dir == str(DEFAULT_LOCAL_DIR):
        args.local_dir = wandb_overrides["local_dir"]

    env = make_environment(args)
    hyper_source = choose_hyperparam_source(args.env)

    algo_builder = getattr(marl.algos, args.algo, None)
    if algo_builder is None:
        raise SystemExit(f"알 수 없는 알고리즘입니다: {args.algo}")

    algo = algo_builder(hyperparam_source=hyper_source)
    model = marl.build_model(
        env,
        algo,
        {
            "core_arch": args.core_arch,
            "encode_layer": args.encode_layer,
        },
    )

    stop_config = {
        "timesteps_total": args.timesteps,
        "episode_reward_mean": args.stop_reward,
    }

    Path(args.local_dir).mkdir(parents=True, exist_ok=True)

    run_kwargs = {
        "share_policy": args.share_policy,
        "num_workers": args.num_workers,
        "num_gpus": args.num_gpus,
        "local_mode": args.local_mode,
        "local_dir": os.fspath(Path(args.local_dir).resolve()),
        "checkpoint_freq": args.checkpoint_freq,
        "checkpoint_end": True,
        "seed": int(args.seed),
    }

    tune_callbacks: List = []
    if wandb_settings.project and WandbLoggerCallback is not None:
        tags = list(wandb_settings.tags or [])
        tags.extend(
            [f"env:{args.env}", f"map:{args.map}", f"algo:{args.algo}"]
        )
        group_name = f"{args.env}:{args.map}"
        wandb_callback = WandbLoggerCallback(
            project=wandb_settings.project,
            entity=wandb_settings.entity,
            group=group_name,
            tags=tags,
            log_config=True,
        )
        tune_callbacks.append(wandb_callback)
    elif wandb_settings.project and WandbLoggerCallback is None:
        print("[wandb] Ray의 WandbLoggerCallback을 찾을 수 없어 W&B 로그를 비활성화합니다.")

    print("[MARLlib] start training")
    print(f" env      : {args.env}/{args.map}")
    print(f" algo     : {args.algo} (hyper params: {hyper_source})")
    print(f" timesteps: {args.timesteps}")
    print(f" results  : {run_kwargs['local_dir']}")
    if wandb_settings.project:
        ent = wandb_settings.entity or os.getenv("WANDB_ENTITY", "(unset)")
        mode = wandb_settings.mode or os.getenv("WANDB_MODE", "online")
        print(f" wandb    : {ent}/{wandb_settings.project} (mode={mode})")

    algo.fit(env, model, stop=stop_config, tune_callbacks=tune_callbacks, **run_kwargs)


if __name__ == "__main__":
    main()
