# Environment Presets

PyMARL2에서 사용할 환경 설정 템플릿을 모아둔 디렉터리입니다. `scripts/run_with_wandb.py` 또는
`scripts/run_once.py` 실행 시 `--env-config=<name>` 형식으로 선택합니다.

## 파일 설명
- `sc2.yaml` : SMAC(기존 맵) 기본 설정. 결과 저장 경로를 `results/pymarl2`로 고정했습니다.
- `sc2v2.yaml` : SMACv2 맵 기본 설정. `env_args.map_name`을 덮어써서 다른 capability 맵을 선택할 수 있습니다.

필요에 따라 새로운 YAML을 추가하면 되며, 공통 필드는 PyMARL2의 `src/config/envs` 구조를 그대로 따릅니다.
각 YAML에는 최소한 `env`, `env_args`, `t_max` 값이 있어야 합니다.

### 예시
```bash
./scripts/run_with_wandb.py --config=qmix --env-config=sc2 \
    with env_args.map_name=3s5z seed=1001 t_max=3000000
```
