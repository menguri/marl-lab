# plugins/registry.py
# EPyMARL 내부 REGISTRY 경로/키는 버전에 따라 다를 수 있음(핵심: add만 하면 됨)

# 이미 run_once.py가 epymarl/src를 sys.path에 넣어둔 상태
# → 각 서브시스템의 REGISTRY를 개별 import
from controllers import REGISTRY as MACS
from learners import REGISTRY as LEARNERS
from envs import REGISTRY as ENVS


# ── 스모크: 업스트림 basic_mac 을 내 별칭으로도 부르기
if "basic_mac" in MACS:
    MACS["my_mac"] = MACS["basic_mac"]
    
    
# 
from plugins.algos.my_qmix.my_q_learner import PatchedQLearner
LEARNERS["my_q_learner"] = PatchedQLearner

# 1) 최소 smoke: 업스트림 qmix를 "내 별칭"으로도 부를 수 있게 alias
# from external.epymarl.src.controllers import basic_controller as ep_qmix_controller
# REGISTRY["mac"]["my_qmix"] = ep_qmix_controller.BasicMAC

# # 2) 내가 만든 믹서/로스/환경도 이런 식으로 등록(나중에 채움)
# from plugins.algos.my_qmix.mixer import MyMixer
# REGISTRY["mixer"]["my_mixer"] = MyMixer

# # 3) 환경 래퍼도 등록
# from plugins.envs.my_env.wrapper import MyEnvWrapper
# REGISTRY["env"]["my_env"] = MyEnvWrapper
