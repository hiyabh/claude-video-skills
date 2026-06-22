#!/usr/bin/env bash
# universal-downloader helper
# Usage: ./download.sh <URL> [video|audio|playlist|subs|file|images]
# Default mode: video

set -e

URL="${1:-}"
MODE="${2:-video}"
ROOT="${HOME}/Downloads/web"
ARCHIVE="${ROOT}/.archive.txt"

if [[ -z "$URL" ]]; then
  echo "Usage: $0 <URL> [video|audio|playlist|subs|file|images]"
  exit 1
fi

mkdir -p "$ROOT/$MODE"
cd "$ROOT/$MODE"

case "$MODE" in
  video)
    yt-dlp --no-check-certificates \
      -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
      --merge-output-format mp4 \
      -o "%(title).200B [%(id)s].%(ext)s" \
      --download-archive "$ARCHIVE" \
      "$URL"
    ;;
  audio)
    yt-dlp --no-check-certificates \
      -x --audio-format mp3 --audio-quality 0 \
      -o "%(title).200B [%(id)s].%(ext)s" \
      --download-archive "$ARCHIVE" \
      "$URL"
    ;;
  playlist)
    yt-dlp --no-check-certificates \
      -o "%(playlist_title)s/%(playlist_index)03d - %(title).150B [%(id)s].%(ext)s" \
      --download-archive "$ARCHIVE" \
      --yes-playlist \
      "$URL"
    ;;
  subs)
    yt-dlp --no-check-certificates \
      --write-subs --write-auto-subs --sub-langs "he,en.*,iw" \
      --convert-subs srt --skip-download \
      -o "%(title).200B [%(id)s].%(ext)s" \
      "$URL"
    ;;
  file)
    curl -L -O --insecure --retry 5 --retry-delay 2 \
      -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
      "$URL"
    ;;
  images)
    command -v gallery-dl >/dev/null 2>&1 || { echo "gallery-dl missing. pip install --user gallery-dl"; exit 2; }
    gallery-dl --no-check-certificate "$URL"
    ;;
  *)
    echo "Unknown mode: $MODE"
    exit 3
    ;;
esac

echo ""
echo "=== Saved to: $ROOT/$MODE/ ==="
ls -lh "$ROOT/$MODE/" | tail -5
