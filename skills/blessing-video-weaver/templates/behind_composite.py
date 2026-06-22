# -*- coding: utf-8 -*-
"""Text-behind-subject composite: base segment -> big word overlay -> subject cutout on top.

Output goes to work/titled/ so build_final.py picks it automatically.
"""
import os
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

SEGS = os.path.join("work", "segments")
GFX = os.path.join("gfx", "renders")
OUT = os.path.join("work", "titled")
os.makedirs(OUT, exist_ok=True)

# (segment, cutout webm, text webm)
TRIPLES = [
    ("seg_01_Z1.mp4", "cut_01.webm", "bh_40.webm"),
    ("seg_22_A7.mp4", "cut_22.webm", "bh_balev.webm"),
    ("seg_37_Z8.mp4", "cut_37.webm", "bh_mazal.webm"),
]

for seg, cut, txt in TRIPLES:
    out = os.path.join(OUT, seg)
    seg_p = os.path.join(SEGS, seg)
    cut_p = os.path.join(SEGS, cut)
    txt_p = os.path.join(GFX, txt)
    for p in (seg_p, cut_p, txt_p):
        if not os.path.exists(p):
            raise SystemExit(f"missing: {p}")
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", seg_p,
        "-c:v", "libvpx-vp9", "-i", txt_p,
        "-c:v", "libvpx-vp9", "-i", cut_p,
        "-filter_complex",
        "[0:v][1:v]overlay=0:0:eof_action=pass[base];"
        "[base][2:v]overlay=0:0:eof_action=pass[v]",
        "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", out,
    ]
    r = subprocess.run(cmd)
    print(("done" if r.returncode == 0 else "FAILED") + f": {seg} (text-behind)", flush=True)

print("BEHIND DONE")
