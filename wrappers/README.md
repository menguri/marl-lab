# Wrappers

이 디렉터리에는 서브모듈을 수정하지 않고 외부 프레임워크를 확장하기 위한 경량 래퍼를 모아둡니다.

## `smacv2_env.py`
- PyMARL2 `envs.REGISTRY`에 SMACv2 환경(`sc2v2`)을 등록하는 헬퍼입니다.
- 실행 전 `pip install SMACv2 pysc2==4.0.6`이 설치되어 있어야 합니다.
- 사용 방법
  ```bash
  ./scripts/run_smacv2.py --config=qmix --env-config=sc2v2 with env_args.map_name=protoss_5_vs_5
  ```
- 상위 레벨에서 래퍼를 유지하면 PyMARL2 서브모듈을 그대로 업데이트해도 충돌이 없습니다.

새로운 환경을 붙이고 싶다면 동일한 패턴으로 래퍼를 추가한 뒤 실행 스크립트에서 레지스트리를 갱신하세요.
