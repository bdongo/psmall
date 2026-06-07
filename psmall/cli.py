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
from .theme import CYAN, DIM, GREEN, MAGENTA, RED, YELLOW, paint


def _print_header(home: str, albums: list[Album]) -> None:
    """Print the colored context banner shown above the menu each loop."""
    total = len(albums)
    pending = sum(1 for a in albums if a.status is Status.PENDING)
    new = sum(1 for a in albums if a.status is Status.NEW_PENDING)
    done = sum(1 for a in albums if a.status is Status.DONE)

    parts = [paint(f"{total} albums", DIM)]
    if pending:
        parts.append(paint(f"{pending} pending", YELLOW))
    if new:
        parts.append(paint(f"{new} new", MAGENTA))
    if done:
        parts.append(paint(f"{done} done", GREEN))

    print()
    print(f"  {paint('psmall', CYAN)}  {paint('· ' + home, DIM)}")
    print("  " + "   ".join(parts))


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


def _run_one(album: Album, skip_existing: bool = True) -> None:
    """Compress a single album with a progress bar.

    With skip_existing=True (default) only new photos are compressed; pass
    False to force a full re-compress that overwrites existing output.
    """
    print(f"\n{paint('Compressing', CYAN)} {album.name} "
          f"{paint('→ ' + album.output_path, DIM)}")
    bar = None
    last = None
    for progress in compress_album(album, skip_existing=skip_existing):
        last = progress
        if bar is None:
            if progress.total == 0:
                print(f"  {paint('Nothing to do — already up to date.', DIM)}")
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
    """Compress pending + new albums; skip (and note) those already done."""
    todo = [a for a in albums if a.status is not Status.DONE]
    done = [a for a in albums if a.status is Status.DONE]

    for album in done:
        print(f"  {paint('↷ skipped', DIM)} {paint(album.name + ' (done)', DIM)}")

    if not todo:
        print(f"\n{paint('Nothing to do', YELLOW)} — all albums are already compressed.")
        return
    print(f"\n{paint('Compressing', CYAN)} {len(todo)} album(s)...")
    for album in todo:
        _run_one(album)  # skip_existing=True: new photos only for NEW_PENDING
    print(f"\n{paint(f'✓ All done — {len(todo)} album(s) compressed.', GREEN)}")


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
            if album is None:
                continue
            if album.status is Status.DONE:
                # Already done — confirm before overwriting everything.
                if menu.confirm_recompress(album):
                    _run_one(album, skip_existing=False)
            else:
                # PENDING compresses all; NEW_PENDING compresses only new photos.
                _run_one(album)


if __name__ == "__main__":
    main()
