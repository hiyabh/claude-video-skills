# -*- coding: utf-8 -*-
"""Composite transparent lower-third webm overlays onto their segments."""
import os
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

SEGS = os.path.join("work", "segments")
GFX = os.path.join("gfx", "renders")
OUT = os.path.join("work", "titled")
os.makedirs(OUT, exist_ok=True)

# segment file -> overlay webm
PAIRS = [   # EDIT: one row per segment that needs a name lower-third
    ("seg_03_A1.mp4", "lt_p1.webm"),
    ("seg_04_B1.mp4", "lt_p2.webm"),
    ("seg_05_C1.mp4", "lt_p3.webm"),
    ("seg_06_D1.mp4", "lt_p4.webm"),
    ("seg_08_H1.mp4", "lt_host1.webm"),
    ("seg_15_H2.mp4", "lt_host2.webm"),
]

for seg, lt in PAIRS:
    out = os.path.join(OUT, seg)
    if os.path.exists(out):
        print(f"skip: {seg}", flush=True)
        continue
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", os.path.join(SEGS, seg),
        "-c:v", "libvpx-vp9", "-i", os.path.join(GFX, lt),
        "-filter_complex", "[0:v][1:v]overlay=0:0:eof_action=pass[v]",
        "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", out,
    ]
    r = subprocess.run(cmd)
    print(("done" if r.returncode == 0 else "FAILED") + f": {seg} + {lt}", flush=True)

print("OVERLAY DONE")
