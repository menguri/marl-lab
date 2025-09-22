#!/usr/bin/env python3
"""
여러 알고리즘을 동일한 환경에서 비교 실험하는 스크립트
알고리즘 개발 시 성능 비교를 위해 사용합니다.

사용법:
  python scripts/algorithm_comparison.py --env matrix_penalty --algorithms qmix vdn qtran --seeds 3
  python scripts/algorithm_comparison.py --env lbf_small --algorithms mappo ippo maa2c --seeds 5 --individual-rewards
"""

import argparse
import subprocess
import sys
from pathlib import Path
import time

# 기존 환경 설정을 통합 설정으로 대체
# 새로운 통합 스크립트 사용 권장: scripts/unified_experiment.py

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from configs.python.environments import ENVIRONMENTS, get_environment_config

# 호환성을 위한 전환 사전
COMPATIBILITY_ENVIRONMENTS = {
    'matrix_penalty': {
        'key': 'matrixgames:penalty-100-nostate-v0',
        'config': 'gymma',
        'wandb_config': 'matrix_games',
        'default_args': 'env_args.time_limit=25 t_max=50000'
    },
    'matrix_climbing': {
        'key': 'matrixgames:climbing-nostate-v0',
        'config': 'gymma',
        'wandb_config': 'matrix_games',
        'default_args': 'env_args.time_limit=25 t_max=50000'
    },
    'lbf_small': {
        'key': 'lbforaging:Foraging-8x8-2p-3f-v3',
        'config': 'gymma',
        'wandb_config': 'foraging',
        'default_args': 'env_args.time_limit=50 t_max=500000'
    },
    'lbf_medium': {
        'key': 'lbforaging:Foraging-10x10-3p-3f-v3',
        'config': 'gymma',
        'wandb_config': 'foraging',
        'default_args': 'env_args.time_limit=50 t_max=500000'
    },
    'rware_tiny': {
        'key': 'rware:rware-tiny-2ag-v2',
        'config': 'gymma',
        'wandb_config': 'default',
        'default_args': 'env_args.time_limit=500 t_max=1000000'
    },
    'smac2_terran': {
        'key': 'terran_5_vs_5',
        'config': 'sc2v2',
        'wandb_config': 'smac2',
        'default_args': 't_max=2000000'
    },
    'smac2_protoss': {
        'key': 'protoss_5_vs_5',
        'config': 'sc2v2',
        'wandb_config': 'smac2',
        'default_args': 't_max=2000000'
    },
    'smac2_zerg': {
        'key': 'zerg_5_vs_5',
        'config': 'sc2v2',
        'wandb_config': 'smac2',
        'default_args': 't_max=2000000'
    },
    # SMAC1 환경 추가
    'smac_3s5z': {
        'key': '3s5z',
        'config': 'sc2',
        'wandb_config': 'smac1',
        'default_args': 'env_args.map_name="3s5z" t_max=2000000'
    },
    'smac_2s_vs_1sc': {
        'key': '2s_vs_1sc',
        'config': 'sc2',
        'wandb_config': 'smac1',
        'default_args': 'env_args.map_name="2s_vs_1sc" t_max=2000000'
    },
    'smac_MMM2': {
        'key': 'MMM2',
        'config': 'sc2',
        'wandb_config': 'smac1',
        'default_args': 'env_args.map_name="MMM2" t_max=2000000'
    }
}

def run_experiment(algorithm, env_config, seed, individual_rewards=False, additional_args=""):
    \"\"\"
    주의: 이 스크립트는 호환성을 위해 유지되지만, 
    새로운 통합 실험 스크립트 사용을 권장합니다:
    python scripts/unified_experiment.py --algorithm <alg> --environment <env> --seeds <n>
    \"\"\"
    """단일 실험을 실행합니다."""
    script_dir = Path(__file__).parent
    run_script = script_dir / "run_with_wandb.py"
    
    cmd = [
        sys.executable,
        str(run_script),
        f"--config={algorithm}",
        f"--env-config={env_config['config']}",
        f"--wandb-config={env_config['wandb_config']}",
        f"env_args.key={env_config['key']}",
        f"seed={seed}"
    ]
    
    # 기본 인자 추가
    if env_config['default_args']:
        cmd.extend(env_config['default_args'].split())
    
    # 개별 보상 설정
    if individual_rewards:
        cmd.append("common_reward=False")
    
    # 추가 인자
    if additional_args:
        cmd.extend(additional_args.split())
    
    print(f"실행 중: {algorithm} (시드 {seed})")
    print(f"명령어: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='여러 알고리즘 성능 비교 실험')
    parser.add_argument('--env', required=True, choices=list(ENVIRONMENTS.keys()),
                        help='실험할 환경')
    parser.add_argument('--algorithms', required=True, nargs='+',
                        help='비교할 알고리즘들')
    parser.add_argument('--seeds', type=int, default=3,
                        help='각 알고리즘당 실행할 시드 개수')
    parser.add_argument('--individual-rewards', action='store_true',
                        help='개별 보상 환경으로 실행 (지원하는 알고리즘만)')
    parser.add_argument('--additional-args', default="",
                        help='추가 인자들')
    parser.add_argument('--delay', type=int, default=5,
                        help='실험 간 대기 시간(초)')
    
    args = parser.parse_args()
    
    env_config = ENVIRONMENTS[args.env]
    
    print("=== 알고리즘 비교 실험 시작 ===")
    print(f"환경: {args.env} ({env_config['key']})")
    print(f"알고리즘: {', '.join(args.algorithms)}")
    print(f"시드 개수: {args.seeds}")
    print(f"개별 보상: {args.individual_rewards}")
    print("=" * 40)
    
    total_experiments = len(args.algorithms) * args.seeds
    current_experiment = 0
    
    for algorithm in args.algorithms:
        print(f"\n[{algorithm}] 실험 시작")
        
        for seed_idx in range(args.seeds):
            current_experiment += 1
            seed = 1000 + seed_idx + 1
            
            print(f"\n진행률: {current_experiment}/{total_experiments}")
            
            success = run_experiment(
                algorithm, 
                env_config, 
                seed, 
                args.individual_rewards,
                args.additional_args
            )
            
            if not success:
                print(f"경고: {algorithm} 시드 {seed} 실험 실패")
            
            # 마지막 실험이 아니면 대기
            if current_experiment < total_experiments:
                time.sleep(args.delay)
    
    print("\n=== 모든 비교 실험 완료 ===")
    print("결과는 results/ 디렉토리와 W&B에서 확인할 수 있습니다.")

if __name__ == "__main__":
    main()
