# Bin Scripts

이 디렉터리에는 상위 프로젝트에서 공용으로 사용하는 셸 스크립트를 모아 둡니다.

- `run_multi_seed.sh` : PyMARL2와 MARLlib 모두를 지원하는 멀티 시드 실행기 (`--wandb-config` 옵션 지원).
  - 예) `RUN_MULTI_SEED_WORKERS=2 ./run_multi_seed.sh pymarl2 qmix sc2 5 --map 3s5z --with t_max=3000000`
  - 예) `./run_multi_seed.sh marllib mappo mpe 4 --map simple_tag --timesteps 2000000 --wandb-config smac2`
- `quick_experiment.sh` : 소규모 빠른 실험 실행용 레거시 스크립트.
- `run_smac_suite.sh` : SMAC/SMACv2 전용 배치 실행기. 3개의 맵 × 5개 알고리즘(IQL/VDN/QMIX/QPLEX/QTRAN)을 시드 2개로 순차 학습합니다.
  - `./run_smac_suite.sh` (SMAC은 `configs/wandb/smac1.yaml`, SMACv2는 `smac2.yaml` 프리셋 사용)
- `run_mpe_pp.sh` : MARLlib MPE Predator-Prey(`simple_tag`) 학습 시 IQL/VDN/IPPO/MAPPO를 시드 2개씩 순차 실행합니다.
  - `./run_mpe_pp.sh`

새로운 셸 스크립트를 추가할 경우 간단한 사용 예시와 결과 경로 규칙을 이 README에 기록해 주세요.
