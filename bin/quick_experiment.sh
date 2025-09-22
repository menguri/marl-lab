#!/bin/bash
"""
빠른 실험을 위한 스크립트
알고리즘 개발 및 테스트 시 짧은 실험으로 빠르게 검증할 수 있습니다.

사용법:
  ./bin/quick_experiment.sh <algorithm> <environment> [additional_args...]

예시:
  ./bin/quick_experiment.sh qmix matrix_penalty
  ./bin/quick_experiment.sh mappo lbf_small common_reward=False
"""

if [ $# -lt 2 ]; then
    echo "사용법: $0 <algorithm> <environment> [additional_args...]"
    echo ""
    echo "지원하는 환경 (통합 스크립트 사용 권장):"
    echo "  python scripts/unified_experiment.py --action list --category quick"
    echo ""
    echo "또는 통합 실험 스크립트 사용:"
    echo "  python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty --quick"
    exit 1
fi

ALGORITHM=$1
ENVIRONMENT=$2
shift 2
ADDITIONAL_ARGS="$@"

# 스크립트 위치 기준으로 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== 빠른 실험 실행 ==="
echo "알고리즘: $ALGORITHM"
echo "환경: $ENVIRONMENT"
echo "===================="

# 환경별 설정
ENV_CONFIG="gymma"

case $ENVIRONMENT in
    "matrix_penalty")
        ENV_KEY="matrixgames:penalty-100-nostate-v0"
        WANDB_CONFIG="matrix_games"
        DEFAULT_ARGS="env_args.time_limit=10 t_max=5000"
        ;;
    "matrix_climbing")
        ENV_KEY="matrixgames:climbing-nostate-v0"
        WANDB_CONFIG="matrix_games"
        DEFAULT_ARGS="env_args.time_limit=10 t_max=5000"
        ;;
    "lbf_small")
        ENV_KEY="lbforaging:Foraging-8x8-2p-3f-v3"
        WANDB_CONFIG="foraging"
        DEFAULT_ARGS="env_args.time_limit=25 t_max=20000"
        ;;
    "lbf_medium")
        ENV_KEY="lbforaging:Foraging-10x10-3p-3f-v3"
        WANDB_CONFIG="foraging"
        DEFAULT_ARGS="env_args.time_limit=25 t_max=20000"
        ;;
    "rware_tiny")
        ENV_KEY="rware:rware-tiny-2ag-v2"
        WANDB_CONFIG="default"
        DEFAULT_ARGS="env_args.time_limit=100 t_max=20000"
        ;;
    "mpe_spread")
        ENV_KEY="pz-mpe-simple-spread-v3"
        WANDB_CONFIG="default"
        DEFAULT_ARGS="env_args.time_limit=15 t_max=15000"
        ;;
    "smac2_terran")
        ENV_KEY="terran_5_vs_5"
        WANDB_CONFIG="smac2"
        DEFAULT_ARGS="t_max=100000"
        ENV_CONFIG="sc2v2"
        ;;
    "smac2_protoss")
        ENV_KEY="protoss_5_vs_5"
        WANDB_CONFIG="smac2"
        DEFAULT_ARGS="t_max=100000"
        ENV_CONFIG="sc2v2"
        ;;
    "smac2_zerg")
        ENV_KEY="zerg_5_vs_5"
        WANDB_CONFIG="smac2"
        DEFAULT_ARGS="t_max=100000"
        ENV_CONFIG="sc2v2"
        ;;
    *)
        echo "지원하지 않는 환경: $ENVIRONMENT"
        exit 1
        ;;
esac

# 실험 실행
python "$PROJECT_ROOT/scripts/run_with_wandb.py" \
    --config="$ALGORITHM" \
    --env-config="$ENV_CONFIG" \
    --wandb-config="$WANDB_CONFIG" \
    env_args.key="$ENV_KEY" \
    $DEFAULT_ARGS \
    $ADDITIONAL_ARGS

echo ""
echo "=== 빠른 실험 완료 ==="
