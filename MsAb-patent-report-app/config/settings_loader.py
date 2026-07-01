from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import os
from typing import Any

import yaml


ENV_TO_CONFIG = {
    "MSAB_NEO4J_URI": ("neo4j", "uri"),
    "MSAB_NEO4J_USER": ("neo4j", "user"),
    "MSAB_NEO4J_PASSWORD": ("neo4j", "password"),
    "MSAB_NEO4J_DATABASE": ("neo4j", "database"),
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"settings file must contain a mapping: {path}")
    return data


def _parse_env_txt(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    neo4j: dict[str, str] = {}
    in_neo4j = False
    neo4j_keys = {"uri", "user", "password", "database"}
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if line.lower().rstrip(":") == "neo4j":
            in_neo4j = True
            continue

        if in_neo4j and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key in neo4j_keys:
                if value:
                    neo4j[key] = value
                continue
            in_neo4j = False

        if in_neo4j:
            in_neo4j = False

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key == "NEO4J_URI":
                neo4j["uri"] = value
            elif key == "NEO4J_USER":
                neo4j["user"] = value
            elif key == "NEO4J_PASSWORD":
                neo4j["password"] = value
            elif key == "NEO4J_DATABASE":
                neo4j["database"] = value
            continue

        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key == "NEO4J_URI":
                neo4j["uri"] = value
            elif key == "NEO4J_USER":
                neo4j["user"] = value
            elif key == "NEO4J_PASSWORD":
                neo4j["password"] = value
            elif key == "NEO4J_DATABASE":
                neo4j["database"] = value
    return {"neo4j": neo4j} if neo4j else {}


def _apply_environment(config: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(config)
    for env_name, path in ENV_TO_CONFIG.items():
        value = os.getenv(env_name)
        if value is None:
            continue
        section, key = path
        merged.setdefault(section, {})
        merged[section][key] = value
    return merged


def load_settings(path: str | Path, env_txt_path: str | Path | None = None) -> dict[str, Any]:
    settings_path = Path(path)
    config = _read_yaml(settings_path)

    if env_txt_path is None:
        candidate = settings_path.resolve().parents[2] / "Env.txt"
        env_txt_path = candidate if candidate.exists() else None
    if env_txt_path is not None:
        config = _deep_merge(config, _parse_env_txt(Path(env_txt_path)))

    local_path = settings_path.with_name("settings.local.yaml")
    config = _deep_merge(config, _read_yaml(local_path))
    return _apply_environment(config)
