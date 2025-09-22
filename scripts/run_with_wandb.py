#!/usr/bin/env python3
"""
W&B 설정을 적용하여 EPyMARL 실험을 실행하는 스크립트
서브모듈을 수정하지 않고 상위 레벨에서 W&B 설정을 주입합니다.
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Any, Dict, Iterable, List

def load_wandb_config(config_name="default"):
    """W&B 설정 파일을 로드합니다."""
    config_path = Path(__file__).parent.parent / "configs" / "wandb" / f"{config_name}.yaml"
    
    if not config_path.exists():
        print(f"경고: W&B 설정 파일 {config_path}를 찾을 수 없습니다. 기본 설정을 사용합니다.")
        config_path = Path(__file__).parent.parent / "configs" / "wandb" / "default.yaml"
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        return {}


def resolve_exp_config_path(name: str) -> Path:
    """Resolve experiment config name or path to an absolute Path."""
    candidate = Path(name)
    if candidate.is_file():
        return candidate
    base = Path(__file__).parent.parent / "configs" / "exp"
    with_ext = candidate if candidate.suffix else candidate.with_suffix('.yaml')
    resolved = base / with_ext
    if not resolved.exists():
        raise FileNotFoundError(f"실험 설정 파일을 찾을 수 없습니다: {name}")
    return resolved


def load_exp_config(exp_config: str | None) -> Dict[str, Any]:
    if not exp_config:
        return {}
    path = resolve_exp_config_path(exp_config)
    with open(path, 'r', encoding='utf-8') as fp:
        data = yaml.safe_load(fp) or {}
    return data


def format_with_arg(key: str, value: Any) -> str:
    if isinstance(value, bool):
        return f"{key}={str(value).lower()}"
    if isinstance(value, (int, float)):
        return f"{key}={value}"
    if value is None:
        return key
    # 문자열은 공백/콜론이 포함될 수 있으므로 큰따옴표로 감싼다
    return f'{key}="{value}"'

def build_epymarl_command(args, wandb_config):
    """EPyMARL 실행 명령어를 구성합니다."""
    epymarl_path = Path(__file__).parent.parent / "external" / "epymarl" / "src" / "main.py"
    
    cmd_parts = [
        sys.executable,
        str(epymarl_path),
        f"--config={args.config}",
        f"--env-config={args.env_config}",
        "with"
    ]
    
    # EPyMARL 원본 인자들 추가 (실험 설정 → CLI 순으로 덮어쓰기)
    if getattr(args, 'exp_with_args', None):
        cmd_parts.extend(args.exp_with_args)
    if args.epymarl_args:
        cmd_parts.extend(args.epymarl_args)

    if len(cmd_parts) == 5:  # "with" 다음에 전달할 인자가 없다면 제거
        cmd_parts.pop()

    # W&B 설정 주입 (EPyMARL에서 지원하는 설정만)
    supported_wandb_keys = ['wandb_team', 'wandb_project', 'wandb_mode', 'wandb_save_model']
    for key, value in wandb_config.items():
        if key.startswith('wandb_') and key in supported_wandb_keys:
            if isinstance(value, bool):
                cmd_parts.append(f"{key}={str(value).lower()}")
            elif value is not None:
                cmd_parts.append(f'{key}="{value}"')
        elif key in ['use_wandb', 'use_tensorboard', 'save_model', 'save_model_interval', 'common_reward', 'reward_scalarisation', 'log_interval', 'test_interval', 'buffer_cpu_only', 'use_cuda', 'batch_size_run', 't_max', 'test_nepisode']:
            if isinstance(value, bool):
                cmd_parts.append(f"{key}={str(value).lower()}")
            elif key in ['save_model_interval', 'log_interval', 'test_interval', 'batch_size_run', 't_max', 'test_nepisode']:
                # 정수 타입 설정들은 따옴표 없이 전달
                cmd_parts.append(f"{key}={value}")
            elif value is not None:
                cmd_parts.append(f'{key}="{value}"')
    
    # 환경 변수에서 W&B 설정 가져오기
    if os.getenv('WANDB_ENTITY') and 'wandb_team' not in [k for k, v in wandb_config.items() if v is not None]:
        cmd_parts.append(f'wandb_team="{os.getenv("WANDB_ENTITY")}"')
    
    if os.getenv('WANDB_PROJECT') and 'wandb_project' not in [k for k, v in wandb_config.items() if v is not None]:
        cmd_parts.append(f'wandb_project="{os.getenv("WANDB_PROJECT")}"')
    
    return cmd_parts

def main():
    parser = argparse.ArgumentParser(description='W&B 설정과 함께 EPyMARL 실험을 실행합니다.')
    parser.add_argument('--config', help='EPyMARL 알고리즘 설정 (실험 설정 파일이 있으면 생략 가능)')
    parser.add_argument('--env-config', help='EPyMARL 환경 설정 (실험 설정 파일이 있으면 생략 가능)')
    parser.add_argument('--wandb-config', default=None, help='사용할 W&B 설정 파일명')
    parser.add_argument('--exp-config', help='configs/exp/ 아래 실험 설정 YAML 이름 또는 경로')
    parser.add_argument('epymarl_args', nargs='*', help='EPyMARL에 전달할 추가 인자들')
    
    args = parser.parse_args()
    
    exp_cfg = load_exp_config(args.exp_config)

    algo_from_cfg = exp_cfg.get('algo') or exp_cfg.get('config')
    if args.config and algo_from_cfg and args.config != algo_from_cfg:
        print(f"경고: --config({args.config})와 실험 설정({algo_from_cfg})이 다릅니다. --config 값을 사용합니다.")
    args.config = args.config or algo_from_cfg
    if not args.config:
        raise SystemExit("알고리즘(--config) 또는 실험 설정(algo)이 지정되어야 합니다.")

    env_config_from_cfg = exp_cfg.get('env_config')
    if args.env_config and env_config_from_cfg and args.env_config != env_config_from_cfg:
        print(f"경고: --env-config({args.env_config})와 실험 설정({env_config_from_cfg})이 다릅니다. --env-config 값을 사용합니다.")
    args.env_config = args.env_config or env_config_from_cfg
    if not args.env_config:
        raise SystemExit("환경 설정(--env-config) 또는 실험 설정(env_config)이 필요합니다.")

    wandb_from_cfg = exp_cfg.get('wandb_config')
    if args.wandb_config and wandb_from_cfg and args.wandb_config != wandb_from_cfg:
        print(f"경고: --wandb-config({args.wandb_config})와 실험 설정({wandb_from_cfg})이 다릅니다. --wandb-config 값을 사용합니다.")
    args.wandb_config = args.wandb_config or wandb_from_cfg or 'default'

    exp_with_args: List[str] = []
    if isinstance(exp_cfg.get('with'), dict):
        for key, value in exp_cfg['with'].items():
            exp_with_args.append(format_with_arg(key, value))
    if isinstance(exp_cfg.get('with_args'), Iterable):
        for token in exp_cfg['with_args']:
            if isinstance(token, str):
                exp_with_args.append(token)
    args.exp_with_args = exp_with_args

    # W&B 설정 로드
    wandb_config = load_wandb_config(args.wandb_config)

    # 명령어 구성
    cmd_parts = build_epymarl_command(args, wandb_config)
    
    # 명령어 출력 및 실행
    print("실행할 명령어:")
    print(" ".join(cmd_parts))
    print()
    
    # 실행
    os.execvp(cmd_parts[0], cmd_parts)

if __name__ == "__main__":
    main()
