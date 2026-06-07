"""Compression engine — UI-agnostic work, lifted from the original notebook.

Converts each source image to a resized HEIC in the album's sibling output
folder, preserving EXIF. Yields Progress after each file so the caller decides
how to render it. The caller is responsible for skip decisions (via
Album.status); _is_done logic lives in the scanner.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator

from PIL import Image
from pillow_heif import register_heif_opener

from .scanner import Album, COMPRESSED_PREFIX

# Enable HEIF read/write support in Pillow.
register_heif_opener()

VALID_EXT = (".jpg", ".jpeg", ".png")
LONG_EDGE = 2048
QUALITY = 80


@dataclass
class Progress:
    done: int
    total: int


def _image_files(input_dir: str) -> list[str]:
    """Return image filenames in input_dir matching VALID_EXT."""
    return [
        f for f in sorted(os.listdir(input_dir))
        if f.lower().endswith(VALID_EXT)
    ]


def compress_album(album: Album,
                   long_edge: int = LONG_EDGE,
                   quality: int = QUALITY) -> Iterator[Progress]:
    """Compress every image in `album`, yielding Progress after each file.

    Creates the output folder if needed. Originals are never touched.
    """
    os.makedirs(album.output_path, exist_ok=True)

    files = _image_files(album.path)
    total = len(files)

    for i, filename in enumerate(files, start=1):
        input_path = os.path.join(album.path, filename)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{COMPRESSED_PREFIX}{base_name}.heic"
        output_path = os.path.join(album.output_path, output_filename)

        with Image.open(input_path) as img:
            exif_data = img.info.get("exif")

            width, height = img.size
            if max(width, height) > long_edge:
                ratio = long_edge / max(width, height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            save_kwargs = {"quality": quality}
            if exif_data:
                save_kwargs["exif"] = exif_data
            img.save(output_path, "HEIF", **save_kwargs)

        yield Progress(done=i, total=total)
