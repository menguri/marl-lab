# MARL Lab

PyMARL2(SMAC/SMACv2)와 MARLlib(PettingZoo, Overcooked, MA-MuJoCo)를 한 저장소에서 관리하기 위한 멀티에이전트 강화학습 실험 허브입니다. 모든 외부 프레임워크는 `external/`에 서브모듈로 두고, 상위 레벨에서만 설정과 실행 스크립트를 유지합니다.

## 📦 디렉터리 개요
```
external/
├── pymarl2/      # SMAC 실험용 공식 PyMARL2 서브모듈
└── marllib/      # Ray RLlib 기반 멀티환경 프레임워크
configs/          # 환경/실험/W&B 프리셋 (PyMARL2 중심)
wrappers/         # 서브모듈 확장 래퍼 (예: SMACv2 등록)
scripts/          # 실행 스크립트 (PyMARL2, MARLlib 모두)
results/          # 프레임워크별 로그 및 체크포인트
requirements/     # 프레임워크별 의존성 목록
```

## 🚀 준비하기
두 프레임워크가 요구하는 파이썬/라이브러리가 충돌하므로 **별도의 가상환경**을 생성합니다.

### PyMARL2 환경 (SMAC/SMACv2)
```bash
conda create -n pymarl2 python=3.10
conda activate pymarl2
pip install -r requirements/pymarl2.txt
./external/pymarl2/install_sc2.sh  # StarCraft II 및 SMAC 맵 설치 (필요 시)
```

### MARLlib 환경 (Predator-Prey, Overcooked, MA-MuJoCo)
```bash
conda create -n marllib python=3.9
conda activate marllib
pip install -r requirements/marllib.txt
```
> 모든 의존성 전략은 `requirements/README.md`에 상세히 정리했습니다.

## 🧪 PyMARL2 사용법
- 기본 결과 디렉터리: `results/pymarl2/`
- 환경 프리셋: `configs/envs/` (예: `sc2.yaml`, `sc2v2.yaml`)

```bash
# SMAC 3s5z 학습 (W&B 프리셋 포함)
python scripts/run_with_wandb.py --config=qmix --env-config=sc2 \
    with env_args.map_name=3s5z seed=1001

# SMACv2 Protoss 5v5 학습
./scripts/run_smacv2.py --config=qmix --env-config=sc2v2 \
    with env_args.map_name=protoss_5_vs_5 seed=42

# 저장된 체크포인트 평가 및 리플레이 저장
python scripts/evaluate_pymarl2.py --config=qmix --env-config=sc2v2 \
    --checkpoint results/pymarl2/models/qmix_seed42_protoss_5_vs_5/5000000 \
    --save-replay --test-episodes=50
```
SMACv2 registry는 `wrappers/smacv2_env.py`에서 PyMARL2에 주입하며, 시나리오 정의는 `configs/smacv2/`에 복사해두었습니다.
또한 Python 3.10 호환성을 위해 `patches/pymarl2/`의 패치가 필요하며, `bin/run_multi_seed.sh`나 `scripts/apply_pymarl2_patches.sh`가 자동으로 적용합니다.

#### W&B 설정 공유
- `configs/wandb/<이름>.yaml`에서 W&B 엔티티(`entity`), 프로젝트(`project`), 모드(`mode`), 태그 등을 정의합니다.
- 같은 파일의 `overrides` 블록은 PyMARL2/MARLlib 실행 시 기본 하이퍼파라미터(예: `save_model`, `log_interval`)를 덮어쓰는 용도로 사용됩니다.
- `scripts/run_with_wandb.py`, `scripts/run_marllib.py`, `bin/run_multi_seed.sh` 모두 `--wandb-config=<이름>` 옵션을 인식하며, 내부에서 `WANDB_ENTITY`, `WANDB_PROJECT`, `WANDB_MODE` 등의 환경 변수를 자동으로 설정합니다.

