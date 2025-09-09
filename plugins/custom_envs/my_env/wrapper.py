# plugins/envs/my_env/wrapper.py
import gymnasium as gym
class MyEnvWrapper:
    def __init__(self, **env_args):
        self._env = gym.make(env_args.get("key", "CartPole-v1"))
        # 필요 시: 개별 보상/공동 보상 스위치, obs/act 변환 등

    def reset(self):
        obs, info = self._env.reset()
        return obs

    def step(self, action):
        obs, rew, term, trunc, info = self._env.step(action)
        done = term or trunc
        return obs, rew, done, info

    # EPyMARL가 기대하는 추가 인터페이스(get_env_info 등)가 있다면 맞춰서 구현
