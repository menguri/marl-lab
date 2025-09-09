# plugins/algos/my_qmix/policy.py
import torch, torch.nn as nn
class MyPolicy(nn.Module):
    def __init__(self, obs_dim, act_dim, **kwargs):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(obs_dim,128), nn.ReLU(), nn.Linear(128, act_dim))
    def forward(self, obs):
        return self.net(obs)  # Q-values
