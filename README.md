# MARL Lab - Multi-Agent Reinforcement Learning Laboratory

이 프로젝트는 EPyMARL을 서브모듈로 사용하여 멀티에이전트 강화학습 알고리즘을 개발하고 실험하기 위한 연구 환경이다.

## 📁 프로젝트 구조

```
marl-lab/
├── external/
│   └── epymarl/              # EPyMARL 서브모듈
├── configs/                  # 커스텀 설정 파일들
├── scripts/                  # 실험 실행 스크립트
├── plugins/                  # 커스텀 플러그인/확장
├── ci/                      # CI/CD 설정
└── README.md
```

## 🔬 EPyMARL 구조 이해

EPyMARL은 PyMARL의 확장 버전으로, 다음과 같은 구조를 가집니다:

### 핵심 디렉토리 구조
```
external/epymarl/src/
├── components/              # 재사용 가능한 컴포넌트
│   ├── action_selectors.py  # 액션 선택 전략 (ε-greedy 등)
│   ├── episode_buffer.py    # 에피소드 데이터 버퍼
│   ├── epsilon_schedules.py # ε 스케줄링
│   └── transforms.py        # 데이터 변환 유틸리티
├── controllers/             # 에이전트 컨트롤러
│   ├── basic_controller.py  # 기본 컨트롤러
│   ├── maddpg_controller.py # MADDPG용 컨트롤러
│   └── non_shared_controller.py # 파라미터 비공유 컨트롤러
├── learners/               # 학습 알고리즘 구현
├── modules/                # 신경망 모듈
│   ├── agents/             # 에이전트 네트워크
│   ├── critics/            # 크리틱 네트워크
│   └── mixers/             # 믹싱 네트워크 (QMIX 등)
├── runners/                # 실험 러너
├── envs/                   # 환경 래퍼들
└── config/                 # 설정 파일들
    ├── algs/               # 알고리즘별 설정
    └── envs/               # 환경별 설정
```

### 지원하는 알고리즘

#### 공통 보상 환경 지원 알고리즘
- **QMIX**: Q-value mixing을 통한 중앙집중식 학습, 분산실행
- **VDN**: Value Decomposition Networks
- **COMA**: Counterfactual Multi-Agent Policy Gradients
- **QTRAN**: Q-Transformation

#### 개별 보상 환경 지원 알고리즘
- **IA2C**: Independent Advantage Actor-Critic
- **IPPO**: Independent Proximal Policy Optimization
- **MAA2C**: Multi-Agent Advantage Actor-Critic  
- **MAPPO**: Multi-Agent Proximal Policy Optimization
- **IQL**: Independent Q-Learning
- **PAC**: Pareto Actor-Critic
- **MADDPG**: Multi-Agent Deep Deterministic Policy Gradient

### 지원하는 환경 (총 30+개)

#### 🎮 Matrix Games (4개)
- **Matrix Penalty Games**: 다양한 페널티 수준 (-25, -50, -100)
- **Matrix Climbing Game**: 협력 게임

#### 🍎 Level-Based Foraging (4개)
- **LBF Small/Medium/Large**: 다양한 크기의 foraging 환경
- **Cooperative LBF**: 협력 필수 버전

#### 📦 Multi-Robot Warehouse (3개)
- **RWARE Tiny/Small**: 2-4 에이전트 창고 환경

#### 🎯 Multi-Agent Particle Environment (4개)
- **MPE Spread/Speaker-Listener/Adversary/Tag**: 다양한 협력/경쟁 환경

#### ⚔️ SMAC (StarCraft Multi-Agent Challenge) (5개)
- **Classic SMAC Maps**: 3s5z, 2s_vs_1sc, corridor, MMM2, 3s_vs_5z

#### 🚀 SMACv2 (4개)
- **Race-based Battles**: Terran/Protoss/Zerg 5v5 및 10v10

#### 🤖 VMAS (2개)
- **Vectorized Multi-Agent**: Balance, Transport 환경

## 🚀 빠른 시작

### 1. 저장소 클론 및 초기화
```bash
git clone --recursive [your-repo-url]
cd marl-lab

# 서브모듈이 초기화되지 않은 경우
git submodule update --init --recursive
```

### 2. 환경 설정
```bash
# EPyMARL 의존성 설치
pip install -r external/epymarl/requirements.txt

# 환경 패키지 설치 (선택사항)
pip install -r external/epymarl/env_requirements.txt

# PAC 알고리즘 의존성 (필요시)
pip install -r external/epymarl/pac_requirements.txt
```

### 3. 기본 실험 실행

