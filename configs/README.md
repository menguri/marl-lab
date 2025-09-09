# Configs 디렉토리

이 디렉토리는 EPyMARL 실험과 서버 환경 설정을 관리합니다.

## 📁 디렉토리 구조

```
configs/
├── wandb/                    # W&B 설정 파일들
│   ├── default.yaml         # 기본 W&B 설정
│   ├── server_default.yaml  # 서버용 기본 설정
│   ├── matrix_games.yaml    # Matrix Games 전용
│   ├── foraging.yaml        # LBF 환경 전용
│   └── smac2.yaml          # SMACv2 환경 전용
├── server_setup.sh          # 서버 환경 변수 설정
└── README.md               # 이 파일
```

## 🔧 W&B 설정 파일들

### `default.yaml`
로컬 개발 환경용 기본 W&B 설정입니다.

```yaml
use_wandb: True
wandb_mode: "offline"
wandb_team: null          # 여기에 팀명 입력
wandb_project: "marl-lab" # 여기에 프로젝트명 입력
```

### `server_default.yaml`
원격 서버용 최적화된 W&B 설정입니다.

```yaml
use_wandb: True
wandb_mode: "online"      # 서버에서는 온라인 모드
buffer_cpu_only: True     # GPU 메모리 절약
log_interval: 5000        # 서버 최적화
```

### 환경별 전용 설정
- `matrix_games.yaml`: Matrix Games 환경용
- `foraging.yaml`: Level-Based Foraging 환경용  
- `smac2.yaml`: SMACv2 환경용

각 파일은 해당 환경에 최적화된 설정을 포함합니다.

## 🖥️ 서버 설정

### `server_setup.sh`
원격 서버 환경 변수를 설정하는 스크립트입니다.

**주요 설정:**
- W&B 디렉토리 설정
- API 키 자동 로드
- CUDA 환경 설정
- StarCraft II 경로 설정

**사용법:**
```bash
# 1. 서버에 로그인 후
source configs/server_setup.sh

# 2. 또는 .bashrc에 추가
echo "source ~/marl-lab/configs/server_setup.sh" >> ~/.bashrc
```

### W&B API 키 설정

**1단계: API 키 저장**
```bash
# W&B 사이트에서 API 키 복사 후
echo 'your_api_key_here' > ~/wandb_config/api_key.txt
chmod 600 ~/wandb_config/api_key.txt
```

**2단계: 환경 변수 확인**
```bash
source configs/server_setup.sh
echo $WANDB_ENTITY    # tatalintelli-university-of-seoul
echo $WANDB_PROJECT   # marl-lab
```

## 🚀 사용 예시

### SMAC2 실험
```bash
# 로컬에서
./scripts/quick_experiment.sh qmix smac2_terran

# 서버에서
./scripts/server_run.sh qmix smac2_terran server_default
```

### 커스텀 환경 키
```bash
# 직접 환경 키 지정
python scripts/run_with_wandb.py \
    --config=qmix \
    --env-config=sc2v2 \
    --wandb-config=smac2 \
    env_args.map_name="protoss_10_vs_10"
```

### 서버에서 다중 시드 실험
```bash
# 서버 환경 설정 후
./scripts/run_multi_seed.sh mappo "lbforaging:Foraging-8x8-2p-3f-v3" 5 foraging common_reward=False
```

## ⚙️ 설정 커스터마이징

### 새로운 W&B 설정 추가

**1. 새 설정 파일 생성**
```bash
# configs/wandb/my_experiment.yaml
use_wandb: True
wandb_project: "my-special-project"
wandb_tags:
  - "custom"
  - "experiment"
```

**2. 스크립트에서 사용**
```bash
python scripts/run_with_wandb.py \
    --wandb-config=my_experiment \
    --config=qmix \
    --env-config=gymma \
    env_args.key="matrixgames:penalty-100-nostate-v0"
```

### 서버별 설정 분리

**개발 서버 설정:**
```bash
# configs/wandb/dev_server.yaml
wandb_project: "marl-lab-dev"
wandb_mode: "offline"
t_max: 50000  # 짧은 실험
```

**프로덕션 서버 설정:**
```bash
# configs/wandb/prod_server.yaml  
wandb_project: "marl-lab-prod"
wandb_mode: "online"
t_max: 2000000  # 긴 실험
```

## 🔄 환경 변수 우선순위

설정 값의 우선순위는 다음과 같습니다:

1. **명령줄 인자** (최우선)
2. **W&B 설정 파일** 
3. **환경 변수**
4. **EPyMARL 기본값** (최하위)

예시:
```bash
# 환경 변수
export WANDB_PROJECT="env-project"

# 설정 파일: wandb_project: "config-project"  

# 명령줄 인자
python scripts/run_with_wandb.py ... wandb_project="cli-project"

# 결과: "cli-project" 사용됨
```

## 🐛 문제 해결

### 일반적인 문제들

**1. W&B 로그인 실패**
```bash
# API 키 확인
cat ~/wandb_config/api_key.txt

# 수동 로그인
wandb login
```

**2. 환경 변수 미적용**
```bash
# 서버 설정 재로드
source configs/server_setup.sh

# 환경 변수 확인
env | grep WANDB
```

**3. GPU 메모리 부족**
```bash
# server_default.yaml에서 다음 설정 확인
buffer_cpu_only: True
use_cuda: True
batch_size_run: 1
```

**4. SMAC2 환경 오류**
```bash
# StarCraft II 설치 확인
ls $SC2PATH
pip install -r external/epymarl/env_requirements.txt
```

### 로그 위치

- **Sacred 로그**: `results/sacred/`
- **TensorBoard**: `results/tb_logs/`  
- **W&B 캐시**: `~/wandb_config/cache/`
- **모델 저장**: `results/models/`