#!/usr/bin/env bash
# Build ONE seamless live-background video from the Veo clips for the live version.
#
# Steps per clip: slow to fill the song (smooth, motion-interpolated) + upscale to
# 1080x1920, then concat (seamless hard cuts — clip boundaries already match).
#
# Pitfalls learned:
#  - ffmpeg on Windows can't open MSYS "/c/..." paths in a concat list. Write the
#    list with paths RELATIVE TO THE LIST FILE'S directory (entries like
#    "proc/clip_01.mp4", list at assets/video/, run ffmpeg from the project root).
#  - Pad the end (+0.8s hold) so the bg is slightly LONGER than the song; otherwise
#    the last fraction of a second freezes/goes black.
#
# Usage: edit FACTOR for your song length, then:  bash build_background.sh
set -e
cd "$(dirname "$0")/.."          # project root

# FACTOR = target_total_seconds / (num_clips * clip_seconds).
# e.g. 8 clips x 8s = 64s native; song ~100s -> FACTOR ~1.58.
FACTOR=1.580

mkdir -p assets/video/proc
for f in assets/video/clip_0*.mp4; do
  base=$(basename "$f" .mp4)
  echo "processing $base ..."
  ffmpeg -v error -i "$f" \
    -vf "setpts=${FACTOR}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc,scale=1080:1920" \
    -an -c:v libx264 -crf 19 -preset medium -pix_fmt yuv420p "assets/video/proc/${base}_proc.mp4" -y
done

echo "concatenating..."
: > assets/video/concat_list.txt
for f in assets/video/proc/clip_0*_proc.mp4; do
  echo "file 'proc/$(basename "$f")'" >> assets/video/concat_list.txt
done
ffmpeg -v error -f concat -safe 0 -i assets/video/concat_list.txt \
  -c:v libx264 -crf 19 -preset medium -pix_fmt yuv420p assets/background_raw.mp4 -y

echo "padding end (+0.8s hold) so it covers the full song..."
ffmpeg -v error -i assets/background_raw.mp4 \
  -vf "tpad=stop_mode=clone:stop_duration=0.8" \
  -c:v libx264 -crf 19 -preset medium -pix_fmt yuv420p assets/background.mp4 -y
rm -f assets/background_raw.mp4

echo "DONE → assets/background.mp4"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 assets/background.mp4
