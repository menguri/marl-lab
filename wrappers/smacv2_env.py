"""SMACv2 environment wrapper for PyMARL2 without touching the submodule."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

try:
    from smacv2.env.starcraft2.wrapper import StarCraftCapabilityEnvWrapper
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "smacv2.env.starcraft2.wrapper is required. Install smacv2 with `pip install smacv2`."
    ) from exc

CONFIG_ROOT = Path(__file__).resolve().parents[1] / "configs" / "smacv2"


class SMACv2Env:
    """PyMARL2-compatible SMACv2 environment wrapper."""

    def __init__(self, map_name: str, seed: int | None = None, **kwargs: Any) -> None:
        self._map_name = map_name
        self._config_path = CONFIG_ROOT / f"{map_name}.yaml"
        if not self._config_path.exists():
            available = sorted(p.stem for p in CONFIG_ROOT.glob("*.yaml"))
            raise ValueError(f"Unknown SMACv2 map '{map_name}'. Available: {available}")

        scenario_args = _load_scenario_args(self._config_path)
        env_args: Dict[str, Any] = scenario_args.get("env_args", {})
        if seed is not None:
            env_args["seed"] = seed
        env_args.update(kwargs)

        self.env = StarCraftCapabilityEnvWrapper(**env_args)
        self.episode_limit = self.env.episode_limit

    # Standard PyMARL2 environment API -------------------------------------------------
    def step(self, actions):
        rewards, terminated, info = self.env.step(actions)
        observations = self.get_obs()
        truncated = False
        return observations, rewards, terminated, truncated, info

    def reset(self, seed: int | None = None, options: Dict[str, Any] | None = None):
        if seed is not None:
            self.env.seed(seed)
        observations, _ = self.env.reset()
        return observations, {}

    def close(self) -> None:
        self.env.close()

    # Delegated helpers ----------------------------------------------------------------
    def get_obs(self):
        return self.env.get_obs()

    def get_obs_agent(self, agent_id: int):
        return self.env.get_obs_agent(agent_id)

    def get_obs_size(self) -> int:
        return self.env.get_obs_size()

    def get_state(self):
        return self.env.get_state()

    def get_state_size(self) -> int:
        return self.env.get_state_size()

    def get_avail_actions(self):
        return self.env.get_avail_actions()

    def get_avail_agent_actions(self, agent_id: int):
        return self.env.get_avail_agent_actions(agent_id)

    def get_total_actions(self) -> int:
        return self.env.get_total_actions()

    def render(self) -> None:
        self.env.render()

    def seed(self, seed: int | None = None) -> None:
        self.env.seed(seed)

    def save_replay(self) -> None:
        self.env.save_replay()

    def get_env_info(self) -> Dict[str, Any]:
        return self.env.get_env_info()

    def get_stats(self) -> Dict[str, Any]:
        return self.env.get_stats()


def _load_scenario_args(config_path: Path) -> Dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def register_smacv2_env() -> None:
    """Register SMACv2 under the PyMARL2 env REGISTRY if not already present."""
    from external.pymarl2.src import envs as pymarl2_envs

    if "sc2v2" in pymarl2_envs.REGISTRY:
        return

    def _factory(**kwargs: Any) -> SMACv2Env:
        return SMACv2Env(**kwargs)

    pymarl2_envs.REGISTRY["sc2v2"] = _factory
