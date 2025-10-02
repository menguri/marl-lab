# Configs Directory

공유 실험 설정과 러너 스크립트에서 사용하는 YAML/파이썬 헬퍼를 모아둔 공간입니다.
모든 설정은 **상위 저장소에서만 수정**하며, PyMARL2나 MARLlib 서브모듈은 그대로 유지합니다.

## 디렉터리 구조
```
configs/
├── envs/        # PyMARL2 환경 프리셋 (sc2.yaml, sc2v2.yaml 등)
├── exp/         # 실험 조합 템플릿 (알고리즘/환경/with 인자)
├── python/      # 파이썬 기반 유틸리티 (환경 메타데이터 등)
├── smacv2/      # SMACv2 시나리오 YAML 모음
├── wandb/       # W&B 프리셋
└── server/      # 서버용 Shell 설정
```

## 사용 방법
- PyMARL2 실행 시 `--config=<algo>`와 함께 `--env-config=<env>`를 지정하면 해당 YAML을 로드합니다.
- `configs/exp/*.yaml`은 공통 실험 설정을 캡슐화한 것으로 `--exp-config` 옵션으로 읽을 수 있습니다.
- W&B 프리셋(`configs/wandb/<이름>.yaml`)은 `wandb` 블록에 엔티티/프로젝트 정보를, `overrides` 블록에 실행 기본값을 정의합니다. `--wandb-config=<이름>` 옵션으로 PyMARL2와 MARLlib 모두 동일하게 사용할 수 있습니다.

새로운 실험군을 추가할 때는 `configs/exp/`에 YAML을 작성하고 README에 간단히 용도를 남겨 주시면 됩니다.
