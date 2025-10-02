# Patches

이 디렉터리는 서브모듈에 적용해야 하는 호환성 패치를 보관합니다.
현재는 PyMARL2의 Python 3.10 지원을 위한 패치(`pymarl2/0001-use-collections-abc.patch`)만 존재합니다.

패치를 적용하려면:
```bash
./scripts/apply_pymarl2_patches.sh
```
`bin/run_multi_seed.sh`는 PyMARL2 실험을 실행하기 전에 자동으로 위 스크립트를 호출합니다.
