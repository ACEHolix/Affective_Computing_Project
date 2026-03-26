#!/usr/bin/env python3

import json
from copy import deepcopy
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().with_name("config.json")


def _deep_merge(base, override):
    if not isinstance(base, dict) or not isinstance(override, dict):
        return deepcopy(override)
    merged = deepcopy(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_workflow_config(config_path=None):
    default_path = DEFAULT_CONFIG_PATH
    base = _load_json(default_path)
    chosen_path = Path(config_path).expanduser().resolve() if config_path else default_path.resolve()
    if chosen_path == default_path.resolve():
        return base, str(chosen_path)
    override = _load_json(chosen_path)
    return _deep_merge(base, override), str(chosen_path)


def pretty_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)
