#!/usr/bin/env bash
# Sequential launcher for SMAC and SMACv2 sweeps.
# Runs IQL/VDN/QMIX/QPLEX/QTRAN on listed maps with 2 seeds each.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SEEDS=2
WORKERS=2
SC2_TMAX=2000000
SC2V2_TMAX=2000000

SC2_ALGOS=(iql vdn qmix qplex qtran)
SC2_MAPS=(3s5z 3s_vs_5z bane_vs_bane)

SC2V2_ALGOS=("${SC2_ALGOS[@]}")
SC2V2_MAPS=(2s3z 5m_vs_6m 6h_vs_8z)

run_smac_block() {
    local env_name=$1
    local wandb_preset=$2
    local tmax=$3
    local env_config_value=$4
    shift 4
    local -n algo_list=$1
    local -n map_list=$2

    local env_extra=()
    if [[ -n "$env_config_value" ]]; then
        env_extra=(--env-config "$env_config_value")
    fi

    for map in "${map_list[@]}"; do
        for algo in "${algo_list[@]}"; do
            echo "[SMAC] env=${env_name} env_config=${env_config_value:-$env_name} map=${map} algo=${algo} seeds=${SEEDS}"
            if ! "$PROJECT_ROOT/bin/run_multi_seed.sh" \
                pymarl2 "$algo" "$env_name" "$SEEDS" \
                --workers "$WORKERS" \
                --wandb "$wandb_preset" \
                "${env_extra[@]}" \
                --map "$map" \
                --with "t_max=${tmax}"; then
                echo "[SMAC][ERROR] Failed env=${env_name} map=${map} algo=${algo}" >&2
                FAILURES+=("${env_name}:${map}:${algo}")
            fi
        done
    done
}

FAILURES=()
run_smac_block sc2 smac1 "$SC2_TMAX" "" SC2_ALGOS SC2_MAPS
run_smac_block sc2 smac2 "$SC2V2_TMAX" "sc2v2" SC2V2_ALGOS SC2V2_MAPS

if ((${#FAILURES[@]})); then
    echo "[SMAC][SUMMARY] ${#FAILURES[@]} jobs failed:" >&2
    for item in "${FAILURES[@]}"; do
        echo "  - $item" >&2
    done
    exit 1
fi

echo "[SMAC] All jobs completed successfully."
