#!/usr/bin/env bash
#
# Build a self-contained `psmall` app with PyInstaller, compressed with UPX,
# and zip it for distribution. Needs no Python, pip, or venv on the target.
#
# Uses --onedir (not --onefile): onefile re-extracts to a temp dir on every
# launch, which makes macOS re-verify every bundled dylib's signature and adds
# ~4.5s to EACH startup. onedir keeps the libraries at a stable path, so that
# verification happens once and later launches start in ~0.1s.
#
# Output:
#   dist/psmall/                  the app folder (executable + _internal libs)
#   dist/psmall-macos-arm64.zip   the same folder, zipped for release upload
#
# Usage: ./build.sh
#
set -euo pipefail

cd "$(dirname "$0")"

PY=.venv/bin/python
UPX_DIR="$(brew --prefix 2>/dev/null)/bin"
ZIP_NAME="psmall-macos-arm64.zip"

# Clean previous build output so size/timestamps are honest.
rm -rf build dist psmall.spec

"$PY" -m PyInstaller \
  --onedir \
  --name psmall \
  --collect-all pillow_heif \
  --collect-all PIL \
  --upx-dir "$UPX_DIR" \
  psmall/__main__.py

# Zip the app folder for distribution (the binary needs _internal beside it,
# so we ship the whole folder, not just the executable).
(cd dist && zip -qr "$ZIP_NAME" psmall)

echo
echo "Built: dist/psmall/ ($(du -sh dist/psmall | cut -f1) folder)"
echo "       dist/$ZIP_NAME ($(du -h "dist/$ZIP_NAME" | cut -f1) for release)"
echo "Run it with:  ./dist/psmall/psmall"
