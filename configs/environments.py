#!/usr/bin/env python3
"""
통합 환경 설정 관리
모든 지원 환경의 설정을 중앙에서 관리합니다.
"""

from typing import Dict, Any, Optional

class EnvironmentConfig:
    """환경 설정 클래스"""
    
    def __init__(self, key: str, env_config: str, wandb_config: str, 
                 default_args: str, description: str, 
                 t_max: Optional[int] = None, supports_individual_rewards: bool = False):
        self.key = key
        self.env_config = env_config
        self.wandb_config = wandb_config
        self.default_args = default_args
        self.description = description
        self.t_max = t_max
        self.supports_individual_rewards = supports_individual_rewards

# 전체 환경 설정 레지스트리
ENVIRONMENTS: Dict[str, EnvironmentConfig] = {
    
    # ===== Matrix Games =====
    'matrix_penalty': EnvironmentConfig(
        key='matrixgames:penalty-100-nostate-v0',
        env_config='gymma',
        wandb_config='matrix_games',
        default_args='env_args.time_limit=25',
        description='Matrix Penalty Game (-100 penalty)',
        t_max=50000,
        supports_individual_rewards=False
    ),
    'matrix_climbing': EnvironmentConfig(
        key='matrixgames:climbing-nostate-v0',
        env_config='gymma',
        wandb_config='matrix_games',
        default_args='env_args.time_limit=25',
        description='Matrix Climbing Game',
        t_max=50000,
        supports_individual_rewards=False
    ),
    'matrix_penalty_25': EnvironmentConfig(
        key='matrixgames:penalty-25-nostate-v0',
        env_config='gymma',
        wandb_config='matrix_games',
        default_args='env_args.time_limit=25',
        description='Matrix Penalty Game (-25 penalty)',
        t_max=50000,
        supports_individual_rewards=False
    ),
    'matrix_penalty_50': EnvironmentConfig(
        key='matrixgames:penalty-50-nostate-v0',
        env_config='gymma',
        wandb_config='matrix_games',
        default_args='env_args.time_limit=25',
        description='Matrix Penalty Game (-50 penalty)',
        t_max=50000,
        supports_individual_rewards=False
    ),
    
    # ===== Level-Based Foraging =====
    'lbf_small': EnvironmentConfig(
        key='lbforaging:Foraging-8x8-2p-3f-v3',
        env_config='gymma',
        wandb_config='foraging',
        default_args='env_args.time_limit=50',
        description='Small LBF (8x8, 2 players, 3 food)',
        t_max=500000,
        supports_individual_rewards=True
    ),
    'lbf_medium': EnvironmentConfig(
        key='lbforaging:Foraging-10x10-3p-3f-v3',
        env_config='gymma',
        wandb_config='foraging',
        default_args='env_args.time_limit=50',
        description='Medium LBF (10x10, 3 players, 3 food)',
        t_max=500000,
        supports_individual_rewards=True
    ),
    'lbf_large': EnvironmentConfig(
        key='lbforaging:Foraging-15x15-3p-5f-v3',
        env_config='gymma',
        wandb_config='foraging',
        default_args='env_args.time_limit=50',
        description='Large LBF (15x15, 3 players, 5 food)',
        t_max=1000000,
        supports_individual_rewards=True
    ),
    'lbf_coop_small': EnvironmentConfig(
        key='lbforaging:Foraging-8x8-2p-2f-coop-v3',
        env_config='gymma',
        wandb_config='foraging',
        default_args='env_args.time_limit=50',
        description='Cooperative LBF (8x8, 2 players, 2 food)',
        t_max=500000,
        supports_individual_rewards=True
    ),
    
    # ===== Multi-Robot Warehouse =====
    'rware_tiny': EnvironmentConfig(
        key='rware:rware-tiny-2ag-v2',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=500',
        description='Tiny RWARE (2 agents)',
        t_max=1000000,
        supports_individual_rewards=True
    ),
    'rware_small': EnvironmentConfig(
        key='rware:rware-small-4ag-v2',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=500',
        description='Small RWARE (4 agents)',
        t_max=1000000,
        supports_individual_rewards=True
    ),
    'rware_tiny_4ag': EnvironmentConfig(
        key='rware:rware-tiny-4ag-v2',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=500',
        description='Tiny RWARE (4 agents)',
        t_max=1000000,
        supports_individual_rewards=True
    ),
    
    # ===== Multi-Agent Particle Environment =====
    'mpe_spread': EnvironmentConfig(
        key='pz-mpe-simple-spread-v3',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=25',
        description='MPE Simple Spread',
        t_max=1000000,
        supports_individual_rewards=False
    ),
    'mpe_speaker_listener': EnvironmentConfig(
        key='pz-mpe-simple-speaker-listener-v4',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=25',
        description='MPE Simple Speaker Listener',
        t_max=1000000,
        supports_individual_rewards=False
    ),
    'mpe_adversary': EnvironmentConfig(
        key='pz-mpe-simple-adversary-v3',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=25 env_args.pretrained_wrapper="PretrainedAdversary"',
        description='MPE Simple Adversary',
        t_max=1000000,
        supports_individual_rewards=False
    ),
    'mpe_tag': EnvironmentConfig(
        key='pz-mpe-simple-tag-v3',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=25 env_args.pretrained_wrapper="PretrainedTag"',
        description='MPE Simple Tag',
        t_max=1000000,
        supports_individual_rewards=False
    ),
    
    # ===== SMAC (StarCraft Multi-Agent Challenge) =====
    'smac_3s5z': EnvironmentConfig(
        key='3s5z',
        env_config='sc2',
        wandb_config='smac1',
        default_args='env_args.map_name="3s5z"',
        description='SMAC 3 Stalkers & 5 Zealots vs 3 Stalkers & 5 Zealots',
        t_max=2000000,
        supports_individual_rewards=False
    ),
    'smac_2s_vs_1sc': EnvironmentConfig(
        key='2s_vs_1sc',
        env_config='sc2',
        wandb_config='smac1',
        default_args='env_args.map_name="2s_vs_1sc"',
        description='SMAC 2 Stalkers vs 1 Spine Crawler',
        t_max=2000000,
        supports_individual_rewards=False
    ),
    'smac_corridor': EnvironmentConfig(
        key='corridor',
        env_config='sc2',
        wandb_config='smac1',
        default_args='env_args.map_name="corridor"',
        description='SMAC Corridor',
        t_max=2000000,
        supports_individual_rewards=False
    ),
    'smac_MMM2': EnvironmentConfig(
        key='MMM2',
        env_config='sc2',
        wandb_config='smac1',
        default_args='env_args.map_name="MMM2"',
        description='SMAC Marines, Marauders & Medivacs 2',
        t_max=2000000,
        supports_individual_rewards=False
    ),
    'smac_3s_vs_5z': EnvironmentConfig(
        key='3s_vs_5z',
        env_config='sc2',
        wandb_config='smac1',
        default_args='env_args.map_name="3s_vs_5z"',
        description='SMAC 3 Stalkers vs 5 Zealots',
        t_max=2000000,
        supports_individual_rewards=False
    ),
    
    # ===== SMACv2 =====
    'smac2_terran': EnvironmentConfig(
        key='terran_5_vs_5',
        env_config='sc2v2',
        wandb_config='smac2',
        default_args='env_args.map_name="terran_5_vs_5"',
        description='SMACv2 Terran vs Terran (5v5)',
        t_max=2000000,
        supports_individual_rewards=False
    ),
    'smac2_protoss': EnvironmentConfig(
        key='protoss_5_vs_5',
        env_config='sc2v2',
        wandb_config='smac2',
        default_args='env_args.map_name="protoss_5_vs_5"',
        description='SMACv2 Protoss vs Protoss (5v5)',
        t_max=2000000,
        supports_individual_rewards=False
    ),
    'smac2_zerg': EnvironmentConfig(
        key='zerg_5_vs_5',
        env_config='sc2v2',
        wandb_config='smac2',
        default_args='env_args.map_name="zerg_5_vs_5"',
        description='SMACv2 Zerg vs Zerg (5v5)',
        t_max=2000000,
        supports_individual_rewards=False
    ),
    'smac2_terran_10v10': EnvironmentConfig(
        key='terran_10_vs_10',
        env_config='sc2v2',
        wandb_config='smac2',
        default_args='env_args.map_name="terran_10_vs_10"',
        description='SMACv2 Terran vs Terran (10v10)',
        t_max=3000000,
        supports_individual_rewards=False
    ),
    
    # ===== VMAS =====
    'vmas_balance': EnvironmentConfig(
        key='vmas-balance',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=150 env_args.key="vmas-balance"',
        description='VMAS Balance',
        t_max=1000000,
        supports_individual_rewards=True
    ),
    'vmas_transport': EnvironmentConfig(
        key='vmas-transport',
        env_config='gymma',
        wandb_config='default',
        default_args='env_args.time_limit=150 env_args.key="vmas-transport"',
        description='VMAS Transport',
        t_max=1000000,
        supports_individual_rewards=True
    )
}