#### 🚀 새로운 통합 스크립트 (권장)
```bash
# 환경 목록 확인
python scripts/unified_experiment.py --action list

# 알고리즘별 추천 환경 확인
python scripts/unified_experiment.py --action list --for-algorithm qmix

# 기본 실험 실행
python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty

# 개별 보상 환경에서 실험
python scripts/unified_experiment.py --algorithm mappo --environment lbf_small --individual-rewards

# 빠른 테스트 (짧은 학습)
python scripts/unified_experiment.py --algorithm qmix --environment smac_3s5z --quick

# 다중 시드 실험
python scripts/unified_experiment.py --algorithm mappo --environment lbf_medium --seeds 5
```

#### 🔧 기존 방식 (호환성)
```bash
# 직접 EPyMARL 실행
python external/epymarl/src/main.py --config=qmix --env-config=gymma with env_args.time_limit=25 env_args.key="matrixgames:penalty-100-nostate-v0"

# W&B 설정 스크립트 사용
python scripts/run_with_wandb.py --config=mappo --env-config=gymma --wandb-config=foraging env_args.key="lbforaging:Foraging-8x8-2p-3f-v3" common_reward=False
```

### 4. 서브모듈 패치 적용

EPyMARL 서브모듈은 그대로 두고, 필요한 수정만 패치 형태로 보관합니다. 저장소 루트의 `patches/epymarl/` 아래에 패치 파일이 있으며, 아래 스크립트로 적용할 수 있습니다.

```bash
# 서브모듈 초기화 후 한 번 실행 (git pull, submodule update 이후 반복 권장)
./scripts/apply_epymarl_patches.sh
```

스크립트는 각 패치를 적용하기 전에 `git apply --check`로 검증하고, 이미 적용된 경우 자동으로 건너뜁니다. 충돌이 발생하면 패치 내용을 최신 버전에 맞게 갱신한 뒤 다시 실행해주세요.

## 🧩 커스텀 확장 설계 가이드

향후 자체 알고리즘이나 환경 래퍼를 추가할 때는 아래 절차를 따른다. 서브모듈(`external/epymarl`)은 수정하지 않고, 상위 저장소에서만 변경이 일어나도록 유지한다.

- **코드 배치**: `plugins/` 하위에 새 패키지를 만들고 모듈을 배치한다. 예) learner → `plugins/algos/<알고리즘>/learner.py`, 환경 래퍼 → `plugins/custom_envs/<환경>/wrapper.py`.
- **레지스트리 등록**: `plugins/registry.py`의 `register_plugins()` 함수 안에서 모듈을 import 해 `LEARNERS[...]`, `MACS[...]`, `ENVS[...]`에 키를 추가한다. 이 단계가 있어야 EPyMARL이 커스텀 클래스를 인식한다.
- **환경 메타데이터 갱신**: 새 환경 키를 노출하려면 `configs/python/environments.py`에 `EnvironmentConfig` 항목을 추가해 설명, 기본 인자, 권장 알고리즘을 정의한다. `scripts/unified_experiment.py`와 CLI 도구들은 이 테이블을 참조한다.
- **W&B 프리셋 추가**: 로깅 설정이 기존과 다르면 `configs/wandb/`에 새로운 YAML을 만들고, 실행 시 `--wandb-config=<이름>` 옵션으로 선택한다.
- **실행 스크립트 연동**: `bin/run_multi_seed.sh`, `bin/server_run.sh`, `bin/quick_experiment.sh`는 모두 `scripts/run_with_wandb.py`를 통해 실행된다. 커스텀 알고리즘을 기본 옵션에 노출하려면 해당 스크립트에 분기를 추가하거나 README 예시 커맨드를 갱신한다.
- **스모크 테스트**: `scripts/run_once.py`는 레지스트리가 정상 동작하는지 확인하는 최소 실행 스크립트이다. 새 알고리즘 이름과 간단한 `with` 인자를 넣어 단일 실험이 성공하는지 점검한다.

> 참고: 커스텀 코드를 작성하기 전에는 `plugins/` 디렉토리가 비어 있어도 무방하다. 새 패키지를 만들 때는 `__init__.py`를 추가해 Python이 패키지로 인식하도록 한다.

### YAML 기반 실험 템플릿

`configs/exp/` 디렉토리에 실험용 YAML을 만들어 두면, 스크립트를 실행할 때 `exp_config=<이름>`으로 호출하여 하이퍼파라미터를 일괄 적용할 수 있다.

```yaml
# configs/exp/smac_qmix_rnn.yaml 예시
algo: qmix
env_config: sc2
wandb_config: smac1
with:
  env_args.map_name: "3s5z"
  use_rnn: true
  obs_last_action: true
```

```bash
# 단일 실행
python scripts/run_with_wandb.py --exp-config=smac_qmix_rnn

# 멀티 시드 실행
RUN_MULTI_SEED_WORKERS=4 ./bin/run_multi_seed.sh qmix sc2 5 smac1 exp_config=smac_qmix_rnn
```

YAML 파일의 `with` 블록은 EPyMARL의 `with` 인자로 변환되며, CLI에서 넘긴 인자가 있으면 YAML 값을 덮어씁니다. 덕분에 `use_rnn`/`obs_last_action`처럼 토글이 필요한 옵션을 쉽게 전환할 수 있다.

