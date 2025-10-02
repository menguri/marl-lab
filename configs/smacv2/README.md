# SMACv2 Scenario Files

`wrappers/smacv2_env.py`가 참조하는 capability 맵 정의 YAML입니다. 각 파일 이름은
`env_args.map_name` 값과 일치해야 하며, SMACv2 공식 저장소에서 제공하는 설정을 그대로 복사했습니다.

새로운 시나리오를 추가하려면 SMACv2 저장소의 YAML을 가져와 이 디렉터리에 저장하고,
실행 시 `with env_args.map_name=<파일이름>` 으로 지정하면 됩니다.
