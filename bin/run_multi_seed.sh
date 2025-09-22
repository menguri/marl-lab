#!/bin/bash
"""
여러 시드로 EPyMARL 실험을 실행하는 스크립트
시드 다양화를 통해 통계적으로 신뢰할 수 있는 결과를 얻습니다.

사용법:
  ./bin/run_multi_seed.sh <algorithm> <environment_key> <num_seeds> [wandb_config] [additional_args...]

예시:
  ./bin/run_multi_seed.sh qmix "matrixgames:penalty-100-nostate-v0" 5 matrix_games env_args.time_limit=25
  ./bin/run_multi_seed.sh mappo "lbforaging:Foraging-8x8-2p-3f-v3" 3 foraging common_reward=False
  ./bin/run_multi_seed.sh vdn sc2 5 smac1 env_args.map_name=3m

동시 실행:
  RUN_MULTI_SEED_WORKERS=N 환경 변수를 설정하면 최대 N개의 실험을 동시에 실행합니다.
  예) RUN_MULTI_SEED_WORKERS=4 ./bin/run_multi_seed.sh qmix ...
"""

# 인자 검증
if [ $# -lt 3 ]; then
    echo "사용법: $0 <algorithm> <environment_key> <num_seeds> [wandb_config] [additional_args...]"
    echo ""
    echo "예시:"
    echo "  $0 qmix \"matrixgames:penalty-100-nostate-v0\" 5 matrix_games env_args.time_limit=25"
    echo "  $0 mappo \"lbforaging:Foraging-8x8-2p-3f-v3\" 3 foraging common_reward=False"
    echo "  $0 vdn sc2 5 smac1 env_args.map_name=3m"
    exit 1
fi

# 서버 설정 로드
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1
if [ -f "$PROJECT_ROOT/configs/server/setup.sh" ]; then
    source "$PROJECT_ROOT/configs/server/setup.sh"
else
    echo "경고: 서버 설정 파일을 찾을 수 없습니다: $PROJECT_ROOT/configs/server/setup.sh"
fi

# 인자 설정
ALGORITHM=$1
ENV_KEY=$2
NUM_SEEDS=$3
WANDB_CONFIG=${4:-"default"}

# 추가 인자들 (4번째 인자부터) - 배열로 보관
shift 4
RAW_ADDITIONAL_ARGS=("$@")
ADDITIONAL_ARGS=()
EXP_CONFIG=""

for arg in "${RAW_ADDITIONAL_ARGS[@]}"; do
    if [[ "$arg" == RUN_MULTI_SEED_WORKERS=* ]]; then
        echo "경고: RUN_MULTI_SEED_WORKERS는 인자가 아니라 환경 변수로 설정하세요 (예: RUN_MULTI_SEED_WORKERS=4 $0 ...)."
        continue
    fi
    if [[ "$arg" == exp_config=* ]]; then
        EXP_CONFIG="${arg#exp_config=}"
        continue
    fi
    if [ -n "$arg" ]; then
        ADDITIONAL_ARGS+=("$arg")
    fi
done

# 스크립트 위치 기준으로 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== 멀티시드 EPyMARL 실험 시작 ==="
MAX_WORKERS=${RUN_MULTI_SEED_WORKERS:-1}
if ! [[ "$MAX_WORKERS" =~ ^[0-9]+$ ]] || [ "$MAX_WORKERS" -lt 1 ]; then
    echo "경고: RUN_MULTI_SEED_WORKERS 값이 잘못되었습니다. 1로 설정합니다."
    MAX_WORKERS=1
fi

echo "알고리즘: $ALGORITHM"
echo "환경: $ENV_KEY"
echo "시드 개수: $NUM_SEEDS"
echo "W&B 설정: $WANDB_CONFIG"
echo "추가 인자: ${ADDITIONAL_ARGS[*]}"
if [ -n "$EXP_CONFIG" ]; then
    echo "실험 설정: $EXP_CONFIG"
fi
echo "동시 실행 워커 수: $MAX_WORKERS"
echo "========================================="
echo ""

declare -a JOB_PIDS=()
FAILURE_DETECTED=0

cleanup_jobs() {
    if [ ${#JOB_PIDS[@]} -gt 0 ]; then
        echo "정리: 실행 중인 모든 실험을 종료합니다..."
        kill "${JOB_PIDS[@]}" 2>/dev/null
    fi
}
trap cleanup_jobs INT TERM

# 시드 기반 실험 실행
for ((i=1; i<=NUM_SEEDS; i++)); do
    SEED=$((1000 + i))
    echo "[$i/$NUM_SEEDS] 시드 $SEED로 실험 실행 중..."
    
    # 환경에 따른 기본 설정
    DEFAULT_ARGS=()
    if [[ "$ENV_KEY" == *"matrixgames"* ]]; then
        ENV_CONFIG="gymma"
        DEFAULT_ARGS+=("env_args.time_limit=25")
    elif [[ "$ENV_KEY" == *"lbforaging"* ]]; then
        ENV_CONFIG="gymma"
        DEFAULT_ARGS+=("env_args.time_limit=50")
    elif [[ "$ENV_KEY" == *"rware"* ]]; then
        ENV_CONFIG="gymma"
        DEFAULT_ARGS+=("env_args.time_limit=500")
    elif [[ "$ENV_KEY" == *"pz-mpe"* ]]; then
        ENV_CONFIG="gymma"
        DEFAULT_ARGS+=("env_args.time_limit=25")
    elif [[ "$ENV_KEY" == "sc2" ]]; then
        ENV_CONFIG="sc2"
        DEFAULT_ARGS+=("env_args.map_name=3m")
    else
        ENV_CONFIG="gymma"
    fi
    
    # W&B 실행 스크립트 사용
    EXP_FLAGS=()
    if [ -n "$EXP_CONFIG" ]; then
        EXP_FLAGS+=("--exp-config" "$EXP_CONFIG")
    fi

    if [[ "$ENV_KEY" == "sc2" ]]; then
        python "$PROJECT_ROOT/scripts/run_with_wandb.py" \
            --config="$ALGORITHM" \
            --env-config="$ENV_CONFIG" \
            --wandb-config="$WANDB_CONFIG" \
            "${EXP_FLAGS[@]}" \
            seed=$SEED \
            "${DEFAULT_ARGS[@]}" \
            "${ADDITIONAL_ARGS[@]}" &
    else
        python "$PROJECT_ROOT/scripts/run_with_wandb.py" \
            --config="$ALGORITHM" \
            --env-config="$ENV_CONFIG" \
            --wandb-config="$WANDB_CONFIG" \
            "${EXP_FLAGS[@]}" \
            env_args.key="$ENV_KEY" \
            seed=$SEED \
            "${DEFAULT_ARGS[@]}" \
            "${ADDITIONAL_ARGS[@]}" &
    fi

    JOB_PIDS+=("$!")

    while [ ${#JOB_PIDS[@]} -ge $MAX_WORKERS ]; do
        wait "${JOB_PIDS[0]}"
        EXIT_CODE=$?
        JOB_PIDS=("${JOB_PIDS[@]:1}")
        if [ $EXIT_CODE -ne 0 ]; then
            echo "경고: 일부 실험이 비정상 종료되었습니다 (exit code $EXIT_CODE)."
            FAILURE_DETECTED=1
        fi
    done

    if [ "$MAX_WORKERS" -eq 1 ]; then
        sleep 2
    fi
    echo ""
done

for PID in "${JOB_PIDS[@]}"; do
    wait "$PID"
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "경고: 일부 실험이 비정상 종료되었습니다 (exit code $EXIT_CODE)."
        FAILURE_DETECTED=1
    fi
done

trap - INT TERM

if [ $FAILURE_DETECTED -eq 0 ]; then
    echo "=== 모든 시드 실험 완료 ==="
else
    echo "=== 실험 종료 (일부 실패 감지) ==="
fi
echo "결과는 results/ 디렉토리와 W&B에서 확인할 수 있습니다."
