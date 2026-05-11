"""
Configuration management module.
配置管理模块。
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


DEFAULT_CONFIG = {
    "search": {
        "default_sources": ["duckduckgo", "wikipedia"],
        "max_results_per_source": 10,
        "request_timeout": 30,
        "user_agent": "DeepProbe/1.0 (Research Bot; +https://github.com/gitstq/DeepProbe)",
        "cache_enabled": True,
        "cache_ttl_hours": 24,
    },
    "llm": {
        "provider": "none",
        "model": "none",
        "api_key": "",
        "base_url": "",
        "max_tokens": 4096,
        "temperature": 0.7,
    },
    "report": {
        "default_format": "markdown",
        "default_language": "auto",
        "include_references": True,
        "include_summary": True,
        "include_timeline": True,
        "max_sections": 10,
    },
    "storage": {
        "database_path": "~/.deepprobe/deepprobe.db",
        "export_dir": "~/.deepprobe/exports",
        "max_history": 1000,
    },
    "ui": {
        "theme": "dark",
        "color_enabled": True,
        "progress_enabled": True,
        "table_max_width": 80,
    },
}


class ConfigManager:
    """Manages DeepProbe configuration."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self._config_path = Path(config_path)
        else:
            self._config_dir = Path(os.path.expanduser("~/.deepprobe"))
            self._config_dir.mkdir(parents=True, exist_ok=True)
            self._config_path = self._config_dir / "config.json"
        self._config = self._load()

    def _load(self) -> dict:
        """Load configuration from file."""
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                return self._merge(self._deep_copy(DEFAULT_CONFIG), user_config)
            except (json.JSONDecodeError, IOError):
                return self._deep_copy(DEFAULT_CONFIG)
        return self._deep_copy(DEFAULT_CONFIG)

    @staticmethod
    def _deep_copy(d: dict) -> dict:
        """Create a deep copy of a dictionary using json serialization."""
        return json.loads(json.dumps(d))

    @staticmethod
    def _merge(base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        result = dict(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge(result[key], value)
            else:
                result[key] = value
        return result

    def save(self) -> None:
        """Save current configuration to file."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-notation key."""
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        # Try to parse numeric/boolean values
        if isinstance(value, str):
            if value.lower() in ("true", "yes"):
                value = True
            elif value.lower() in ("false", "no"):
                value = False
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
        config[keys[-1]] = value
        self.save()

    def list_all(self) -> None:
        """List all configuration values."""
        def _print_dict(d: dict, prefix: str = ""):
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    _print_dict(value, full_key)
                else:
                    # Mask sensitive values
                    if "key" in key.lower() and isinstance(value, str) and len(value) > 8:
                        display = value[:4] + "****" + value[-4:]
                    else:
                        display = value
                    print(f"  {full_key} = {display}")

        print("📋 DeepProbe Configuration:")
        _print_dict(self._config)

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = self._deep_copy(DEFAULT_CONFIG)
        self.save()

    @property
    def config(self) -> dict:
        """Get full configuration dictionary."""
        return dict(self._config)
