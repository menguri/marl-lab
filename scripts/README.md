# Scripts 디렉토리

EPyMARL 기반 실험을 쉽게 실행하고 관리하기 위한 스크립트들입니다.

## 🚀 새로운 통합 스크립트 (권장)

### `unified_experiment.py` - 통합 실험 실행 도구
모든 환경과 알고리즘을 중앙에서 관리하는 통합 인터페이스입니다.

**주요 특징:**
- ✅ 알고리즘-환경 호환성 자동 검증
- ✅ 30+개 환경 자동 설정 관리
- ✅ 개별/공통 보상 모드 지원
- ✅ 빠른 테스트 모드
- ✅ 다중 시드 실험 지원

```bash
# 환경 목록 확인
python scripts/unified_experiment.py --action list

# 특정 카테고리 환경 확인
python scripts/unified_experiment.py --action list --category smac1

# 알고리즘별 추천 환경 확인
python scripts/unified_experiment.py --action list --for-algorithm qmix

# 기본 실험 실행
python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty

# 개별 보상 환경 실험
python scripts/unified_experiment.py --algorithm mappo --environment lbf_small --individual-rewards

# 빠른 테스트 (짧은 학습)
python scripts/unified_experiment.py --algorithm qmix --environment smac_3s5z --quick

# 다중 시드 실험
python scripts/unified_experiment.py --algorithm mappo --environment lbf_medium --seeds 5
```

**지원하는 환경 카테고리:**
- `matrix`: Matrix Games (penalty, climbing)
- `lbf`: Level-Based Foraging 환경들
- `rware`: Multi-Robot Warehouse 환경들
- `mpe`: Multi-Agent Particle Environment들
- `smac1`: SMAC (StarCraft) 환경들
- `smac2`: SMACv2 환경들
- `vmas`: VMAS 환경들
- `quick`: 빠른 테스트용 추천 환경들
- `individual_rewards`: 개별 보상 지원 환경들

## 🔧 기존 스크립트들 (호환성)

> 🗂️ 실행 가능한 셸 스크립트는 `bin/` 디렉토리로 이동했습니다.

### `run_with_wandb.py` - W&B 설정 통합 스크립트
```bash
python scripts/run_with_wandb.py --config=qmix --env-config=gymma --wandb-config=matrix_games env_args.key="matrixgames:penalty-100-nostate-v0"
```

### `run_multi_seed.sh` (`bin/`) - 다중 시드 실험
```bash
./bin/run_multi_seed.sh qmix "matrixgames:penalty-100-nostate-v0" 5 matrix_games
./bin/run_multi_seed.sh mappo "lbforaging:Foraging-8x8-2p-3f-v3" 3 foraging common_reward=False

# 동시에 여러 시드를 돌리려면 환경 변수를 지정하세요.
RUN_MULTI_SEED_WORKERS=4 ./bin/run_multi_seed.sh ...
```

### `quick_experiment.sh` (`bin/`) - 빠른 실험
```bash
./bin/quick_experiment.sh qmix matrix_penalty
./bin/quick_experiment.sh mappo lbf_small common_reward=False
./bin/quick_experiment.sh qmix smac_3s5z
./bin/quick_experiment.sh vdn smac2_terran
```

### `algorithm_comparison.py` - 알고리즘 성능 비교
```bash
python scripts/algorithm_comparison.py --env matrix_penalty --algorithms qmix vdn qtran --seeds 3
python scripts/algorithm_comparison.py --env lbf_small --algorithms mappo ippo maa2c --seeds 5 --individual-rewards
```

### `server_run.sh` (`bin/`) - 서버 환경 실행
```bash
# 서버 설정 후
./bin/server_run.sh qmix smac_3s5z server_default
```

## 📊 지원하는 환경들 (총 30+개)

### Matrix Games (4개)
```
matrix_penalty        - Matrix Penalty Game (-100 penalty)
matrix_climbing       - Matrix Climbing Game  
matrix_penalty_25     - Matrix Penalty Game (-25 penalty)
matrix_penalty_50     - Matrix Penalty Game (-50 penalty)
```

### Level-Based Foraging (4개)
```
lbf_small            - Small LBF (8x8, 2 players, 3 food)
lbf_medium           - Medium LBF (10x10, 3 players, 3 food)
lbf_large            - Large LBF (15x15, 3 players, 5 food)
lbf_coop_small       - Cooperative LBF (8x8, 2 players, 2 food)
```

