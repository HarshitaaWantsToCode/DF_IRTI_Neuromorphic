"""
Core utilities and configuration loaders.
"""
import yaml
import os
from typing import Dict, Any


def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Loads a YAML configuration file safely."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_directory(dir_path: str) -> str:
    """Ensures a directory exists, creating parents if necessary."""
    os.makedirs(dir_path, exist_ok=True)
    return dir_path