### 멀티 시드 실행 (PyMARL2/MARLlib 공통)
```bash
# SMAC 3s5z, 5개 시드, 동시 2개 실행
RUN_MULTI_SEED_WORKERS=2 ./bin/run_multi_seed.sh pymarl2 qmix sc2 5 \
    --map 3s5z --with t_max=3000000 --wandb smac_default

# Predator-Prey(simple_tag) MAPPO, 4개 시드
./bin/run_multi_seed.sh marllib mappo mpe 4 --map simple_tag \
    --timesteps 2000000 --num-workers 8 --share-policy group

# Overcooked cramped_room, GPU 1개 사용
./bin/run_multi_seed.sh marllib mappo overcooked 2 --map cramped_room \
    --num-gpus 1 --local-mode
```
파라미터는 프레임워크에 따라 자동으로 분기되며, 필요한 경우 `--with key=value`(PyMARL2) 또는 `--share-policy`, `--num-workers`(MARLlib) 등을 조합하면 됩니다.

## 🍳 MARLlib 사용법 (Predator-Prey & Overcooked)
- 학습 결과: `results/marllib/`
- 평가 로그: `results/marllib_evals/`

```bash
# Predator-Prey(simple_tag) MAPPO 학습
python scripts/run_marllib.py --env=mpe --map=simple_tag --algo=mappo \
    --timesteps=2000000 --num-workers=8 --share-policy=group

# Overcooked cramped_room MAPPO 학습
python scripts/run_marllib.py --env=overcooked --map=cramped_room --algo=mappo \
    --timesteps=1000000 --share-policy=all

# 체크포인트 평가 (렌더링 포함)
python scripts/evaluate_marllib.py --env=overcooked --map=cramped_room \
    --algo=mappo --trial-dir results/marllib/MAPPO_mlp_cramped_room_00123 \
    --render --evaluation-episodes=10
```

## 📁 주요 폴더 설명
- `configs/envs/` : PyMARL2 환경 YAML. 결과 경로를 `results/pymarl2`로 고정했습니다.
- `configs/smacv2/` : SMACv2 capability 맵 YAML (상위 래퍼에서 참조).
- `wrappers/` : PyMARL2 레지스트리를 확장하는 파이썬 모듈. 현재는 `smacv2_env.py`만 포함.
- `results/README.md` : 프레임워크별 결과 정리 방식 안내.
- `scripts/README.md` : 모든 실행 스크립트 사용법 요약.

## 🧭 연구 로드맵과 스크립트 활용
| 단계 | 목적 | 관련 스크립트 |
| --- | --- | --- |
| Baseline | SMAC/SMACv2 재현 | `run_with_wandb.py`, `run_smacv2.py`, `evaluate_pymarl2.py` |
| Ad-Hoc 강화 | Predator-Prey, Overcooked | `run_marllib.py`, `evaluate_marllib.py` |
| Sim2Real | 추후 ROS2/로보틱스 연계 | 별도 모듈 예정 |

## ✅ 테스트 체크리스트
1. PyMARL2: `./scripts/run_smacv2.py --config=qmix --env-config=sc2v2 with t_max=1000` (1분 이내 완주)
2. MARLlib: `python scripts/run_marllib.py --env=mpe --map=simple_spread --algo=mappo --timesteps=50000 --local-mode`
3. 평가 스크립트: 위 두 실험에서 생성된 체크포인트로 `evaluate_*` 실행

## 🔗 참고 링크
- [PyMARL2 GitHub](https://github.com/hijkzzz/pymarl2)
- [MARLlib Documentation](https://marllib.readthedocs.io/)
- [SMACv2 GitHub](https://github.com/oxwhirl/smacv2)
- [Overcooked-AI](https://github.com/HumanCompatibleAI/overcooked_ai)

궁금한 점이나 개선 아이디어는 `연구노트.txt` 또는 GitHub 이슈로 공유해 주세요.
