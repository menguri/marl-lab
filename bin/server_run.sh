#!/bin/bash
"""
서버 환경에서 EPyMARL 실험을 실행하는 스크립트
환경 변수와 서버 최적화 설정을 자동으로 적용합니다.

사용법:
  ./bin/server_run.sh <algorithm> <environment> [wandb_config] [additional_args...]

예시:
  ./bin/server_run.sh qmix smac2_terran server_default
  ./bin/server_run.sh mappo lbf_small foraging common_reward=False
"""

# 서버 설정 로드
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 서버 환경 설정 로드
if [ -f "$PROJECT_ROOT/configs/server/setup.sh" ]; then
    source "$PROJECT_ROOT/configs/server/setup.sh"
else
    echo "경고: 서버 설정 파일을 찾을 수 없습니다: $PROJECT_ROOT/configs/server/setup.sh"
fi

# 인자 검증
if [ $# -lt 2 ]; then
    echo "사용법: $0 <algorithm> <environment> [wandb_config] [additional_args...]"
    echo ""
    echo "지원하는 환경:"
    echo "  matrix_penalty, matrix_climbing"
    echo "  lbf_small, lbf_medium"
    echo "  rware_tiny"
    echo "  mpe_spread"
    echo "  smac2_terran, smac2_protoss, smac2_zerg"
    exit 1
fi

ALGORITHM=$1
ENVIRONMENT=$2
WANDB_CONFIG=${3:-"server_default"}  # 기본값: server_default

# 추가 인자들
shift 3
ADDITIONAL_ARGS="$@"

echo "=== 서버 EPyMARL 실험 시작 ==="
echo "알고리즘: $ALGORITHM"
echo "환경: $ENVIRONMENT"
echo "W&B 설정: $WANDB_CONFIG"
echo "W&B Entity: ${WANDB_ENTITY:-'설정되지 않음'}"
echo "W&B Project: ${WANDB_PROJECT:-'설정되지 않음'}"
echo "추가 인자: $ADDITIONAL_ARGS"
echo "==============================="

# quick_experiment.sh 스타일로 환경 설정
case $ENVIRONMENT in
    "matrix_penalty"|"matrix_climbing"|"lbf_small"|"lbf_medium"|"rware_tiny"|"mpe_spread"|"smac2_terran"|"smac2_protoss"|"smac2_zerg")
        # 지원하는 환경 - quick_experiment.sh 사용
        "$SCRIPT_DIR/quick_experiment.sh" "$ALGORITHM" "$ENVIRONMENT" \
            wandb_config="$WANDB_CONFIG" \
            $ADDITIONAL_ARGS
        ;;
    *)
        # 직접 설정한 환경 키 - run_with_wandb.py 직접 사용
        python "$PROJECT_ROOT/scripts/run_with_wandb.py" \
            --config="$ALGORITHM" \
            --env-config="gymma" \
            --wandb-config="$WANDB_CONFIG" \
            env_args.key="$ENVIRONMENT" \
            $ADDITIONAL_ARGS
        ;;
esac

echo ""
echo "=== 서버 실험 완료 ==="

# W&B 결과 확인 안내
if [ "$WANDB_MODE" = "offline" ] || [ -z "$WANDB_MODE" ]; then
    echo "오프라인 모드로 실행되었습니다. 다음 명령어로 W&B에 업로드하세요:"
    echo "  wandb sync $WANDB_DIR"
fi
