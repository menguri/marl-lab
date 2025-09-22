# Configs 디렉토리

EPyMARL 실험에서 사용하는 설정과 서버 환경 구성 파일을 모아둔 디렉토리입니다. 실행 가능한 스크립트(`*.sh`)는 모두 `bin/`으로 이동했고, 이 디렉토리에는 순수 설정 자료와 Python 헬퍼만 남겨두었습니다.

## 📁 구성
```
marl-lab/
├── bin/                     # 실행 스크립트 (run_multi_seed.sh 등)
├── configs/
│   ├── python/              # Python 기반 환경/실험 레지스트리
│   │   └── environments.py
│   ├── server/
│   │   └── setup.sh         # 서버 공용 환경 변수 세팅
│   ├── exp/                 # 실험 템플릿 (algo/env/with 인자)
│   └── wandb/               # W&B 프리셋 모음 (YAML)
│       ├── default.yaml
│       ├── server_default.yaml
│       ├── matrix_games.yaml
│       ├── foraging.yaml
│       └── smac2.yaml
└── scripts/                 # Python 실행 스크립트 (unified_experiment.py 등)
```

## 🔧 W&B 프리셋 (`configs/wandb/*.yaml`)

- `default.yaml`: 로컬 개발 환경 기본 설정 (오프라인 모드).  
- `server_default.yaml`: 원격 서버용 설정 (온라인 모드, CPU 버퍼 등).
- `matrix_games.yaml`, `foraging.yaml`, `smac2.yaml`: 환경 특화 프리셋.

W&B 프로젝트/팀명을 바꾸고 싶다면 각 YAML 파일에서 `wandb_project`, `wandb_team` 값을 조정하면 됩니다.

## 🧠 Python 환경 레지스트리 (`configs/python/environments.py`)

환경 메타데이터, 권장 알고리즘, 기본 하이퍼파라미터 등을 코드로 정의해 둔 모듈입니다. `scripts/*`에서 `from configs.python.environments import ...` 형태로 불러와 사용합니다.

## 🖥️ 서버 환경 설정 (`configs/server/setup.sh`)

원격 서버 접속 후 한 번만 `source` 해두면 W&B, CUDA, 결과 경로 등이 자동으로 맞춰집니다.

```bash
# 1. 서버에서 환경 변수 로드
source configs/server/setup.sh

# 2. 재접속 시 자동 적용하고 싶다면 (예: ~/.bashrc)
echo "source ~/marl-lab/configs/server/setup.sh" >> ~/.bashrc
```

**포함된 설정**
- `WANDB_DIR`, `WANDB_API_KEY` 자동 로드
- `WANDB_ENTITY`, `WANDB_PROJECT` 기본값 지정
- `CUDA_VISIBLE_DEVICES`, `SC2PATH` 예시 설정
- `MARL_LAB_ROOT`, `RESULTS_DIR` 자동 계산

> `WANDB_CONFIG_DIR/api_key.txt` 파일이 존재하면 API 키를 읽어 자동으로 로그인합니다.

## 🚀 활용 예시

```bash
# 빠른 실험
./bin/quick_experiment.sh qmix matrix_penalty

# 서버 프로파일로 실행
./bin/server_run.sh qmix smac2_terran server_default

# 다중 시드 실험 (동시 워커 4개)
RUN_MULTI_SEED_WORKERS=4 ./bin/run_multi_seed.sh mappo "lbforaging:Foraging-8x8-2p-3f-v3" 5 foraging common_reward=False

# YAML 템플릿을 활용한 SMAC 3s5z 실험
./bin/run_multi_seed.sh qmix sc2 3 smac1 exp_config=smac_qmix_rnn

# Python 기반 통합 실험 러너
python scripts/unified_experiment.py --algorithm qmix --environment matrix_penalty --seeds 3
```

필요한 설정을 원하는 곳에 복사하거나 새 YAML을 추가해도 좋습니다. 새 프리셋을 만들었다면 README에 명시하거나 팀과 공유하여 일관성을 유지하세요.