# 알고리즘별 추천 환경
ALGORITHM_RECOMMENDATIONS = {
    # 공통 보상 환경에서만 작동하는 알고리즘
    'qmix': {
        'good': ['matrix_penalty', 'smac_3s5z', 'smac2_terran', 'mpe_spread'],
        'supported_envs': [env for env, config in ENVIRONMENTS.items() if not config.supports_individual_rewards],
        'description': 'Q-value mixing - 공통 보상 환경에서 강력'
    },
    'vdn': {
        'good': ['matrix_penalty', 'matrix_climbing', 'smac_3s5z', 'mpe_spread'],
        'supported_envs': [env for env, config in ENVIRONMENTS.items() if not config.supports_individual_rewards],
        'description': 'Value Decomposition Networks - 간단하고 안정적'
    },
    'qtran': {
        'good': ['matrix_penalty', 'smac_MMM2', 'smac2_protoss'],
        'supported_envs': [env for env, config in ENVIRONMENTS.items() if not config.supports_individual_rewards],
        'description': 'Q-Transformation - 복잡한 협력 환경에서 우수'
    },
    'coma': {
        'good': ['smac_3s5z', 'smac_corridor', 'matrix_climbing'],
        'supported_envs': [env for env, config in ENVIRONMENTS.items() if not config.supports_individual_rewards],
        'description': 'Counterfactual Multi-Agent Policy Gradients'
    },
    
    # 개별 보상 환경 지원 알고리즘
    'mappo': {
        'good': ['lbf_small', 'lbf_medium', 'rware_tiny', 'vmas_balance'],
        'supported_envs': list(ENVIRONMENTS.keys()),
        'description': 'Multi-Agent PPO - 개별 보상 환경에서 강력'
    },
    'ippo': {
        'good': ['lbf_small', 'rware_tiny', 'vmas_transport'],
        'supported_envs': list(ENVIRONMENTS.keys()),
        'description': 'Independent PPO - 안정적이고 확장성 좋음'
    },
    'maa2c': {
        'good': ['lbf_medium', 'rware_small', 'mpe_spread'],
        'supported_envs': list(ENVIRONMENTS.keys()),
        'description': 'Multi-Agent A2C - 빠른 학습'
    },
    'ia2c': {
        'good': ['lbf_small', 'matrix_penalty', 'mpe_spread'],
        'supported_envs': list(ENVIRONMENTS.keys()),
        'description': 'Independent A2C - 가벼운 알고리즘'
    },
    'iql': {
        'good': ['matrix_penalty', 'lbf_small', 'rware_tiny'],
        'supported_envs': list(ENVIRONMENTS.keys()),
        'description': 'Independent Q-Learning - 기본적인 알고리즘'
    },
    'pac': {
        'good': ['matrix_penalty', 'matrix_climbing', 'lbf_coop_small'],
        'supported_envs': list(ENVIRONMENTS.keys()),
        'description': 'Pareto Actor-Critic - 다중 균형점 환경에서 우수'
    },
    'maddpg': {
        'good': ['mpe_spread', 'mpe_adversary', 'vmas_balance'],
        'supported_envs': list(ENVIRONMENTS.keys()),
        'description': 'Multi-Agent DDPG - 연속 액션 공간'
    }
}