## 📊 Weights & Biases (W&B) 통합

### W&B 설정 (서브모듈 수정 없이)

1. **W&B 라이브러리 설치 및 인증**
```bash
pip install wandb
wandb login
```

2. **커스텀 W&B 설정 파일 생성**
```bash
# configs/wandb_config.yaml 파일을 생성하여 프로젝트별 설정 관리
mkdir -p configs
```

설정 파일 예시는 아래 섹션에 정리했다.

## 🛠 알고리즘 개발 및 실험

### 🔬 고급 실험 기능

#### 시드 다양화 실험

**📋 VDN + SMAC 3m 환경 실험 (추천)**
```bash
# VDN 알고리즘으로 SMAC 3m 환경에서 5개 시드 실험 (W&B 로깅 포함)
./bin/run_multi_seed.sh vdn sc2 5 smac1

# 다른 SMAC 맵 사용시 (8m, 2s3z 등)
./bin/run_multi_seed.sh vdn sc2 5 smac1 env_args.map_name=8m
./bin/run_multi_seed.sh vdn sc2 5 smac1 env_args.map_name=2s3z
```

**🔧 다른 환경 실험**
```bash
# 통합 스크립트 사용 (권장)
python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty --seeds 5

# Matrix Games
./bin/run_multi_seed.sh qmix "matrixgames:penalty-100-nostate-v0" 5 matrix_games

# Level-based Foraging
./bin/run_multi_seed.sh mappo "lbforaging:Foraging-8x8-2p-3f-v3" 5 foraging common_reward=False
```

#### 알고리즘 성능 비교
```bash
# 통합 스크립트로 여러 알고리즘 비교 실험 계획
python scripts/unified_experiment.py --action list --for-algorithm qmix  # 추천 환경 확인
python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty --seeds 3
python scripts/unified_experiment.py --algorithm vdn --environment matrix_penalty --seeds 3

# 기존 비교 스크립트
python scripts/algorithm_comparison.py --env matrix_penalty --algorithms qmix vdn qtran --seeds 3
```

#### 호환성 검증
```bash
# 알고리즘-환경 호환성 자동 검증
python scripts/unified_experiment.py --algorithm qmix --environment lbf_small --individual-rewards
# ❌ 호환성 오류: 알고리즘 qmix는 개별 보상 모드를 지원하지 않습니다

python scripts/unified_experiment.py --algorithm mappo --environment lbf_small --individual-rewards
# ✅ 호환성 검증 통과
```

#### 하이퍼파라미터 탐색
```bash
# EPyMARL의 search.py 사용
python external/epymarl/search.py run --config=search.config.example.yaml --seeds 5 locally
```

#### 결과 시각화
```bash
# EPyMARL의 plotting 스크립트 사용
python external/epymarl/plot_results.py --results_dir results/ --env_name "penalty"
```

## 📁 커스텀 설정 및 확장

### configs/ 디렉토리 활용
- `configs/python/`: 환경 레지스트리 및 추천 정보
- `configs/exp/`: 실험용 YAML 템플릿
- `configs/wandb/`: W&B 프로젝트별 설정
- `configs/server/`: 서버 공용 환경 변수 스크립트

### plugins/ 디렉토리 활용
- 추후 작성할 커스텀 learner/controller/env 래퍼
- EPyMARL 레지스트리에 연결될 보조 유틸리티
- 테스트용 스모크 스크립트 및 어댑터

## 🔧 개발 가이드라인

### 서브모듈 관리 원칙
- **EPyMARL 서브모듈은 직접 수정하지 않습니다**
- 모든 커스터마이제이션은 상위 디렉토리에서 관리
- 설정 파일과 스크립트를 통한 확장

### 브랜치 전략
- `master`: 안정적인 실험 환경
- `experiment/*`: 특정 실험을 위한 브랜치
- `feature/*`: 새로운 기능 개발

## 📚 참고 자료

- [EPyMARL 공식 문서](https://github.com/uoe-agents/epymarl)
- [PyMARL 원본 저장소](https://github.com/oxwhirl/pymarl)
- [SMAC 환경](https://github.com/oxwhirl/smac)
- [W&B 문서](https://docs.wandb.ai/)

## 📜 라이선스

이 프로젝트는 Apache License v2.0 하에 배포된다. EPyMARL 서브모듈도 동일한 라이선스를 따른다.

## 🤝 기여하기

1. 이슈를 통해 문제점이나 개선사항을 공유해라
2. 새로운 알고리즘이나 환경 추가 시 적절한 테스트와 문서화를 포함해라
3. 서브모듈 수정이 필요한 경우, 먼저 상위 레벨에서의 해결 방안을 검토해라

---

*이 README는 EPyMARL 서브모듈을 효과적으로 활용하여 MARL 연구를 수행하기 위한 가이드이다.*
