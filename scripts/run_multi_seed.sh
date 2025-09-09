#!/bin/bash
"""
여러 시드로 EPyMARL 실험을 실행하는 스크립트
시드 다양화를 통해 통계적으로 신뢰할 수 있는 결과를 얻습니다.

사용법:
  ./scripts/run_multi_seed.sh <algorithm> <environment_key> <num_seeds> [wandb_config] [additional_args...]

예시:
  ./scripts/run_multi_seed.sh qmix "matrixgames:penalty-100-nostate-v0" 5 matrix_games env_args.time_limit=25
  ./scripts/run_multi_seed.sh mappo "lbforaging:Foraging-8x8-2p-3f-v3" 3 foraging common_reward=False
"""

# 인자 검증
if [ $# -lt 3 ]; then
    echo "사용법: $0 <algorithm> <environment_key> <num_seeds> [wandb_config] [additional_args...]"
    echo ""
    echo "예시:"
    echo "  $0 qmix \"matrixgames:penalty-100-nostate-v0\" 5 matrix_games env_args.time_limit=25"
    echo "  $0 mappo \"lbforaging:Foraging-8x8-2p-3f-v3\" 3 foraging common_reward=False"
    exit 1
fi

ALGORITHM=$1
ENV_KEY=$2
NUM_SEEDS=$3
WANDB_CONFIG=${4:-"default"}

# 추가 인자들 (4번째 인자부터)
shift 4
ADDITIONAL_ARGS="$@"

# 스크립트 위치 기준으로 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== 멀티시드 EPyMARL 실험 시작 ==="
echo "알고리즘: $ALGORITHM"
echo "환경: $ENV_KEY"
echo "시드 개수: $NUM_SEEDS"
echo "W&B 설정: $WANDB_CONFIG"
echo "추가 인자: $ADDITIONAL_ARGS"
echo "========================================="
echo ""

# 시드 기반 실험 실행
for ((i=1; i<=NUM_SEEDS; i++)); do
    SEED=$((1000 + i))
    echo "[$i/$NUM_SEEDS] 시드 $SEED로 실험 실행 중..."
    
    # 환경에 따른 기본 설정
    if [[ "$ENV_KEY" == *"matrixgames"* ]]; then
        ENV_CONFIG="gymma"
        DEFAULT_ARGS="env_args.time_limit=25"
    elif [[ "$ENV_KEY" == *"lbforaging"* ]]; then
        ENV_CONFIG="gymma"
        DEFAULT_ARGS="env_args.time_limit=50"
    elif [[ "$ENV_KEY" == *"rware"* ]]; then
        ENV_CONFIG="gymma"
        DEFAULT_ARGS="env_args.time_limit=500"
    elif [[ "$ENV_KEY" == *"pz-mpe"* ]]; then
        ENV_CONFIG="gymma"
        DEFAULT_ARGS="env_args.time_limit=25"
    else
        ENV_CONFIG="gymma"
        DEFAULT_ARGS=""
    fi
    
    # W&B 실행 스크립트 사용
    python "$SCRIPT_DIR/run_with_wandb.py" \
        --config="$ALGORITHM" \
        --env-config="$ENV_CONFIG" \
        --wandb-config="$WANDB_CONFIG" \
        env_args.key="$ENV_KEY" \
        seed=$SEED \
        $DEFAULT_ARGS \
        $ADDITIONAL_ARGS
    
    # 실험 간 간격
    sleep 2
    echo ""
done

echo "=== 모든 시드 실험 완료 ==="
echo "결과는 results/ 디렉토리와 W&B에서 확인할 수 있습니다."