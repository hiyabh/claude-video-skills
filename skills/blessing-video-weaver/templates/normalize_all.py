# -*- coding: utf-8 -*-
"""Normalize all clips to 576x1024 @30fps, h264 crf18, aac 48k stereo, loudnorm.

Hezi is handled separately by face-track-reframe (square -> 9:16 needs tracking);
this script post-processes its output for fps/audio uniformity too.
"""
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)  # Hebrew-safe: pass relative paths only

SRC = "סרטונים"
NORM = os.path.join("work", "norm")
W, H = 576, 1024
VF_FILL = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps=30"
AF = "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000"

CLIPS = {
    "שירה": os.path.join(SRC, "שירה.MOV"),
    "איתן": os.path.join(SRC, "איתן.MP4"),
    "מאיה": os.path.join(SRC, "מאיה.mp4"),
    "תמר": os.path.join(SRC, "תמר.MP4"),
    "נועה": os.path.join(SRC, "נועה.mp4"),
    "יוסי": os.path.join(SRC, "יוסי.mp4"),
    "דוד": os.path.join(SRC, "דוד.MP4"),
    "רוני": os.path.join(SRC, "רוני.mp4"),
    # Hezi: input is the face-tracked 576x1024 output, normalize fps/audio only
    "גיל": os.path.join("work", "norm", "גיל.mp4"),
}

only = sys.argv[1] if len(sys.argv) > 1 else None

for name, src in CLIPS.items():
    if only and only != name:
        continue
    out = os.path.join(NORM, name + "_n.mp4")
    if os.path.exists(out):
        print(f"skip (exists): {name}", flush=True)
        continue
    if not os.path.exists(src):
        print(f"MISSING SOURCE: {src}", flush=True)
        continue
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", src,
        "-vf", VF_FILL,
        "-af", AF,
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ac", "2",
        "-movflags", "+faststart",
        out,
    ]
    r = subprocess.run(cmd)
    print(("done: " if r.returncode == 0 else "FAILED: ") + name, flush=True)

print("NORMALIZE DONE")
