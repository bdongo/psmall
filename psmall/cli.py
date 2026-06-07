"""Entry point and main loop for psmall.

Wires config -> scanner -> menu -> compressor. Ensures a home directory is set
on first run, then loops: scan, render menu, dispatch the chosen action, and
re-scan so just-finished albums show as done. Only Exit leaves the loop.
"""

from __future__ import annotations

import sys

from tqdm import tqdm

from . import config, menu
from .compressor import compress_album
from .scanner import Album, Status, scan


def _ensure_home() -> str | None:
    """Return a configured home dir, prompting on first run. None if cancelled."""
    home = config.get_home()
    if home:
        return home

    print("Welcome to psmall! First, tell me where your photo albums live.")
    chosen = menu.prompt_home_dir()
    if chosen is None:
        return None
    config.set_home(chosen)
    return chosen


def _run_one(album: Album) -> None:
    """Compress a single album with a progress bar."""
    print(f"\nCompressing '{album.name}' → {album.output_path}")
    bar = None
    for progress in compress_album(album):
        if bar is None:
            if progress.total == 0:
                print("  (no images found)")
                return
            bar = tqdm(total=progress.total, unit="img", leave=True)
        bar.update(1)
    if bar is not None:
        bar.close()
    print(f"  Done — originals untouched in {album.path}")


def _run_all_pending(albums: list[Album]) -> None:
    """Compress every pending album, skipping those already done."""
    pending = [a for a in albums if a.status is Status.PENDING]
    if not pending:
        print("Nothing pending — all albums are already compressed.")
        return
    print(f"\nCompressing {len(pending)} pending album(s)...")
    for album in pending:
        _run_one(album)
    print(f"\nAll done — {len(pending)} album(s) compressed.")


def _handle_settings() -> None:
    """Run the settings submenu loop."""
    while True:
        action = menu.settings_menu()
        if action == "change_home":
            current = config.get_home()
            chosen = menu.prompt_home_dir(current)
            if chosen is not None:
                config.set_home(chosen)
                print(f"Home directory set to: {chosen}")
        elif action == "back":
            return


def main() -> None:
    home = _ensure_home()
    if home is None:
        print("No home directory set. Exiting.")
        sys.exit(0)

    while True:
        albums = scan(home)
        if not albums:
            print(f"No albums found under {home}. Add some folders, or change "
                  f"the home directory in Settings.")

        action = menu.main_menu(albums)

        if action == menu.EXIT:
            print("Bye!")
            return
        elif action == menu.SETTINGS:
            _handle_settings()
            home = config.get_home()  # may have changed
        elif action == menu.ALL:
            _run_all_pending(albums)
        else:
            # action is an album path
            album = next((a for a in albums if a.path == action), None)
            if album is not None:
                _run_one(album)


if __name__ == "__main__":
    main()
