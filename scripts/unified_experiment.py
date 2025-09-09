#!/usr/bin/env python3
"""
통합 실험 실행 스크립트
모든 환경과 설정을 중앙에서 관리하는 통합된 인터페이스입니다.

사용법:
  python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty
  python scripts/unified_experiment.py --algorithm mappo --environment lbf_small --individual-rewards
  python scripts/unified_experiment.py --algorithm qmix --environment smac_3s5z --wandb-config server_default
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.environments import (
    ENVIRONMENTS, ALGORITHM_RECOMMENDATIONS, 
    get_environment_config, get_supported_environments,
    get_algorithm_recommendations, filter_environments_by_category
)

def validate_algorithm_environment(algorithm: str, environment: str, individual_rewards: bool = False) -> tuple[bool, str]:
    """알고리즘과 환경의 호환성을 검증합니다."""
    env_config = get_environment_config(environment)
    if not env_config:
        return False, f"지원하지 않는 환경: {environment}"
    
    alg_recommendations = get_algorithm_recommendations(algorithm)
    if environment not in alg_recommendations.get('supported_envs', []):
        return False, f"알고리즘 {algorithm}는 환경 {environment}를 지원하지 않습니다"
    
    # 개별 보상 설정 검증
    if individual_rewards and not env_config.supports_individual_rewards:
        return False, f"환경 {environment}는 개별 보상을 지원하지 않습니다"
    
    # 공통 보상 전용 알고리즘 검증
    common_reward_only_algorithms = ['qmix', 'vdn', 'qtran', 'coma']
    if algorithm in common_reward_only_algorithms and individual_rewards:
        return False, f"알고리즘 {algorithm}는 개별 보상 모드를 지원하지 않습니다"
    
    return True, "호환성 검증 통과"

def run_experiment(algorithm: str, environment: str, wandb_config: str = None, 
                  individual_rewards: bool = False, seeds: int = 1, 
                  additional_args: str = "", quick_mode: bool = False) -> bool:
    """실험을 실행합니다."""
    
    # 호환성 검증
    is_valid, message = validate_algorithm_environment(algorithm, environment, individual_rewards)
    if not is_valid:
        print(f"❌ 호환성 오류: {message}")
        return False
    
    env_config = get_environment_config(environment)
    
    # W&B 설정 자동 선택
    if not wandb_config:
        wandb_config = env_config.wandb_config
    
    # 빠른 모드 설정
    if quick_mode:
        quick_t_max = min(env_config.t_max // 10, 50000) if env_config.t_max else 20000
        additional_args = f"t_max={quick_t_max} {additional_args}"
    
    # 개별 보상 설정 추가
    if individual_rewards:
        additional_args = f"common_reward=false {additional_args}"
    
    print(f"🚀 실험 시작")
    print(f"   알고리즘: {algorithm}")
    print(f"   환경: {environment} ({env_config.description})")
    print(f"   W&B 설정: {wandb_config}")
    print(f"   시드 개수: {seeds}")
    print(f"   개별 보상: {individual_rewards}")
    print(f"   빠른 모드: {quick_mode}")
    print("=" * 50)
    
    script_dir = Path(__file__).parent
    
    if seeds == 1:
        # 단일 실험
        run_script = script_dir / "run_with_wandb.py"
        cmd = [
            sys.executable, str(run_script),
            f"--config={algorithm}",
            f"--env-config={env_config.env_config}",
            f"--wandb-config={wandb_config}",
            f"env_args.key={env_config.key}" if env_config.env_config == "gymma" else f"env_args.map_name={env_config.key}",
            env_config.default_args
        ]
        
        if additional_args:
            cmd.extend(additional_args.split())
        
        print(f"실행 명령어: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        return result.returncode == 0
    
    else:
        # 다중 시드 실험
        multi_seed_script = script_dir / "run_multi_seed.sh"
        env_key = env_config.key
        cmd = [
            str(multi_seed_script),
            algorithm,
            f'"{env_key}"',
            str(seeds),
            wandb_config
        ]
        
        # 환경별 추가 설정
        if env_config.default_args:
            cmd.append(env_config.default_args)
        
        if additional_args:
            cmd.append(additional_args)
        
        print(f"실행 명령어: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        return result.returncode == 0

def list_environments(category: str = None, algorithm: str = None):
    """지원하는 환경들을 나열합니다."""
    print("🌍 지원하는 환경들")
    print("=" * 50)
    
    if algorithm:
        # 특정 알고리즘 추천 환경
        recommendations = get_algorithm_recommendations(algorithm)
        print(f"📊 알고리즘 '{algorithm}' 정보:")
        print(f"   설명: {recommendations.get('description', 'No description')}")
        
        print(f"\n✅ 추천 환경:")
        for env_name in recommendations.get('good', []):
            env_config = get_environment_config(env_name)
            if env_config:
                rewards_info = "개별/공통 보상" if env_config.supports_individual_rewards else "공통 보상만"
                print(f"   {env_name:<20} - {env_config.description} ({rewards_info})")
        
        print(f"\n🔧 지원하는 모든 환경:")
        for env_name in recommendations.get('supported_envs', []):
            if env_name not in recommendations.get('good', []):
                env_config = get_environment_config(env_name)
                if env_config:
                    rewards_info = "개별/공통 보상" if env_config.supports_individual_rewards else "공통 보상만"
                    print(f"   {env_name:<20} - {env_config.description} ({rewards_info})")
        return
    
    if category:
        # 특정 카테고리 환경
        envs = filter_environments_by_category(category)
        if envs:
            print(f"📂 카테고리: {category.upper()}")
            for name, config in envs.items():
                rewards_info = "개별/공통 보상" if config.supports_individual_rewards else "공통 보상만"
                print(f"   {name:<20} - {config.description} ({rewards_info})")
        else:
            print(f"❌ 카테고리 '{category}'를 찾을 수 없습니다.")
            print("사용 가능한 카테고리: matrix, lbf, rware, mpe, smac1, smac2, vmas, quick, individual_rewards")
        return
    
    # 전체 환경 (카테고리별)
    categories = ['matrix', 'lbf', 'rware', 'mpe', 'smac1', 'smac2', 'vmas']
    for cat in categories:
        envs = filter_environments_by_category(cat)
        if envs:
            print(f"\n📂 {cat.upper()}:")
            for name, config in envs.items():
                rewards_info = "개별/공통 보상" if config.supports_individual_rewards else "공통 보상만"
                print(f"   {name:<20} - {config.description} ({rewards_info})")

def main():
    parser = argparse.ArgumentParser(description='통합 EPyMARL 실험 실행 스크립트')
    
    # 액션 선택
    parser.add_argument('--action', choices=['run', 'list'], default='run',
                       help='실행할 액션 (run: 실험 실행, list: 환경 목록)')
    
    # 실험 실행 옵션
    parser.add_argument('--algorithm', '-a', help='실험할 알고리즘')
    parser.add_argument('--environment', '-e', help='실험할 환경')
    parser.add_argument('--wandb-config', help='사용할 W&B 설정')
    parser.add_argument('--individual-rewards', action='store_true',
                       help='개별 보상 모드로 실행')
    parser.add_argument('--seeds', type=int, default=1,
                       help='실행할 시드 개수')
    parser.add_argument('--quick', action='store_true',
                       help='빠른 모드 (짧은 학습)')
    parser.add_argument('--additional-args', default="",
                       help='추가 EPyMARL 인자들')
    
    # 환경 목록 옵션
    parser.add_argument('--category', help='특정 카테고리의 환경만 표시')
    parser.add_argument('--for-algorithm', help='특정 알고리즘에 적합한 환경들 표시')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_environments(args.category, args.for_algorithm)
        return
    
    # 실험 실행
    if not args.algorithm or not args.environment:
        print("❌ 실험 실행을 위해서는 --algorithm과 --environment가 필요합니다.")
        parser.print_help()
        return
    
    success = run_experiment(
        algorithm=args.algorithm,
        environment=args.environment,
        wandb_config=args.wandb_config,
        individual_rewards=args.individual_rewards,
        seeds=args.seeds,
        additional_args=args.additional_args,
        quick_mode=args.quick
    )
    
    if success:
        print("✅ 실험이 성공적으로 완료되었습니다!")
    else:
        print("❌ 실험 실행 중 오류가 발생했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()