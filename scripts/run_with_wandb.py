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
    
    # EPyMARL 원본 인자들 추가
    if args.epymarl_args:
        cmd_parts.extend(args.epymarl_args)
    
    # W&B 설정 주입
    for key, value in wandb_config.items():
        if key.startswith('wandb_') or key in ['use_wandb', 'use_tensorboard', 'save_model', 'save_model_interval', 'common_reward', 'reward_scalarisation', 'log_interval', 'test_interval', 'buffer_cpu_only', 'use_cuda', 'batch_size_run']:
            if isinstance(value, bool):
                cmd_parts.append(f"{key}={str(value).lower()}")
            elif isinstance(value, list):
                # 리스트는 문자열로 변환 (wandb_tags 등)
                cmd_parts.append(f'{key}="{",".join(map(str, value))}"')
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
    parser.add_argument('--config', required=True, help='EPyMARL 알고리즘 설정')
    parser.add_argument('--env-config', required=True, help='EPyMARL 환경 설정')
    parser.add_argument('--wandb-config', default='default', help='사용할 W&B 설정 파일명')
    parser.add_argument('epymarl_args', nargs='*', help='EPyMARL에 전달할 추가 인자들')
    
    args = parser.parse_args()
    
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