def get_environment_config(env_name: str) -> Optional[EnvironmentConfig]:
    """환경 설정을 가져옵니다."""
    return ENVIRONMENTS.get(env_name)

def get_supported_environments() -> Dict[str, str]:
    """지원하는 모든 환경의 이름과 설명을 반환합니다."""
    return {name: config.description for name, config in ENVIRONMENTS.items()}

def get_algorithm_recommendations(algorithm: str) -> Dict[str, Any]:
    """알고리즘별 추천 환경을 반환합니다."""
    return ALGORITHM_RECOMMENDATIONS.get(algorithm, {
        'good': [],
        'supported_envs': list(ENVIRONMENTS.keys()),
        'description': 'Unknown algorithm'
    })

def filter_environments_by_category(category: str) -> Dict[str, EnvironmentConfig]:
    """카테고리별로 환경을 필터링합니다."""
    category_filters = {
        'matrix': lambda name: name.startswith('matrix_'),
        'lbf': lambda name: name.startswith('lbf_'),
        'rware': lambda name: name.startswith('rware_'),
        'mpe': lambda name: name.startswith('mpe_'),
        'smac1': lambda name: name.startswith('smac_'),
        'smac2': lambda name: name.startswith('smac2_'),
        'vmas': lambda name: name.startswith('vmas_'),
        'quick': lambda name: name in ['matrix_penalty', 'lbf_small', 'rware_tiny', 'mpe_spread', 'smac_3s5z', 'smac2_terran'],
        'individual_rewards': lambda name: ENVIRONMENTS[name].supports_individual_rewards
    }
    
    if category not in category_filters:
        return {}
    
    filter_func = category_filters[category]
    return {name: config for name, config in ENVIRONMENTS.items() if filter_func(name)}

if __name__ == "__main__":
    # 테스트 코드
    print("=== 지원하는 환경들 ===")
    for category in ['matrix', 'lbf', 'rware', 'mpe', 'smac1', 'smac2', 'vmas']:
        envs = filter_environments_by_category(category)
        if envs:
            print(f"\n{category.upper()}:")
            for name, config in envs.items():
                print(f"  {name}: {config.description}")
    
    print("\n=== 개별 보상 지원 환경 ===")
    individual_envs = filter_environments_by_category('individual_rewards')
    for name, config in individual_envs.items():
        print(f"  {name}: {config.description}")