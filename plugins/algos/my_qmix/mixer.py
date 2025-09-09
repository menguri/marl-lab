# plugins/algos/my_qmix/mixer.py
class MyMixer:
    def __init__(self, **kwargs):
        # 예: n_agents, state_dim 등 args 주입
        pass
    def __call__(self, agent_qs, states):
        # agent_qs: [B, n_agents], states: [B, state_dim]
        # 아주 단순히 평균만 내는 dummy
        return agent_qs.mean(dim=-1, keepdim=True)
