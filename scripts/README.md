# Scripts

PyMARL2와 MARLlib 실험을 상위 레포에서 직접 제어하기 위한 헬퍼 스크립트 모음입니다. 실행 가능한 셸 스크립트는
`bin/`에 있으며, 이 디렉터리에는 Python 진입점만 남겨 두었습니다.

## PyMARL2 (SMAC / SMACv2)
| 스크립트 | 설명 |
| --- | --- |
| `run_with_wandb.py` | W&B 프리셋과 함께 PyMARL2 학습을 실행합니다. `--config`, `--env-config`, `--wandb-config`, `with` 인자를 사용할 수 있고 결과는 `results/pymarl2/`에 저장됩니다. |
| `run_smacv2.py` | SMACv2 레지스트리를 등록한 뒤 PyMARL2 `main.py`를 실행합니다. `--config=qmix --env-config=sc2v2` 형태로 사용하세요. |
| `run_once.py` | 빠르게 한 번만 실행하고 싶은 경우 사용합니다. 기본적으로 `sc2v2` 환경과 `results/pymarl2` 경로를 지정합니다. |
| `evaluate_pymarl2.py` | 저장된 체크포인트를 불러와 평가 모드(`evaluate=True`)로 실행하고 필요 시 SC2 리플레이를 저장합니다. |
| `apply_pymarl2_patches.sh` | Python 3.10 호환 패치를 PyMARL2 서브모듈에 적용합니다. `run_multi_seed.sh`에서 자동으로 실행되며, 필요시 수동으로 실행할 수 있습니다. |

### 예시
```bash
# SMAC 3s5z 학습 (PyMARL2 기본 설정 + WandB 프리셋)
python scripts/run_with_wandb.py --config=qmix --env-config=sc2 \
    with env_args.map_name=3s5z seed=1001

# SMACv2 Protoss 5v5 학습
./scripts/run_smacv2.py --config=qmix --env-config=sc2v2 \
    with env_args.map_name=protoss_5_vs_5 seed=42

# 베스트 체크포인트 평가 및 리플레이 저장
python scripts/evaluate_pymarl2.py --config=qmix --env-config=sc2v2 \
    --checkpoint results/pymarl2/models/qmix_seed42_protoss_5_vs_5/5000000 \
    --save-replay --test-episodes 50
```

## MARLlib (Predator-Prey, Overcooked, MA-MuJoCo)
| 스크립트 | 설명 |
| --- | --- |
| `run_marllib.py` | MARLlib 고수준 API를 사용해 PettingZoo(MPE)와 Overcooked 실험을 실행합니다. `--wandb-config` 옵션으로 동일한 W&B 프리셋을 사용할 수 있으며, 결과는 `results/marllib/`에 저장됩니다. |
| `evaluate_marllib.py` | Ray Tune trial 디렉터리와 체크포인트를 지정해 평가/렌더링을 수행합니다. 결과는 `results/marllib_evals/`에 기록합니다. |

### 예시
```bash
# Predator-Prey(simple_tag) MAPPO 학습
python scripts/run_marllib.py --env=mpe --map=simple_tag --algo=mappo \
    --timesteps=2000000 --num-workers=8 --share-policy=group

# Overcooked cramped_room 레이아웃 MAPPo 학습
python scripts/run_marllib.py --env=overcooked --map=cramped_room --algo=mappo \
    --timesteps=1000000 --num-workers=4 --share-policy=all

# 학습된 체크포인트 평가 (렌더링 포함)
python scripts/evaluate_marllib.py --env=overcooked --map=cramped_room \
    --algo=mappo --trial-dir results/marllib/MAPPO_mlp_cramped_room_00123 \
    --render --evaluation-episodes=10
```

## 기타
- `unified_experiment.py` 와 `algorithm_comparison.py` 는 기존 EPyMARL 워크플로를 기반으로 작성된 레거시 스크립트입니다. 현재 PyMARL2 전용 환경 정의(`configs/python/environments.py`)를 업데이트하지 않았으므로, 새 파이프라인에서는 사용을 권장하지 않습니다.
- `bin/run_multi_seed.sh` 는 PyMARL2와 MARLlib 모두를 지원하는 멀티 시드 실행용 셸 스크립트입니다. 예)
  - `RUN_MULTI_SEED_WORKERS=2 ./bin/run_multi_seed.sh pymarl2 qmix sc2 5 --map 3s5z --with t_max=3000000`
  - `./bin/run_multi_seed.sh marllib mappo mpe 4 --map simple_tag --timesteps 2000000`
- `bin/quick_experiment.sh` 등 기타 스크립트는 필요 시 직접 수정하여 사용할 수 있습니다.

새로운 스크립트를 추가할 때는 README에 간단한 사용법과 결과 경로 규칙을 함께 기록해 주세요.
