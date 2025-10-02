#!/bin/bash
# 멀티 시드 실험 실행 스크립트 (PyMARL2 & MARLlib)
#
# 예시
#   RUN_MULTI_SEED_WORKERS=2 ./bin/run_multi_seed.sh pymarl2 qmix sc2 5 --map 3s5z --with t_max=3000000
#   ./bin/run_multi_seed.sh pymarl2 qmix sc2v2 3 --map protoss_5_vs_5 --wandb smac2
#   ./bin/run_multi_seed.sh marllib mappo mpe 4 --map simple_tag --timesteps 2000000 --num-workers 8
#   ./bin/run_multi_seed.sh marllib mappo overcooked 2 --map cramped_room --num-gpus 1 --local-mode

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: run_multi_seed.sh <framework> <algorithm> <environment> <num_seeds> [options]
  framework : pymarl2 | marllib
  algorithm : 학습 알고리즘 이름 (예: qmix, mappo)
  environment : 프레임워크별 환경 키 (예: sc2, sc2v2, mpe, overcooked)
  num_seeds  : 실행할 시드 개수 (양의 정수)

Common options:
  --workers <int>       동시에 실행할 실험 수 (기본 RUN_MULTI_SEED_WORKERS 또는 1)
  --start-seed <int>    시작 시드 값 (기본 1000)
  --timesteps <int>     PyMARL2 t_max 또는 MARLlib 학습 스텝

PyMARL2 전용 옵션:
  --wandb <name>        W&B 프리셋 이름 (기본 default)
  --env-config <name>   PyMARL2 환경 설정 이름 (기본 sc2)
  --map <name>          SMAC/SMACv2 맵 이름 (env_args.map_name)
  --with <key=value>    추가 with 인자 (필요시 반복)
  --exp-config <name>   configs/exp/ 템플릿 이름

MARLlib 전용 옵션:
  --map <name>          PettingZoo/Overcooked 레이아웃 (필수)
  --share-policy <mode> 정책 공유 방식 (all/group/individual)
  --num-workers <int>   Ray rollout worker 수 (기본 4)
  --num-gpus <int>      사용 GPU 수 (기본 0)
  --local-dir <path>    결과 저장 경로 (기본 results/marllib)
  --checkpoint-freq <n> 체크포인트 주기 (training_iteration)
  --stop-reward <val>   목표 평균 리워드
  --core-arch <arch>    모델 구조 (예: mlp, rnn)
  --encode-layer <spec> 인코더 레이어 (예: 128-256)
  --local-mode          Ray local mode (디버그용)
  --force-coop          환경을 강제로 공통 보상으로 설정
EOF
}

if [ $# -lt 4 ]; then
    usage
    exit 1
fi

FRAMEWORK=$1
ALGORITHM=$2
TARGET_ENV=$3
NUM_SEEDS=$4
shift 4

case "$FRAMEWORK" in
    pymarl2|marllib) ;;
    *) echo "지원하지 않는 프레임워크: $FRAMEWORK" >&2; exit 1;;
 esac

if ! [[ $NUM_SEEDS =~ ^[0-9]+$ ]] || [ "$NUM_SEEDS" -le 0 ]; then
    echo "num_seeds 값이 잘못되었습니다: $NUM_SEEDS" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

SETUP_SCRIPT="$PROJECT_ROOT/configs/server/setup.sh"
if [ -f "$SETUP_SCRIPT" ]; then
    # shellcheck disable=SC1090
    source "$SETUP_SCRIPT"
fi

if [ "$FRAMEWORK" = "pymarl2" ]; then
    PATCH_SCRIPT="$PROJECT_ROOT/scripts/apply_pymarl2_patches.sh"
    if [ -x "$PATCH_SCRIPT" ]; then
        "$PATCH_SCRIPT"
    fi
fi

MAX_WORKERS=${RUN_MULTI_SEED_WORKERS:-1}
START_SEED=1000

WANDB_CONFIG="default"
ENV_CONFIG="sc2"
MAP_NAME=""
WITH_ARGS=()
EXP_CONFIG=""

SHARE_POLICY="group"
NUM_WORKERS=4
NUM_GPUS=0
LOCAL_DIR_MARL=""
LOCAL_MODE=0
FORCE_COOP=0
CHECKPOINT_FREQ=""
STOP_REWARD=""
CORE_ARCH=""
ENCODE_LAYER=""
TIMESTEPS=""

REMAINDER=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --workers) MAX_WORKERS=$2; shift 2;;
        --start-seed) START_SEED=$2; shift 2;;
        --timesteps) TIMESTEPS=$2; shift 2;;
        --wandb) WANDB_CONFIG=$2; shift 2;;
        --env-config) ENV_CONFIG=$2; shift 2;;
        --map) MAP_NAME=$2; shift 2;;
        --with) WITH_ARGS+=("$2"); shift 2;;
        --exp-config) EXP_CONFIG=$2; shift 2;;
        --share-policy) SHARE_POLICY=$2; shift 2;;
        --num-workers) NUM_WORKERS=$2; shift 2;;
        --num-gpus) NUM_GPUS=$2; shift 2;;
        --local-dir) LOCAL_DIR_MARL=$2; shift 2;;
        --checkpoint-freq) CHECKPOINT_FREQ=$2; shift 2;;
        --stop-reward) STOP_REWARD=$2; shift 2;;
        --core-arch) CORE_ARCH=$2; shift 2;;
        --encode-layer) ENCODE_LAYER=$2; shift 2;;
        --local-mode) LOCAL_MODE=1; shift 1;;
        --force-coop) FORCE_COOP=1; shift 1;;
        --) shift; REMAINDER=("$@") ; break;;
        *) REMAINDER+=("$1"); shift;;
    esac
