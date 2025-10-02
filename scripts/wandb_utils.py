"""Shared helpers for loading and applying W&B configuration."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import os
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "configs" / "wandb"


def _resolve_config_path(name: str | None) -> Path | None:
    candidates: list[Path] = []
    if name:
        candidate = Path(name)
        if candidate.is_file():
            return candidate
        candidates.append(CONFIG_DIR / (name if name.endswith(".yaml") else f"{name}.yaml"))

    candidates.append(CONFIG_DIR / "default.yaml")

    for path in candidates:
        if path.exists():
            return path
    return None


@dataclass
class WandbSettings:
    entity: str | None = None
    project: str | None = None
    mode: str | None = None
    tags: list[str] = field(default_factory=list)
    group: str | None = None
    notes: str | None = None


def load_wandb_config(name: str | None) -> Tuple[WandbSettings, Dict[str, Any]]:
    path = _resolve_config_path(name)
    data: Dict[str, Any] = {}
    if path and path.exists():
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    elif name:
        print(f"[wandb] 구성 파일을 찾을 수 없습니다: {name}. default.yaml을 사용합니다.")

    wandb_data = data.get("wandb", {}) if isinstance(data, dict) else {}
    overrides = data.get("overrides", {}) if isinstance(data, dict) else {}

    settings = WandbSettings(
        entity=wandb_data.get("entity"),
        project=wandb_data.get("project"),
        mode=wandb_data.get("mode"),
        tags=list(wandb_data.get("tags", []) or []),
        group=wandb_data.get("group"),
        notes=wandb_data.get("notes"),
    )
    return settings, overrides if isinstance(overrides, dict) else {}


def apply_wandb_env(settings: WandbSettings) -> None:
    if settings.entity:
        os.environ["WANDB_ENTITY"] = settings.entity
    if settings.project:
        os.environ["WANDB_PROJECT"] = settings.project
    if settings.mode:
        os.environ["WANDB_MODE"] = settings.mode
    if settings.group:
        os.environ["WANDB_RUN_GROUP"] = settings.group
    if settings.notes:
        os.environ["WANDB_NOTES"] = settings.notes
    if settings.tags:
        os.environ["WANDB_TAGS"] = ",".join(settings.tags)


def format_overrides(overrides: Dict[str, Any], allowed: Iterable[str]) -> list[str]:
    formatted: list[str] = []
    allow = set(allowed)
    for key, value in overrides.items():
        if key not in allow:
            continue
        if isinstance(value, bool):
            formatted.append(f"{key}={str(value)}")
        elif isinstance(value, (int, float)):
            formatted.append(f"{key}={value}")
        elif value is None:
            continue
        else:
            formatted.append(f'{key}="{value}"')
    return formatted
