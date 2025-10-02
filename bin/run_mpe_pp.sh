#!/usr/bin/env bash
# Sequential MARLlib Predator-Prey (MPE) sweep with multiple algorithms and seeds.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SEEDS=2
WORKERS=2
TIMESTEPS=2000000
MPE_MAP="simple_tag"  # Predator-prey scenario in MPE
ALGORITHMS=(iql vdn ippo mappo)
WANDB_PRESET="default"

FAILURES=()

for algo in "${ALGORITHMS[@]}"; do
    echo "[MPE-PP] map=${MPE_MAP} algo=${algo} seeds=${SEEDS}"
    if ! "$PROJECT_ROOT/bin/run_multi_seed.sh" \
        marllib "$algo" mpe "$SEEDS" \
        --workers "$WORKERS" \
        --wandb "$WANDB_PRESET" \
        --map "$MPE_MAP" \
        --timesteps "$TIMESTEPS" \
        --num-gpus 0 \
        --num-workers 4; then
        echo "[MPE-PP][ERROR] Failed algo=${algo}" >&2
        FAILURES+=("${algo}")
    else
        echo "[MPE-PP] Completed algo=${algo}"
    fi
    sleep 5
done

if ((${#FAILURES[@]})); then
    echo "[MPE-PP][SUMMARY] ${#FAILURES[@]} jobs failed:" >&2
    for algo in "${FAILURES[@]}"; do
        echo "  - ${MPE_MAP}:${algo}" >&2
    done
    exit 1
fi

echo "[MPE-PP] All jobs completed successfully."
