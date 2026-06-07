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

from .scanner import Album, COMPRESSED_PREFIX, IMAGE_EXTENSIONS

# Enable HEIF read/write support in Pillow.
register_heif_opener()

LONG_EDGE = 2048
QUALITY = 80


@dataclass
class Progress:
    done: int            # files attempted so far
    total: int           # files to process
    failed: int = 0      # files that errored and were skipped
    last_error: str = ""  # message for the most recent failure, if any


def _image_files(input_dir: str) -> list[str]:
    """Return image filenames in input_dir matching IMAGE_EXTENSIONS."""
    return [
        f for f in sorted(os.listdir(input_dir))
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ]


def compress_album(album: Album,
                   long_edge: int = LONG_EDGE,
                   quality: int = QUALITY) -> Iterator[Progress]:
    """Compress every image in `album`, yielding Progress after each file.

    Creates the output folder if needed. Originals are never touched. A file
    that fails to convert (e.g. corrupt) is skipped and counted in
    Progress.failed rather than aborting the whole album.
    """
    os.makedirs(album.output_path, exist_ok=True)

    files = _image_files(album.path)
    total = len(files)
    failed = 0
    last_error = ""

    for i, filename in enumerate(files, start=1):
        input_path = os.path.join(album.path, filename)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{COMPRESSED_PREFIX}{base_name}.heic"
        output_path = os.path.join(album.output_path, output_filename)

        try:
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
        except Exception as exc:  # corrupt/unreadable image — skip, keep going
            failed += 1
            last_error = f"{filename}: {exc}"

        yield Progress(done=i, total=total, failed=failed, last_error=last_error)