### Multi-Robot Warehouse (3개)
```
rware_tiny           - Tiny RWARE (2 agents)
rware_small          - Small RWARE (4 agents)  
rware_tiny_4ag       - Tiny RWARE (4 agents)
```

### Multi-Agent Particle Environment (4개)
```
mpe_spread           - MPE Simple Spread
mpe_speaker_listener - MPE Simple Speaker Listener
mpe_adversary        - MPE Simple Adversary
mpe_tag              - MPE Simple Tag
```

### SMAC (StarCraft Multi-Agent Challenge) (5개)
```
smac_3s5z            - SMAC 3 Stalkers & 5 Zealots
smac_2s_vs_1sc       - SMAC 2 Stalkers vs 1 Spine Crawler
smac_corridor        - SMAC Corridor
smac_MMM2            - SMAC Marines, Marauders & Medivacs 2
smac_3s_vs_5z        - SMAC 3 Stalkers vs 5 Zealots
```

### SMACv2 (4개)
```
smac2_terran         - SMACv2 Terran vs Terran (5v5)
smac2_protoss        - SMACv2 Protoss vs Protoss (5v5)
smac2_zerg           - SMACv2 Zerg vs Zerg (5v5)
smac2_terran_10v10   - SMACv2 Terran vs Terran (10v10)
```

### VMAS (2개)
```
vmas_balance         - VMAS Balance
vmas_transport       - VMAS Transport
```

## 🎯 알고리즘별 추천 환경

### 공통 보상 전용 알고리즘
```
qmix     → matrix_penalty, smac_3s5z, smac2_terran, mpe_spread
vdn      → matrix_penalty, matrix_climbing, smac_3s5z, mpe_spread
qtran    → matrix_penalty, smac_MMM2, smac2_protoss  
coma     → smac_3s5z, smac_corridor, matrix_climbing
```

### 개별 보상 지원 알고리즘
```
mappo    → lbf_small, lbf_medium, rware_tiny, vmas_balance
ippo     → lbf_small, rware_tiny, vmas_transport
maa2c    → lbf_medium, rware_small, mpe_spread
ia2c     → lbf_small, matrix_penalty, mpe_spread
iql      → matrix_penalty, lbf_small, rware_tiny
pac      → matrix_penalty, matrix_climbing, lbf_coop_small
maddpg   → mpe_spread, mpe_adversary, vmas_balance
```

## 🔄 마이그레이션 가이드

### 기존 → 통합 스크립트 변환

**기존 방식:**
```bash
python external/epymarl/src/main.py --config=qmix --env-config=gymma with env_args.time_limit=25 env_args.key="matrixgames:penalty-100-nostate-v0"
```

**새 방식:**
```bash
python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty
```

**기존 다중 시드:**
```bash
./bin/run_multi_seed.sh qmix "matrixgames:penalty-100-nostate-v0" 5 matrix_games
```

**새 방식:**
```bash
python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty --seeds 5
```

## 🐛 문제 해결

### 호환성 오류
```bash
python scripts/unified_experiment.py --algorithm qmix --environment lbf_small --individual-rewards
# ❌ 호환성 오류: 알고리즘 qmix는 개별 보상 모드를 지원하지 않습니다
```

**해결:** 개별 보상을 지원하는 알고리즘 사용 (mappo, ippo, maa2c 등)

### 환경을 찾을 수 없음
```bash
# 지원하는 환경 목록 확인
python scripts/unified_experiment.py --action list --category smac1
```

### 서버 설정 오류
```bash
# 서버 환경 설정 확인
source configs/server/setup.sh
echo $WANDB_ENTITY
```

## 📈 성능 최적화

### 빠른 테스트
```bash
# 짧은 학습으로 빠른 검증
python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty --quick
```

### 서버 최적화
```bash
# 서버 전용 설정으로 실행
python scripts/unified_experiment.py --algorithm qmix --environment smac_3s5z --wandb-config server_default
```

### 배치 실험
```bash
# 여러 알고리즘 순차 실행 (스크립트로 자동화)
for alg in qmix vdn qtran; do
    python scripts/unified_experiment.py --algorithm $alg --environment matrix_penalty --seeds 3
done
```

---

**권장사항:** 새로운 실험에는 `unified_experiment.py` 사용을 강력히 권장합니다. 기존 스크립트들은 호환성을 위해 유지되지만, 통합 스크립트가 더 안전하고 사용하기 쉽습니다.
