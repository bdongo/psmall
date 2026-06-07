"""Terminal colors and the questionary prompt style, in one place.

Two styling systems live here because the tool uses two rendering paths:
- ANSI escape codes for plain `print()` output (header, progress, summaries).
- A questionary/prompt_toolkit Style for the interactive menus.

Status colors are shared in spirit: pending is yellow, done is green.
"""

from __future__ import annotations

import questionary

# --- ANSI codes for plain print() output --------------------------------
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[90m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"


def paint(text: str, *codes: str) -> str:
    """Wrap text in the given ANSI codes, resetting afterwards."""
    return "".join(codes) + text + RESET


# --- questionary (prompt_toolkit) style for interactive menus -----------
# Class names map to selectors used in Choice titles and the select widget.
STYLE = questionary.Style([
    ("qmark", "fg:ansicyan bold"),
    ("question", "bold"),
    ("pointer", "fg:ansicyan bold"),
    ("highlighted", "fg:ansicyan bold"),
    ("selected", "fg:ansicyan"),
    ("separator", "fg:ansibrightblack"),
    ("instruction", "fg:ansibrightblack"),
    ("disabled", "fg:ansibrightblack italic"),
    # custom classes used inside Choice titles
    ("done", "fg:ansigreen bold"),
    ("pending", "fg:ansiyellow bold"),
    ("new", "fg:ansimagenta bold"),
    ("action", "fg:ansicyan bold"),
    ("dim", "fg:ansibrightblack"),
])
