# Scripts 디렉토리

이 디렉토리는 EPyMARL 기반 실험을 쉽게 실행하고 관리하기 위한 스크립트들을 포함합니다.

## 🛠 스크립트 목록

### 1. `run_with_wandb.py`
W&B 설정을 적용하여 EPyMARL 실험을 실행하는 기본 스크립트입니다.

```bash
python scripts/run_with_wandb.py --config=qmix --env-config=gymma --wandb-config=matrix_games env_args.key="matrixgames:penalty-100-nostate-v0"
```

### 2. `run_multi_seed.sh`
동일한 설정으로 여러 시드를 사용한 실험을 자동화합니다.

```bash
# Matrix Games 예시
./scripts/run_multi_seed.sh qmix "matrixgames:penalty-100-nostate-v0" 5 matrix_games

# LBF 개별 보상 예시  
./scripts/run_multi_seed.sh mappo "lbforaging:Foraging-8x8-2p-3f-v3" 3 foraging common_reward=False
```

### 3. `quick_experiment.sh`
알고리즘 개발 시 빠른 검증을 위한 짧은 실험 스크립트입니다.

```bash
# 지원하는 환경들
./scripts/quick_experiment.sh qmix matrix_penalty
./scripts/quick_experiment.sh mappo lbf_small common_reward=False
./scripts/quick_experiment.sh vdn rware_tiny
```

**지원하는 빠른 실험 환경:**
- `matrix_penalty`: Matrix Penalty Game (짧은 에피소드)
- `matrix_climbing`: Matrix Climbing Game
- `lbf_small`: 작은 LBF 환경 (8x8-2p-3f)
- `lbf_medium`: 중간 LBF 환경 (10x10-3p-3f)
- `rware_tiny`: 작은 RWARE 환경 (2 에이전트)
- `mpe_spread`: MPE Simple Spread

### 4. `algorithm_comparison.py`
여러 알고리즘의 성능을 체계적으로 비교하는 스크립트입니다.

```bash
# Matrix Games에서 QMIX 계열 알고리즘 비교
python scripts/algorithm_comparison.py --env matrix_penalty --algorithms qmix vdn qtran --seeds 3

# LBF에서 Policy Gradient 계열 알고리즘 비교 (개별 보상)
python scripts/algorithm_comparison.py --env lbf_small --algorithms mappo ippo maa2c --seeds 5 --individual-rewards

# 추가 옵션과 함께 실행
python scripts/algorithm_comparison.py --env rware_tiny --algorithms qmix mappo --seeds 3 --delay 10 --additional-args "use_tensorboard=True"
```

## 📋 사용 가이드라인

### 실험 워크플로우

1. **빠른 검증**: `quick_experiment.sh`로 알고리즘이 환경에서 정상 작동하는지 확인
2. **시드 다양화**: `run_multi_seed.sh`로 통계적 신뢰성 확보
3. **알고리즘 비교**: `algorithm_comparison.py`로 체계적인 성능 비교
4. **커스텀 실험**: `run_with_wandb.py`로 세밀한 설정 조정

### W&B 설정 연동

모든 스크립트는 `configs/wandb/` 디렉토리의 설정 파일을 자동으로 적용합니다:

- `default.yaml`: 기본 W&B 설정
- `matrix_games.yaml`: Matrix Games 전용 설정
- `foraging.yaml`: LBF 환경 전용 설정

### 환경별 권장 설정

#### Matrix Games
- 짧은 에피소드, 빠른 실험
- 공통 보상 환경
- 추천 알고리즘: QMIX, VDN, QTRAN, COMA

#### Level-Based Foraging (LBF)
- 개별 보상 권장
- 협력적 환경
- 추천 알고리즘: MAPPO, IPPO, MAA2C, PAC

#### Multi-Robot Warehouse (RWARE)
- 긴 에피소드
- 개별 또는 공통 보상 모두 지원
- 추천 알고리즘: QMIX, MAPPO

## 🔧 커스터마이제이션

### 새로운 환경 추가

1. `quick_experiment.sh`에 새 환경 케이스 추가
2. `algorithm_comparison.py`의 `ENVIRONMENTS` 딕셔너리에 설정 추가
3. 필요시 `configs/wandb/`에 전용 W&B 설정 파일 생성

### 스크립트 수정

모든 스크립트는 서브모듈을 수정하지 않고 상위 레벨에서 설정을 주입하는 방식으로 설계되었습니다. 새로운 기능이 필요한 경우 이 원칙을 유지해주세요.

## 🐛 문제 해결

### 일반적인 문제들

1. **Permission denied**: 스크립트 실행 권한 확인
   ```bash
   chmod +x scripts/*.sh scripts/*.py
   ```

2. **Python 경로 문제**: 가상환경 활성화 확인
   ```bash
   which python
   pip list | grep -E "(torch|sacred|wandb)"
   ```

3. **환경 등록 오류**: 환경별 라이브러리 설치 확인
   ```bash
   pip install -r external/epymarl/env_requirements.txt
   ```

4. **W&B 인증**: W&B 로그인 상태 확인
   ```bash
   wandb status
   ```

## 📊 결과 분석

실험 결과는 다음 위치에서 확인할 수 있습니다:

- **Sacred 로그**: `results/sacred/` (기본)
- **TensorBoard 로그**: `results/tb_logs/` (설정 시)
- **W&B 대시보드**: https://wandb.ai (온라인 동기화 시)
- **저장된 모델**: `results/models/` (모델 저장 설정 시)

### 결과 시각화

```bash
# EPyMARL 내장 플롯팅 스크립트 사용
python external/epymarl/plot_results.py --results_dir results/ --env_name "penalty"

# W&B 대시보드에서 실시간 모니터링
wandb sync results/wandb/  # 오프라인 로그 업로드 시
```