# psmall

Interactive terminal tool for compressing photo albums to mobile-friendly HEIC.
Wraps the original compression notebook in an arrow-key menu so you can pick
albums, batch-process everything, and skip work that's already done.

## What it does

- **Compresses images** (`.jpg`, `.jpeg`, `.png`) to HEIC at quality 80,
  resized so the long edge is at most 2048px. EXIF metadata is preserved
  (e.g. Ricoh GR camera info).
- **Originals are never touched.** Each album's output lands in a sibling
  folder named `compressed_<album>` next to the source.
- **Tracks what's done.** An album counts as *done* once its
  `compressed_<album>` folder exists and isn't empty.

## Install

Only Python 3.9 was available on this machine, so the project lives in an
isolated virtual environment:

```bash
cd /Users/brandon/Documents/image_compression
python3 -m venv .venv          # if not already created
.venv/bin/pip install -e .
```

## Usage

```bash
.venv/bin/psmall
```

Or activate the environment first to use `psmall` as a bare command:

```bash
source .venv/bin/activate
psmall
```

## Standalone binary (no Python required)

To produce a single self-contained executable that runs on a Mac with no
Python, pip, or venv installed:

```bash
./build.sh          # needs PyInstaller (in .venv) and upx (brew install upx)
```

This writes `dist/psmall` — a ~13MB binary with Python, Pillow, and `libheif`
all bundled in (compressed with UPX). Copy it anywhere on the target machine:

```bash
cp dist/psmall /usr/local/bin/psmall    # now `psmall` works globally
```

Notes:
- The binary is **Apple Silicon (arm64)**; build separately on an Intel Mac
  for that architecture.
- First launch on another machine may hit macOS Gatekeeper
  (*"unidentified developer"*). Clear it once with:
  ```bash
  xattr -d com.apple.quarantine /path/to/psmall
  ```

### First run

You'll be asked for your **photo home directory** — the parent folder that
holds your album subfolders. It's saved so you only set it once.

```
~/Documents/pictures/          <- home directory
├── 2025 SF July/              <- album (source)
├── 2024 Tokyo/                <- album (source)
├── compressed_2025 SF July/   <- output (created by psmall)
└── compressed_2024 Tokyo/     <- output (created by psmall)
```

### Main menu

```
Select an album to compress:
  Compress all (skip done) — 1 pending
  ──────────────
  [• pending] 2025 SF July
  [✓ done   ] 2024 Tokyo
  ──────────────
  ⚙  Settings
  Exit
```

- **Compress all (skip done)** — processes every pending album, skipping any
  already compressed. Disabled when nothing is pending.
- **An album** — compresses just that one (re-running a done album re-creates
  any missing files).
- **Settings → Change home directory** — point psmall at a different folder.
- **Exit** — quit. After any compression run, psmall re-scans and returns to
  this menu, so a just-finished album shows `✓ done`.

## Config

Settings persist to `~/.config/psmall/config.json`:

```json
{
  "home": "/Users/you/Documents/pictures"
}
```

Delete this file to reset to first-run behavior.

## Compression settings

Quality (80) and long edge (2048px) are fixed in `psmall/compressor.py`
(`QUALITY`, `LONG_EDGE`) for this version. Source formats handled are listed
in `VALID_EXT`.
