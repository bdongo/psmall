"""Album scanner — discovers compressible albums under the home directory.

Lists one level of subdirectories, skips the `compressed_*` artifact folders
themselves, and tags each album as done or pending based on whether its
sibling output folder already holds compressed files.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum

COMPRESSED_PREFIX = "compressed_"

# Source formats psmall compresses. Lives here (not the compressor) so both the
# scanner's photo count and the compressor agree, without a circular import.
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


class Status(str, Enum):
    PENDING = "pending"
    DONE = "done"


@dataclass
class Album:
    name: str          # e.g. "2025 SF July"
    path: str          # absolute source directory
    status: Status
    output_path: str   # absolute "<home>/compressed_<name>"
    count: int         # number of compressible source images


def scan(home: str) -> list[Album]:
    """Return albums under `home`, sorted by name, with done/pending status."""
    home = os.path.abspath(os.path.expanduser(home))
    albums: list[Album] = []

    for name in sorted(os.listdir(home)):
        path = os.path.join(home, name)
        if not os.path.isdir(path):
            continue
        if name.startswith(COMPRESSED_PREFIX):
            continue  # this is an artifact folder, not a source album

        output_path = os.path.join(home, f"{COMPRESSED_PREFIX}{name}")
        status = Status.DONE if _is_done(output_path) else Status.PENDING
        albums.append(Album(name=name, path=path, status=status,
                            output_path=output_path, count=_count_images(path)))

    return albums


def _is_done(output_path: str) -> bool:
    """True if the output folder exists and contains at least one file."""
    return os.path.isdir(output_path) and len(os.listdir(output_path)) > 0


def _count_images(path: str) -> int:
    """Number of compressible source images directly in `path`."""
    return sum(1 for f in os.listdir(path)
               if f.lower().endswith(IMAGE_EXTENSIONS))
