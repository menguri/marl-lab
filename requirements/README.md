# Dependency Strategy

이 저장소는 두 개의 서로 다른 러닝 프레임워크(PyMARL2, MARLlib)를 사용합니다. 두 프레임워크가 요구하는
파이썬 버전과 주요 라이브러리(PyTorch, Ray 등)가 상충하기 때문에 **각 프레임워크별로 독립된 가상환경**을
만드는 것을 권장합니다.

## 1. PyMARL2 (SMAC / SMACv2)
- 권장 파이썬: 3.9 또는 3.10
- 필요한 패키지: `requirements/pymarl2.txt`
- 설치 예시
  ```bash
  conda create -n pymarl2 python=3.10
  conda activate pymarl2
  pip install -r requirements/pymarl2.txt
  ```
- CUDA 버전에 맞춰 PyTorch wheel(`--extra-index-url`)을 조정하세요.

## 2. MARLlib (Predator-Prey, Overcooked, MA-MuJoCo)
- 권장 파이썬: 3.8 또는 3.9 (Ray 1.8.0 호환 범위)
- 필요한 패키지: `requirements/marllib.txt`
- 설치 예시
  ```bash
  conda create -n marllib python=3.9
  conda activate marllib
  pip install -r requirements/marllib.txt
  ```
- MA-MuJoCo를 사용하려면 MuJoCo 라이선스 및 `mujoco-py` 환경 세팅이 추가로 필요합니다.

## 3. 통합 `requirements.txt`
루트의 `requirements.txt`는 위 두 파일을 안내용으로 연결하고 있습니다. 특정 프레임워크만 사용할 경우
해당 경로만 설치하면 됩니다. 하나의 파이썬 환경에 두 프레임워크를 모두 설치하려면 Ray/PyTorch 버전을
다시 조정해야 하며, 현재 조합은 동일한 환경에서의 안정성을 보증하지 않습니다.

## 4. 추가 패키지
- StarCraft II 바이너리(4.10+)와 맵 파일은 `external/pymarl2/install_sc2.sh` 참고
- Overcooked는 `overcooked-ai` 패키지를 설치하면 자동으로 포함됩니다.
- GPU 사용 시 NVIDIA 드라이버 및 CUDA Toolkit 버전에 맞는 PyTorch wheel을 선택하세요.

환경 구성 후 `python --version`과 `pip list`를 확인하여 Ray/Torch가 정상 설치되었는지 반드시 점검하세요.
