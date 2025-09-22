#!/bin/bash
"""
원격 서버 환경 설정 스크립트
W&B API 키와 환경 변수를 설정합니다.

사용법:
  source configs/server/setup.sh
  
또는 .bashrc나 .zshrc에 추가:
  echo "source ~/marl-lab/configs/server/setup.sh" >> ~/.bashrc
"""

# ------------------------------------------------
# W&B 설정
# ------------------------------------------------
export WANDB_DIR="${HOME}/mingukang/wandb_config"
export WANDB_CONFIG_DIR="${HOME}/mingukang/wandb_config"
export WANDB_CACHE_DIR="${HOME}/mingukang/wandb_config/cache"

# 디렉토리 생성
mkdir -p "$WANDB_DIR" "$WANDB_CONFIG_DIR" "$WANDB_CACHE_DIR"

# API Key 파일이 있으면 로그인
if [ -f "$WANDB_CONFIG_DIR/api_key.txt" ]; then
    export WANDB_API_KEY="$(cat "$WANDB_CONFIG_DIR/api_key.txt")"
    echo "W&B API Key 로드됨"
    # 자동 로그인 (선택사항)
    # wandb login --relogin "$WANDB_API_KEY" 2>/dev/null
else
    echo "W&B API Key 파일이 없습니다: $WANDB_CONFIG_DIR/api_key.txt"
    echo "다음 명령어로 API Key를 저장하세요:"
    echo "  echo 'your_api_key_here' > $WANDB_CONFIG_DIR/api_key.txt"
    echo "  chmod 600 $WANDB_CONFIG_DIR/api_key.txt"
fi

# Entity / Project 지정
export WANDB_ENTITY="tatalintelli-university-of-seoul"
export WANDB_PROJECT="marl-lab"  # 기본 프로젝트명

# ------------------------------------------------
# EPyMARL 환경 설정
# ------------------------------------------------

# CUDA 설정 (필요시)
export CUDA_VISIBLE_DEVICES="0"  # 원하는 GPU 번호로 변경

# StarCraft II 설정 (SMAC/SMAC2 사용시)
export SC2PATH="${HOME}/StarCraftII"

# Python 경로 (가상환경 사용시)
# export PYTHONPATH="${HOME}/miniconda3/envs/marl/bin/python"

# ------------------------------------------------
# 프로젝트 설정
# ------------------------------------------------

# 프로젝트 루트 디렉토리
export MARL_LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# 결과 저장 디렉토리
export RESULTS_DIR="${MARL_LAB_ROOT}/results"
mkdir -p "$RESULTS_DIR"

echo "=================================="
echo "MARL Lab 서버 환경 설정 완료"
echo "W&B Entity: $WANDB_ENTITY"
echo "W&B Dir: $WANDB_DIR"
echo "Project Root: $MARL_LAB_ROOT"
echo "Results Dir: $RESULTS_DIR"
echo "=================================="
