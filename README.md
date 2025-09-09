# MARL Lab - Multi-Agent Reinforcement Learning Laboratory

이 프로젝트는 EPyMARL을 서브모듈로 사용하여 멀티에이전트 강화학습 알고리즘을 개발하고 실험하기 위한 연구 환경입니다.

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

### 지원하는 환경
- **SMAC/SMACv2**: StarCraft Multi-Agent Challenge
- **SMAClite**: 경량화된 SMAC 버전
- **Matrix Games**: 행렬 게임 환경
- **LBF**: Level-Based Foraging
- **RWARE**: Multi-Robot Warehouse
- **MPE**: Multi-agent Particle Environment (PettingZoo)
- **VMAS**: Vectorized Multi-Agent Simulator

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
```bash
# QMIX로 Matrix Game 실험
python external/epymarl/src/main.py --config=qmix --env-config=gymma with env_args.time_limit=25 env_args.key="matrixgames:penalty-100-nostate-v0"

# MAPPO로 LBF 개별 보상 실험
python external/epymarl/src/main.py --config=mappo --env-config=gymma with env_args.time_limit=50 env_args.key="lbforaging:Foraging-8x8-2p-3f-v3" common_reward=False
```

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

설정 파일 예시는 아래 섹션에서 생성됩니다.

## 🛠 알고리즘 개발 및 실험

### 시드 다양화 실험
여러 시드로 실험을 실행하여 통계적 신뢰성을 확보할 수 있습니다:

```bash
# scripts/ 디렉토리의 스크립트 사용 (아래에서 생성 예정)
./scripts/run_multi_seed.sh qmix matrixgames:penalty-100-nostate-v0 5
```

### 하이퍼파라미터 탐색
```bash
# EPyMARL의 search.py 사용
python external/epymarl/search.py run --config=search.config.example.yaml --seeds 5 locally
```

### 결과 시각화
```bash
# EPyMARL의 plotting 스크립트 사용
python external/epymarl/plot_results.py --results_dir results/ --env_name "penalty"
```

## 📁 커스텀 설정 및 확장

### configs/ 디렉토리 활용
- `configs/algorithms/`: 새로운 알고리즘 설정
- `configs/environments/`: 커스텀 환경 설정
- `configs/wandb/`: W&B 프로젝트별 설정

### plugins/ 디렉토리 활용
- 새로운 환경 래퍼
- 커스텀 네트워크 아키텍처
- 실험 후처리 스크립트

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

이 프로젝트는 Apache License v2.0 하에 배포됩니다. EPyMARL 서브모듈도 동일한 라이선스를 따릅니다.

## 🤝 기여하기

1. 이슈를 통해 문제점이나 개선사항을 공유해주세요
2. 새로운 알고리즘이나 환경 추가 시 적절한 테스트와 문서화를 포함해주세요
3. 서브모듈 수정이 필요한 경우, 먼저 상위 레벨에서의 해결 방안을 검토해주세요

---

*이 README는 EPyMARL 서브모듈을 효과적으로 활용하여 MARL 연구를 수행하기 위한 가이드입니다.*
