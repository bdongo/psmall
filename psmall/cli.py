"""Entry point and main loop for psmall.

Wires config -> scanner -> menu -> compressor. Ensures a home directory is set
on first run, then loops: scan, render menu, dispatch the chosen action, and
re-scan so just-finished albums show as done. Only Exit leaves the loop.
"""

from __future__ import annotations

import argparse
import sys

from tqdm import tqdm

from . import __version__, config, menu
from .compressor import compress_album
from .scanner import Album, Status, scan
from .theme import CYAN, DIM, GREEN, RED, YELLOW, paint


def _print_header(home: str, albums: list[Album]) -> None:
    """Print the colored context banner shown above the menu each loop."""
    total = len(albums)
    done = sum(1 for a in albums if a.status is Status.DONE)
    pending = total - done
    print()
    print(f"  {paint('psmall', CYAN)}  {paint('· ' + home, DIM)}")
    print(f"  {paint(f'{total} albums', DIM)}   "
          f"{paint(f'{pending} pending', YELLOW)}   "
          f"{paint(f'{done} done', GREEN)}")


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
    print(f"\n{paint('Compressing', CYAN)} {album.name} "
          f"{paint('→ ' + album.output_path, DIM)}")
    bar = None
    last = None
    for progress in compress_album(album):
        last = progress
        if bar is None:
            if progress.total == 0:
                print(f"  {paint('(no images found)', DIM)}")
                return
            bar = tqdm(total=progress.total, unit="img", leave=True, colour="green")
        bar.update(1)
    if bar is not None:
        bar.close()

    if last and last.failed:
        ok = last.total - last.failed
        print(f"  {paint(f'✓ {ok} compressed', GREEN)}, "
              f"{paint(f'✗ {last.failed} failed', RED)} "
              f"{paint('— ' + last.last_error, DIM)}")
    else:
        print(f"  {paint('✓ Done', GREEN)} "
              f"{paint('— originals untouched in ' + album.path, DIM)}")


def _run_all_pending(albums: list[Album]) -> None:
    """Compress every pending album, noting those skipped because they're done."""
    pending = [a for a in albums if a.status is Status.PENDING]
    done = [a for a in albums if a.status is Status.DONE]

    for album in done:
        print(f"  {paint('↷ skipped', DIM)} {paint(album.name + ' (done)', DIM)}")

    if not pending:
        print(f"\n{paint('Nothing pending', YELLOW)} — all albums are already compressed.")
        return
    print(f"\n{paint('Compressing', CYAN)} {len(pending)} pending album(s)...")
    for album in pending:
        _run_one(album)
    print(f"\n{paint(f'✓ All done — {len(pending)} album(s) compressed.', GREEN)}")


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
    parser = argparse.ArgumentParser(
        prog="psmall",
        description="Interactive HEIC photo compression for your album folders.",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"psmall {__version__}",
    )
    parser.parse_args()

    home = _ensure_home()
    if home is None:
        print("No home directory set. Exiting.")
        sys.exit(0)

    while True:
        albums = scan(home)
        _print_header(home, albums)
        if not albums:
            print(f"  {paint('No albums found here.', YELLOW)} Add some folders, "
                  f"or change the home directory in Settings.")

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
