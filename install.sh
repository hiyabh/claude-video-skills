#!/usr/bin/env bash
# Installer for the "בין קודש לקלוד" Claude Code video-skills bundle.
# Usage:  curl -L https://hiyabh.github.io/claude-video-skills/install.sh | bash
set -euo pipefail

BUNDLE_URL="https://hiyabh.github.io/claude-video-skills/claude-video-skills.tar.gz"
SKILLS_DIR="${HOME}/.claude/skills"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "==> Installing Claude Code video skills into: $SKILLS_DIR"
mkdir -p "$SKILLS_DIR"

echo "==> Downloading bundle..."
if command -v curl >/dev/null 2>&1; then
  curl -fL -o "$TMP/bundle.tar.gz" "$BUNDLE_URL"
elif command -v wget >/dev/null 2>&1; then
  wget -O "$TMP/bundle.tar.gz" "$BUNDLE_URL"
else
  echo "ERROR: need curl or wget." >&2; exit 1
fi

echo "==> Extracting..."
mkdir -p "$TMP/x"
tar -xzf "$TMP/bundle.tar.gz" -C "$TMP/x"
# bundle root is "skills/" — copy each skill folder
SRC="$TMP/x/skills"
[ -d "$SRC" ] || SRC="$(find "$TMP/x" -maxdepth 2 -type d -name skills | head -n1)"

installed=0; skipped=0
for d in "$SRC"/*/; do
  name="$(basename "$d")"
  dest="$SKILLS_DIR/$name"
  if [ -e "$dest" ]; then
    echo "   skip (already exists): $name"
    skipped=$((skipped+1))
  else
    cp -r "$d" "$dest"
    echo "   installed: $name"
    installed=$((installed+1))
  fi
done

echo ""
echo "==> Done. Installed: $installed, skipped (already present): $skipped"
echo "==> Restart Claude Code so it picks up the new skills."
echo ""
echo "Prerequisites you may still need: Node.js 22+, FFmpeg, Python 3.9+"
echo "(AI image/video skills also need GOOGLE_API_KEY as an env var)."
