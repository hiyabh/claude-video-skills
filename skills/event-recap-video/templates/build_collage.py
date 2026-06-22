#!/usr/bin/env python3
"""Build the mandatory opening collage for the event-recap video.

The collage is a 5-photo asymmetric mosaic at 1920x1080:
  - Left half: 2x2 grid of 588x522 tiles (photos 1-4)
  - Right column: 696x1056 hero tile (photo 5 — portrait works best)
  - 12px white gaps between every tile

Selection rule — one photo per bucket:
  1. WIDE_CROWD       — wide establishing shot, shows the scale
  2. ACTIVITY         — busy/active scene with multiple interacting people
  3. JOY              — single hero portrait or strongest expression of joy
  4. GROUP_FACES      — group of smiling kids/faces (3+ subjects)
  5. HERO_PORTRAIT    — the iconic craft/artifact/closing image (PORTRAIT ratio)

Output filename: photo_collage<PHOTO_SUFFIX>.jpg so the build_video.py template
picks it up as shot 0 without extra wiring.

USAGE:
  1. Set BASE_DIR + PHOTO_SUFFIX
  2. Fill in the 5 photo filenames below
  3. Run: python build_collage.py
"""

import os
import subprocess
from pathlib import Path

# >>> EDIT THIS:
BASE_DIR = Path("./event-media")   # <-- set to your folder of photos+clips
PHOTO_SUFFIX = "_YYYY-MM-DD_HH-MM-SS"
os.chdir(BASE_DIR)

# >>> EDIT THESE 5 — one photo per bucket. All paths relative to BASE_DIR.
WIDE_CROWD    = f"photo_X{PHOTO_SUFFIX}.jpg"   # wide establishing
ACTIVITY      = f"photo_X{PHOTO_SUFFIX}.jpg"   # busy scene
JOY           = f"photo_X{PHOTO_SUFFIX}.jpg"   # joyful single hero face
GROUP_FACES   = f"photo_X{PHOTO_SUFFIX}.jpg"   # group of smiling faces
HERO_PORTRAIT = f"photo_X{PHOTO_SUFFIX}.jpg"   # portrait of iconic artifact

OUTPUT = f"photo_collage{PHOTO_SUFFIX}.jpg"

# Layout math (do not edit unless you also update the SKILL.md spec):
#   Canvas: 1920x1080
#   2x2 left tiles: w=588, h=522, gap=12px
#     top-left:    x=12,  y=12
#     top-right:   x=612, y=12
#     bot-left:    x=12,  y=546
#     bot-right:   x=612, y=546
#   Right hero column: w=696, h=1056, x=1212, y=12
FILTER = (
    "[1:v]scale=588:522:force_original_aspect_ratio=increase:flags=lanczos,crop=588:522[tl];"
    "[2:v]scale=588:522:force_original_aspect_ratio=increase:flags=lanczos,crop=588:522[tr];"
    "[3:v]scale=588:522:force_original_aspect_ratio=increase:flags=lanczos,crop=588:522[bl];"
    "[4:v]scale=588:522:force_original_aspect_ratio=increase:flags=lanczos,crop=588:522[br];"
    "[5:v]scale=696:1056:force_original_aspect_ratio=increase:flags=lanczos,crop=696:1056[hero];"
    "[0:v][tl]overlay=12:12[a];"
    "[a][tr]overlay=612:12[b];"
    "[b][bl]overlay=12:546[c];"
    "[c][br]overlay=612:546[d];"
    "[d][hero]overlay=1212:12[outv]"
)


def main():
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-t", "1", "-i", "color=c=white:s=1920x1080",
        "-i", WIDE_CROWD,
        "-i", ACTIVITY,
        "-i", JOY,
        "-i", GROUP_FACES,
        "-i", HERO_PORTRAIT,
        "-filter_complex", FILTER,
        "-map", "[outv]",
        "-frames:v", "1",
        "-q:v", "2",
        OUTPUT,
    ]
    print(">>>", " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-2000:])
        raise RuntimeError("Collage build failed")
    size = Path(OUTPUT).stat().st_size
    print(f"OK {OUTPUT} ({size:,} bytes)")


if __name__ == "__main__":
    main()
