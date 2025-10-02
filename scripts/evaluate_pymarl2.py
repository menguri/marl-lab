#!/usr/bin/env python3
"""Evaluate a trained PyMARL2 checkpoint and optionally save SC2 replays."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]
PYMARL2_MAIN = ROOT / "external" / "pymarl2" / "src" / "main.py"
PATCH_SCRIPT = ROOT / "scripts" / "apply_pymarl2_patches.sh"


def build_command(args: argparse.Namespace) -> List[str]:
    command: List[str] = [
        sys.executable,
        str(PYMARL2_MAIN),
        f"--config={args.config}",
        f"--env-config={args.env_config}",
    ]

    with_tokens: List[str] = [
        f'checkpoint_path="{args.checkpoint}"',
        f"load_step={args.load_step}",
        "evaluate=True",
        f"test_nepisode={args.test_episodes}",
    ]
    if args.save_replay:
        with_tokens.append("save_replay=True")
    if args.extra_with:
        with_tokens.extend(args.extra_with)

    command.append("with")
    command.extend(with_tokens)
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PyMARL2 체크포인트 평가")
    parser.add_argument("--config", required=True, help="PyMARL2 알고리즘 설정 이름")
    parser.add_argument("--env-config", required=True, help="PyMARL2 환경 설정 이름")
    parser.add_argument("--checkpoint", required=True, help="모델이 저장된 디렉터리 (results/models/…)" )
    parser.add_argument("--load-step", type=int, default=0, help="불러올 스텝 (0이면 최신)")
    parser.add_argument("--test-episodes", type=int, default=20, help="평가 에피소드 수")
    parser.add_argument("--save-replay", action="store_true", help="SC2 리플레이 저장 여부")
    parser.add_argument("extra_with", nargs="*", help="추가 with 인자 (key=value)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if PATCH_SCRIPT.exists():
        subprocess.run([str(PATCH_SCRIPT)], check=True)
    command = build_command(args)
    print("실행할 명령어:\n", " ".join(command), "\n")
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