done

if ! [[ $MAX_WORKERS =~ ^[0-9]+$ ]] || [ "$MAX_WORKERS" -lt 1 ]; then
    MAX_WORKERS=1
fi
if ! [[ $START_SEED =~ ^[0-9]+$ ]]; then
    START_SEED=1000
fi

if [ "$FRAMEWORK" = "marllib" ] && [ -z "$MAP_NAME" ]; then
    echo "MARLlib 실행에는 --map 옵션이 필요합니다." >&2
    exit 1
fi

JOB_PIDS=()
FAILURE=0

cleanup() {
    if [ ${#JOB_PIDS[@]} -gt 0 ]; then
        kill "${JOB_PIDS[@]}" 2>/dev/null || true
    fi
}
trap cleanup INT TERM

launch_command() {
    local cmd=("$@")
    echo "[seed $CURRENT_SEED] ${cmd[*]}"
    "${cmd[@]}" &
    JOB_PIDS+=("$!")
}

run_pymarl2() {
    local with_list=("${WITH_ARGS[@]}" "seed=$CURRENT_SEED")
    if [[ -n "$MAP_NAME" && "$ENV_CONFIG" == sc2* ]]; then
        with_list+=("env_args.map_name=$MAP_NAME")
    fi
    if [[ -n "$TIMESTEPS" ]]; then
        with_list+=("t_max=$TIMESTEPS")
    fi
    if [[ ${#REMAINDER[@]} -gt 0 ]]; then
        with_list+=("${REMAINDER[@]}")
    fi

    local cmd=(python "$PROJECT_ROOT/scripts/run_with_wandb.py"
        --config="$ALGORITHM"
        --env-config="$ENV_CONFIG"
        --wandb-config="$WANDB_CONFIG")
    if [ -n "$EXP_CONFIG" ]; then
        cmd+=(--exp-config "$EXP_CONFIG")
    fi
    if [[ ${#with_list[@]} -gt 0 ]]; then
        cmd+=(with)
        cmd+=("${with_list[@]}")
    fi
    launch_command "${cmd[@]}"
}

run_marllib() {
    local cmd=(python "$PROJECT_ROOT/scripts/run_marllib.py"
        --env="$TARGET_ENV"
        --map="$MAP_NAME"
        --algo="$ALGORITHM"
        --seed="$CURRENT_SEED"
        --share-policy="$SHARE_POLICY"
        --num-workers="$NUM_WORKERS"
        --num-gpus="$NUM_GPUS"
        --wandb-config="$WANDB_CONFIG")
    if [[ -n "$TIMESTEPS" ]]; then cmd+=(--timesteps "$TIMESTEPS"); fi
    if [[ -n "$STOP_REWARD" ]]; then cmd+=(--stop-reward "$STOP_REWARD"); fi
    if [[ -n "$LOCAL_DIR_MARL" ]]; then cmd+=(--local-dir "$LOCAL_DIR_MARL"); fi
    if [[ -n "$CHECKPOINT_FREQ" ]]; then cmd+=(--checkpoint-freq "$CHECKPOINT_FREQ"); fi
    if [[ "$LOCAL_MODE" -eq 1 ]]; then cmd+=(--local-mode); fi
    if [[ "$FORCE_COOP" -eq 1 ]]; then cmd+=(--force-coop); fi
    if [[ -n "$CORE_ARCH" ]]; then cmd+=(--core-arch "$CORE_ARCH"); fi
    if [[ -n "$ENCODE_LAYER" ]]; then cmd+=(--encode-layer "$ENCODE_LAYER"); fi
    if [[ ${#REMAINDER[@]} -gt 0 ]]; then cmd+=("${REMAINDER[@]}"); fi
    launch_command "${cmd[@]}"
}

echo "=== Multi-seed run ==="
echo "framework   : $FRAMEWORK"
echo "algorithm   : $ALGORITHM"
echo "environment : $TARGET_ENV"
echo "num_seeds   : $NUM_SEEDS (start_seed=$START_SEED)"
echo "max_workers : $MAX_WORKERS"
if [ "$FRAMEWORK" = "pymarl2" ]; then
    echo "wandb       : $WANDB_CONFIG"
    echo "env_config  : $ENV_CONFIG"
    echo "map         : ${MAP_NAME:-<default>}"
else
    echo "map         : $MAP_NAME"
    echo "share_policy: $SHARE_POLICY"
    echo "num_workers : $NUM_WORKERS"
    echo "num_gpus    : $NUM_GPUS"
    echo "wandb       : $WANDB_CONFIG"
fi
echo "========================"

for ((i=0; i<NUM_SEEDS; i++)); do
    CURRENT_SEED=$((START_SEED + i))
    if [ "$FRAMEWORK" = "pymarl2" ]; then
        run_pymarl2
    else
        run_marllib
    fi

    while [ ${#JOB_PIDS[@]} -ge "$MAX_WORKERS" ]; do
        wait "${JOB_PIDS[0]}"
        EXIT_CODE=$?
        JOB_PIDS=("${JOB_PIDS[@]:1}")
        if [ $EXIT_CODE -ne 0 ]; then
            FAILURE=1
        fi
    done

done

for pid in "${JOB_PIDS[@]}"; do
    if ! wait "$pid"; then
        FAILURE=1
    fi

done

trap - INT TERM

if [ $FAILURE -eq 0 ]; then
    echo "모든 시드 실험이 완료되었습니다."
else
    echo "일부 실험에서 오류가 발생했습니다." >&2
    exit 1
fi
