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

## Install

Download the standalone binary — **no Python required**. macOS, Apple Silicon
(arm64).

```bash
curl -L -o psmall https://github.com/bdongo/psmall/releases/latest/download/psmall
chmod +x psmall
xattr -d com.apple.quarantine psmall   # clear Gatekeeper (first run only)
./psmall
```

To run it from anywhere, move it onto your PATH:

```bash
mv psmall /usr/local/bin/
```

Latest release: https://github.com/bdongo/psmall/releases/latest

## Using psmall

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
./build.sh                        # -> dist/psmall (~14MB, UPX-compressed)
```

`build.sh` bundles Python, Pillow, and `libheif` into one self-contained file.
The result is **Apple Silicon (arm64)** — build separately on an Intel Mac for
that architecture.

### Cutting a release

```bash
git add -A && git commit -m "..." && git push
./build.sh
gh release create vX.Y.Z dist/psmall --title "psmall vX.Y.Z" --notes "..."
```

The binary attaches to the release as a downloadable asset; the source repo
never stores it (`dist/` is gitignored).
