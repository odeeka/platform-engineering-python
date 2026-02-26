"""Loader: parse YAML/JSON config files."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


def load_config(path: str | Path) -> dict:
    """Load a YAML or JSON config file and return the parsed dict."""
    p = Path(path)
    text = p.read_text()

    if p.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(text)
    elif p.suffix == ".json":
        data = json.loads(text)
    else:
        # Try YAML first, fall back to JSON
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            data = json.loads(text)

    if not isinstance(data, dict):
        raise ValueError(f"Config file '{p}' must contain a mapping, got {type(data).__name__}")
    return data
