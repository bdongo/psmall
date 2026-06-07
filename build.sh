#!/usr/bin/env bash
#
# Build a single-file, self-contained `psmall` binary with PyInstaller,
# compressed with UPX. The result lands in dist/psmall and needs no Python,
# pip, or venv on the target machine.
#
# Usage: ./build.sh
#
set -euo pipefail

cd "$(dirname "$0")"

PY=.venv/bin/python
UPX_DIR="$(brew --prefix 2>/dev/null)/bin"

# Clean previous build output so size/timestamps are honest.
rm -rf build dist psmall.spec

"$PY" -m PyInstaller \
  --onefile \
  --name psmall \
  --collect-all pillow_heif \
  --collect-all PIL \
  --upx-dir "$UPX_DIR" \
  psmall/__main__.py

echo
echo "Built: dist/psmall ($(du -h dist/psmall | cut -f1))"
echo "Run it with:  ./dist/psmall"
