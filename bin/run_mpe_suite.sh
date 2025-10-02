#!/usr/bin/env bash
# Sequential launcher for MPE Predator-Prey sweeps.
# Runs specified algorithms on easy, medium, and hard maps with 2 seeds each.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SEEDS=2
WORKERS=2
WANDB_PRESET="mpe" # MPE 전용 W&B 설정 사용

ALGORITHMS=(iql vdn qmix ippo mappo maddpg)

# MPE Predator-Prey maps with varying difficulty
MPE_MAPS=(simple_tag simple_adversary)

run_mpe_block() {
    local -n map_list=$1
    local -n algo_list=$2

    for map in "${map_list[@]}"; do
        for algo in "${algo_list[@]}"; do
            echo "[MPE] map=${map} algo=${algo} seeds=${SEEDS}"
            if ! "$PROJECT_ROOT/bin/run_multi_seed.sh" \
                marllib "$algo" mpe "$SEEDS" \
                --workers "$WORKERS" \
                --wandb "$WANDB_PRESET" \
                --map "$map" \
                --num-gpus 0 \
                --num-workers 4; then
                echo "[MPE][ERROR] Failed map=${map} algo=${algo}" >&2
                FAILURES+=("${map}:${algo}")
            fi
        done
    done
}

FAILURES=()
run_mpe_block MPE_MAPS ALGORITHMS

if ((${#FAILURES[@]})); then
    echo "[MPE][SUMMARY] ${#FAILURES[@]} jobs failed:" >&2
    for item in "${FAILURES[@]}"; do
        echo "  - $item" >&2
    done
    exit 1
fi

echo "[MPE] All jobs completed successfully."