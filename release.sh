#!/usr/bin/env bash
#
# Cut a new release: bump version, commit + push source, build the binary,
# and publish a GitHub release with the binary attached.
#
# Usage:
#   ./release.sh <version> [message]
#
# Examples:
#   ./release.sh 0.2.0
#   ./release.sh v0.2.0 "Add quality setting to the menu"
#
# The message (optional) is used as both the commit message and the release
# notes. If omitted, "Release <version>" is used.
#
set -euo pipefail

cd "$(dirname "$0")"

# --- args ---------------------------------------------------------------
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: ./release.sh <version> [message]"
  echo "Example: ./release.sh 0.2.0 \"Add quality setting\""
  exit 1
fi
# Normalize to a v-prefixed tag (v0.2.0) and a bare version (0.2.0).
VERSION="v${VERSION#v}"
BARE="${VERSION#v}"
MESSAGE="${2:-Release $VERSION}"

# --- preflight ----------------------------------------------------------
if ! command -v gh >/dev/null; then
  echo "error: gh CLI not found (brew install gh)"; exit 1
fi
if git rev-parse "$VERSION" >/dev/null 2>&1; then
  echo "error: tag $VERSION already exists — pick a new version."; exit 1
fi
if gh release view "$VERSION" >/dev/null 2>&1; then
  echo "error: release $VERSION already exists on GitHub."; exit 1
fi

# --- 1. sync version in source -----------------------------------------
sed -i '' -E "s/^version = \".*\"/version = \"$BARE\"/" pyproject.toml
sed -i '' -E "s/^__version__ = \".*\"/__version__ = \"$BARE\"/" psmall/__init__.py

# --- 2. commit + push ---------------------------------------------------
git add -A
if git diff --cached --quiet; then
  echo "No source changes to commit."
else
  git commit -m "$MESSAGE"
fi
git push origin main

# --- 3. build the binary ------------------------------------------------
./build.sh

# --- 4. publish the release ---------------------------------------------
gh release create "$VERSION" dist/psmall \
  --title "psmall $VERSION" \
  --notes "$MESSAGE"

echo
echo "Released $VERSION → https://github.com/bdongo/psmall/releases/tag/$VERSION"
