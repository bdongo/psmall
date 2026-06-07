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
    PENDING = "pending"          # never compressed
    NEW_PENDING = "new_pending"  # compressed, but source has new images
    DONE = "done"                # fully compressed


@dataclass
class Album:
    name: str             # e.g. "2025 SF July"
    path: str             # absolute source directory
    status: Status
    output_path: str      # absolute "<home>/compressed_<name>"
    count: int            # number of compressible source images
    compressed_count: int  # number of files already in the output folder

    @property
    def new_count(self) -> int:
        """How many source images have no output yet (>=0)."""
        return max(0, self.count - self.compressed_count)


def scan(home: str) -> list[Album]:
    """Return albums under `home`, sorted by name, with their status."""
    home = os.path.abspath(os.path.expanduser(home))
    albums: list[Album] = []

    for name in sorted(os.listdir(home)):
        path = os.path.join(home, name)
        if not os.path.isdir(path):
            continue
        if name.startswith(COMPRESSED_PREFIX):
            continue  # this is an artifact folder, not a source album

        count = _count_images(path)
        if count == 0:
            continue  # no compressible images here — not an album

        output_path = os.path.join(home, f"{COMPRESSED_PREFIX}{name}")
        compressed_count = _count_output(output_path)
        if compressed_count == 0:
            status = Status.PENDING
        elif count > compressed_count:
            status = Status.NEW_PENDING  # new source images added since last run
        else:
            status = Status.DONE
        albums.append(Album(name=name, path=path, status=status,
                            output_path=output_path, count=count,
                            compressed_count=compressed_count))

    return albums


def _count_images(path: str) -> int:
    """Number of compressible source images directly in `path`."""
    return sum(1 for f in os.listdir(path)
               if f.lower().endswith(IMAGE_EXTENSIONS))


def _count_output(output_path: str) -> int:
    """Number of files in the output folder (0 if it doesn't exist)."""
    if not os.path.isdir(output_path):
        return 0
    return sum(1 for f in os.listdir(output_path)
               if not f.startswith("."))
