"""Interactive prompts — thin wrappers around questionary.

Returns action tokens to cli.py; holds no business logic. Album entries are
labelled with their status so the user sees done vs. pending at selection time.
"""

from __future__ import annotations

import os

import questionary

from .scanner import Album, Status

# Sentinel action tokens returned by main_menu (besides an album path).
ALL = "all"
SETTINGS = "settings"
EXIT = "exit"


def _album_label(album: Album) -> str:
    marker = "✓ done   " if album.status is Status.DONE else "• pending"
    return f"[{marker}] {album.name}"


def main_menu(albums: list[Album]) -> str:
    """Show the main menu. Returns ALL | SETTINGS | EXIT | an album path."""
    pending = sum(1 for a in albums if a.status is Status.PENDING)

    choices = [
        questionary.Choice(
            title=f"Compress all (skip done) — {pending} pending",
            value=ALL,
            disabled=None if pending else "nothing pending",
        ),
        questionary.Separator(),
    ]
    for album in albums:
        choices.append(questionary.Choice(title=_album_label(album),
                                          value=album.path))
    choices += [
        questionary.Separator(),
        questionary.Choice(title="⚙  Settings", value=SETTINGS),
        questionary.Choice(title="Exit", value=EXIT),
    ]

    answer = questionary.select("Select an album to compress:",
                                choices=choices).ask()
    # ask() returns None on Ctrl-C / Esc — treat as exit.
    return answer if answer is not None else EXIT


def settings_menu() -> str:
    """Settings submenu. Returns 'change_home' | 'back'."""
    answer = questionary.select(
        "Settings:",
        choices=[
            questionary.Choice(title="Change home directory", value="change_home"),
            questionary.Choice(title="← Back", value="back"),
        ],
    ).ask()
    return answer if answer is not None else "back"


def prompt_home_dir(current: str | None = None) -> str | None:
    """Prompt for a home directory, validating that it exists.

    Returns the validated absolute path, or None if the user cancels.
    """
    def validate(text: str) -> bool | str:
        path = os.path.abspath(os.path.expanduser(text.strip()))
        return True if os.path.isdir(path) else "Not a directory"

    answer = questionary.path(
        "Photo home directory:",
        default=current or "",
        validate=validate,
        only_directories=True,
    ).ask()
    if answer is None:
        return None
    return os.path.abspath(os.path.expanduser(answer.strip()))
