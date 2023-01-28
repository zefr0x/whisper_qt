"""Function to get default XDG directories."""
from os import environ
from pathlib import Path

from .__about__ import APP_NAME


def xdg_cache_dir() -> Path:
    """XDG base cache directory."""
    xdg_cache_home = Path(environ.get("XDG_CACHE_HOME", "")) or Path.home().joinpath(
        ".cache"
    )

    return xdg_cache_home / APP_NAME


def xdg_config_file() -> Path:
    """XDG base config directory."""
    xdg_config_home = Path(environ.get("XDG_CONFIG_HOME", "")) or Path.home().joinpath(
        ".config"
    )

    return xdg_config_home / APP_NAME / "config"
