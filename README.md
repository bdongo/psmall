# psmall

Interactive terminal tool for compressing photo albums to mobile-friendly HEIC.
Pick albums from an arrow-key menu, batch-process everything, and skip work
that's already done.

- **Compresses images** (`.jpg`, `.jpeg`, `.png`) to HEIC at quality 80,
  resized so the long edge is at most 2048px. EXIF metadata is preserved
  (e.g. Ricoh GR camera info).
- **Originals are never touched.** Each album's output lands in a sibling
  folder named `compressed_<album>` next to the source.
- **Tracks what's done.** An album counts as *done* once its
  `compressed_<album>` folder exists and isn't empty.
- **Only lists real albums.** Subfolders with no compressible images (empty
  folders, docs-only folders) are skipped, not shown.

## Install

Standalone app — **no Python required**. macOS, Apple Silicon (arm64).

Download and unzip the app, clear the macOS Gatekeeper quarantine, install the
folder under `/usr/local`, and symlink it onto your PATH so `psmall` works from
anywhere:

```bash
curl -L -o /tmp/psmall.zip https://github.com/bdongo/psmall/releases/latest/download/psmall-macos-arm64.zip
unzip -o /tmp/psmall.zip -d /tmp
xattr -dr com.apple.quarantine /tmp/psmall
sudo rm -rf /usr/local/psmall
sudo mv /tmp/psmall /usr/local/psmall
sudo ln -sf /usr/local/psmall/psmall /usr/local/bin/psmall
```

Then run it:

```bash
psmall
```

Notes:
- The app ships as a **folder** (the executable needs its bundled libraries
  beside it), so it installs to `/usr/local/psmall/` with a symlink at
  `/usr/local/bin/psmall`. Don't move the executable out of its folder on its
  own.
- These commands use absolute paths — run them from any directory.
- `sudo` is only needed for the `/usr/local` steps. `xattr -dr` clears the
  Gatekeeper quarantine for the unsigned app.
- **First launch is slow (a few seconds)** while macOS verifies the bundled
  libraries; every launch after that is instant.

Latest release: https://github.com/bdongo/psmall/releases/latest

Check your installed version with `psmall --version` and compare it against the
latest release above. To update, re-run the same commands — they replace your
install with the newest version.

## Using psmall

### First run

You'll be asked for your **photo home directory** — the parent folder that
holds your album subfolders. It's saved so you only set it once.

```
~/Documents/pictures/          <- home directory
├── 2025 SF July/              <- album (source)
├── 2024 Korea/                <- album (source)
├── compressed_2025 SF July/   <- output (created by psmall)
└── compressed_2024 Korea/     <- output (created by psmall)
```

### Main menu

A colored header shows where you are and what's left, then the album list —
**pending in yellow, done in green** — each with its photo count:

```
  psmall  · ~/Documents/pictures
  2 albums   1 pending   1 done

? Select an album to compress:
 » ▶ Compress all (skip done)  1 pending
   ──────────────
   ● pending  2025 SF July  (72 photos)
   ✓ done     2024 Korea    (58 photos)
   ──────────────
   ⚙  Settings
   ✕ Exit
```

- **Compress all (skip done)** — processes every pending album, printing a dim
  `↷ skipped` line for each already-done album. Disabled when nothing is pending.
- **An album** — compresses just that one (re-running a done album re-creates
  any missing files).
- **Settings → Change home directory** — point psmall at a different folder.
- **Exit** — quit. After any compression run, psmall re-scans and returns to
  this menu, so a just-finished album shows `✓ done`.

A corrupt or unreadable image is skipped (reported in red) rather than aborting
the album; the rest still compress.

### Config

Settings persist to `~/.config/psmall/config.json`:

```json
{
  "home": "/Users/you/Documents/pictures"
}
```

Delete this file to reset to first-run behavior.

---

## Development

Requires Python 3.9+. Set up an isolated environment and install editable:

```bash
git clone git@github.com:bdongo/psmall.git
cd psmall
python3 -m venv .venv
.venv/bin/pip install -e .
```

Run from the venv:

```bash
.venv/bin/psmall          # or: source .venv/bin/activate && psmall
```

### Layout

| File | Responsibility |
|---|---|
| `psmall/cli.py` | entry point + main loop |
| `psmall/config.py` | persisted home directory (`~/.config/psmall/config.json`) |
| `psmall/scanner.py` | album discovery + done/pending status |
| `psmall/compressor.py` | HEIC engine (resize, EXIF, encode) — UI-agnostic |
| `psmall/menu.py` | questionary arrow-key prompts |

Compression parameters are fixed in `psmall/compressor.py`: quality (`QUALITY`,
80), long edge (`LONG_EDGE`, 2048px), and accepted source formats (`VALID_EXT`).

### Building the binary

```bash
brew install upx                  # one-time
.venv/bin/pip install pyinstaller # one-time
./build.sh                        # -> dist/psmall/ + dist/psmall-macos-arm64.zip
```

`build.sh` bundles Python, Pillow, and `libheif` into a self-contained app.
It uses PyInstaller `--onedir` (a folder), not `--onefile`: a onefile binary
re-extracts to a temp dir on every launch, which makes macOS re-verify every
bundled library and adds several seconds to *each* startup. onedir keeps the
libraries at a stable path, so that cost is paid once and later launches start
in ~0.1s. The folder is zipped to `dist/psmall-macos-arm64.zip` for release
upload. The result is **Apple Silicon (arm64)** — build separately on an Intel
Mac for that architecture.

Run the built app with `./dist/psmall/psmall`.

### Cutting a release

One command bumps the version, commits + pushes, rebuilds the app, and
publishes a GitHub release with the zip attached:

```bash
./release.sh 0.2.0 "Add quality setting to the menu"
```

The message is optional (defaults to `Release v0.2.0`) and is used for both the
commit and the release notes. The script syncs the version in `pyproject.toml`
and `psmall/__init__.py`, and refuses to reuse an existing version.

The `psmall-macos-arm64.zip` attaches to the release as a downloadable asset;
the source repo never stores it (`dist/` is gitignored).
