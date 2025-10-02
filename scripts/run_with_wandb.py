#!/usr/bin/env python3
"""Launch PyMARL2 experiments with W&B configuration overlays."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
PYMARL2_MAIN = ROOT / "external" / "pymarl2" / "src" / "main.py"
PATCH_SCRIPT = ROOT / "scripts" / "apply_pymarl2_patches.sh"

from wandb_utils import apply_wandb_env, format_overrides, load_wandb_config  # noqa: E402




def login_to_wandb_if_possible() -> None:
    """Attempt non-interactive wandb.login using the exported API key."""
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
    except Exception as exc:  # pragma: no cover - best effort
        print(f"[wandb] 자동 로그인에 실패했습니다: {exc}", file=sys.stderr)


def ensure_patches() -> None:
    if PATCH_SCRIPT.exists():
        subprocess.run([str(PATCH_SCRIPT)], check=True)


def resolve_exp_config_path(name: str) -> Path:
    candidate = Path(name)
    if candidate.is_file():
        return candidate
    base = ROOT / "configs" / "exp"
    if candidate.suffix:
        resolved = base / candidate
    else:
        resolved = base / f"{name}.yaml"
    if not resolved.exists():
        raise FileNotFoundError(f"실험 설정 파일을 찾을 수 없습니다: {name}")
    return resolved


def load_exp_config(exp_config: str | None) -> Dict[str, Any]:
    if not exp_config:
        return {}
    with resolve_exp_config_path(exp_config).open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def format_with_arg(key: str, value: Any) -> str:
    if isinstance(value, bool):
        return f"{key}={str(value)}"
    if isinstance(value, (int, float)):
        return f"{key}={value}"
    if value is None:
        return key
    return f'{key}="{value}"'


def merge_with_arguments(primary: Iterable[str] | None, override: Iterable[str] | None) -> List[str]:
    def arg_key(token: str) -> str | None:
        if "=" not in token:
            return None
        return token.split("=", 1)[0]

    merged: List[str] = []
    for token_list in (primary or [], override or []):
        for token in token_list:
            if not token:
                continue
            if token == "with":
                continue
            key = arg_key(token)
            if key:
                for idx in range(len(merged) - 1, -1, -1):
                    if arg_key(merged[idx]) == key:
                        merged.pop(idx)
                        break
            merged.append(token)
    return merged


def build_pymarl2_command(
    args: argparse.Namespace, combined_with_args: List[str]
) -> List[str]:
    cmd_parts = [
        sys.executable,
        str(PYMARL2_MAIN),
        f"--config={args.config}",
        f"--env-config={args.env_config}",
    ]

    has_local_results_path = any(
        token.startswith("local_results_path") for token in (combined_with_args or [])
    )
    if not has_local_results_path:
        if not combined_with_args:
            combined_with_args = []
        combined_with_args.append('local_results_path="results/pymarl2"')
    if combined_with_args:
        cmd_parts.append("with")
        cmd_parts.extend(combined_with_args)

    return cmd_parts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PyMARL2 + W&B 실행 헬퍼")
    parser.add_argument("--config", required=False, help="PyMARL2 알고리즘 설정 이름")
    parser.add_argument("--env-config", required=False, help="PyMARL2 환경 설정 이름")
    parser.add_argument("--wandb-config", default=None, help="configs/wandb/ 아래 설정 파일 이름")
    parser.add_argument("--exp-config", help="configs/exp/ 아래 실험 설정 YAML 이름 또는 경로")
    parser.add_argument("extra_args", nargs="*", help="PyMARL2 main.py에 전달할 추가 인자 (key=value)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exp_cfg = load_exp_config(args.exp_config)

    algo_from_cfg = exp_cfg.get("algo") or exp_cfg.get("config")
    if args.config and algo_from_cfg and args.config != algo_from_cfg:
        print(f"경고: --config({args.config}) != 실험 설정({algo_from_cfg}). --config 우선 적용")
    args.config = args.config or algo_from_cfg
    if not args.config:
        raise SystemExit("알고리즘(--config) 또는 실험 설정(algo)이 필요합니다.")

    env_from_cfg = exp_cfg.get("env_config")
    if args.env_config and env_from_cfg and args.env_config != env_from_cfg:
        print(f"경고: --env-config({args.env_config}) != 실험 설정({env_from_cfg}). --env-config 우선 적용")
    args.env_config = args.env_config or env_from_cfg
    if not args.env_config:
        raise SystemExit("환경 설정(--env-config) 또는 실험 설정(env_config)이 필요합니다.")

    wandb_from_cfg = exp_cfg.get("wandb_config")
    if args.wandb_config and wandb_from_cfg and args.wandb_config != wandb_from_cfg:
        print(f"경고: --wandb-config({args.wandb_config}) != 실험 설정({wandb_from_cfg}). --wandb-config 우선 적용")
    args.wandb_config = args.wandb_config or wandb_from_cfg or "default"

    exp_with_args: List[str] = []
    if isinstance(exp_cfg.get("with"), dict):
        exp_with_args.extend(format_with_arg(k, v) for k, v in exp_cfg["with"].items())
    if isinstance(exp_cfg.get("with_args"), Iterable):
        exp_with_args.extend(token for token in exp_cfg["with_args"] if isinstance(token, str))
    args.exp_with_args = exp_with_args

    ensure_patches()

    wandb_settings, wandb_overrides = load_wandb_config(args.wandb_config)
    apply_wandb_env(wandb_settings)

    login_to_wandb_if_possible()

    forwardable_keys = {
        "save_model",
        "save_model_interval",
        "use_tensorboard",
        "log_interval",
        "test_interval",
        "test_nepisode",
        "t_max",
        "batch_size_run",
        "buffer_cpu_only",
        "use_cuda",
        "local_results_path",
    }

    combined_with_args = merge_with_arguments(
        format_overrides(wandb_overrides, forwardable_keys),
        args.exp_with_args,
    )
    combined_with_args = merge_with_arguments(
        combined_with_args,
        args.extra_args,
    )

    command = build_pymarl2_command(args, combined_with_args)

    if wandb_settings.project:
        ent = wandb_settings.entity or os.getenv("WANDB_ENTITY", "(unset)")
        mode = wandb_settings.mode or os.getenv("WANDB_MODE", "online")
        print(f"W&B 설정  : {ent}/{wandb_settings.project} (mode={mode})")

    print("실행할 명령어:\n", " ".join(command), "\n")
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
