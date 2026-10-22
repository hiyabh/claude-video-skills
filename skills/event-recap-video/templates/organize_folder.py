#!/usr/bin/env python3
"""FINAL tidy step — sort the project folder after the recap video is delivered.

Run this LAST, once the final muxed video is verified. It sorts loose files into
subfolders and leaves only the deliverable + its collage in the root:

  <root>/
    01 - <event>.mp4            <- the finished recap video     (stays in root)
    01 - <event> (ווטסאפ).mp4    <- the WhatsApp-light copy       (stays in root)
    photo_collage<SUFFIX>.jpg    <- the titled opening collage    (stays in root)
    פרסום.jpeg                   <- the event flyer/promo         (stays in root)
    תמונות גלם/                  <- all source photos
    סרטוני גלם/                  <- all source video clips
    סקריפטים/                    <- build_*.py, add_collage_title.py, this file, logos

Notes:
  - Idempotent: safe to re-run; already-sorted files are skipped.
  - After sorting, re-running the build scripts needs the photos/clips back in root
    (they use relative paths). That's fine — organization is a post-delivery step.
"""

import os
import shutil
from pathlib import Path

# >>> EDIT per event:
BASE_DIR = Path("./event-media")   # <-- set to your folder of photos+clips
FINAL_VIDEO = "01 - <event-name>.mp4"   # exact filename of the deliverable to KEEP in root
os.chdir(BASE_DIR)

# Folder names (Hebrew by default — rename if you prefer English)
DIR_PHOTOS  = "תמונות גלם"
DIR_VIDEOS  = "סרטוני גלם"
DIR_SCRIPTS = "סקריפטים"

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".gif"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}
THIS_FILE = Path(__file__).name


def is_logo(name: str) -> bool:
    n = name.lower()
    return "logo" in n or "לוגו" in name


# Keywords that keep a file in root: flyer/promo, and the WhatsApp-light export.
# NOTE: no English "whatsapp" here on purpose — raw WhatsApp-exported clips are
# named "WhatsApp Video/Image ..." and must NOT stay in root. The light export
# uses the Hebrew "ווטסאפ" suffix, which is the keyword that keeps it in root.
# "גרסה" keeps alternate music versions ("גרסה ב - ...mp4") next to the deliverable.
ROOT_KEYS = ("פרסום", "פלאייר", "flyer", "ווטסאפ", "גרסה")


def keep_in_root(name: str) -> bool:
    # Deliverable, titled collage, flyer/promo, and WhatsApp-light copy stay in root.
    if name == FINAL_VIDEO or name.startswith("photo_collage"):
        return True
    low = name.lower()
    return any(k in name or k in low for k in ROOT_KEYS)


def main():
    for d in (DIR_PHOTOS, DIR_VIDEOS, DIR_SCRIPTS):
        Path(d).mkdir(exist_ok=True)

    moved = {"photos": 0, "videos": 0, "scripts": 0}
    for p in sorted(Path(".").iterdir()):
        if p.is_dir() or keep_in_root(p.name):
            continue
        name = p.name
        ext = p.suffix.lower()

        # Scripts + build assets (python files, this organizer, logo images)
        if ext in {".py", ".m4a"} or is_logo(name):   # build assets incl. the kept music track(s)
            dest = DIR_SCRIPTS
            key = "scripts"
        elif ext in VIDEO_EXT:
            dest = DIR_VIDEOS
            key = "videos"
        elif ext in IMAGE_EXT:
            dest = DIR_PHOTOS
            key = "photos"
        else:
            continue  # leave anything unrecognized in the root

        target = Path(dest) / name
        if target.exists():
            target.unlink()
        shutil.move(name, str(target))
        moved[key] += 1

    print(f"OK organized -> {DIR_PHOTOS}: {moved['photos']} | "
          f"{DIR_VIDEOS}: {moved['videos']} | {DIR_SCRIPTS}: {moved['scripts']}")
    print(f"Kept in root: {FINAL_VIDEO} + photo_collage*.jpg")


if __name__ == "__main__":
    main()
