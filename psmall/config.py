"""Persisted configuration store for psmall.

Single source of truth for "where are my photos." Settings live in a JSON
file under the user's config directory so the home directory survives between
runs.
"""

from __future__ import annotations

import json
import os

CONFIG_PATH = os.path.expanduser("~/.config/psmall/config.json")


def load() -> dict:
    """Return the stored config, or an empty dict if none exists yet."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupt or unreadable config — start fresh rather than crash.
        return {}


def save(cfg: dict) -> None:
    """Write config to disk, creating the parent directory if needed."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def get_home() -> str | None:
    """Return the configured home directory, or None if unset."""
    return load().get("home")


def set_home(path: str) -> None:
    """Validate and store the home directory as an absolute path."""
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a directory: {path}")
    cfg = load()
    cfg["home"] = path
    save(cfg)
