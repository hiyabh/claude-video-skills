# -*- coding: utf-8 -*-
"""TEMPLATE — append the 2s credit endcard to the render and emit master + share.
Run from build/ after rendering clip/renders/clip_fast.mp4 and qc/endcard.png."""
import subprocess, os

# ---------- CONFIG ----------
REND = "clip/renders/clip_fast.mp4"
ENDCARD = "qc/endcard.png"
MASTER = "../פרשת חוקת - זוגיות ופרנסה (רקע נושאי).mp4"
SHARE = "../פרשת חוקת - זוגיות ופרנסה (רקע נושאי) - לשיתוף.mp4"
END_SECS = 2.0
# ----------------------------

def run(a): subprocess.run(a, check=True, capture_output=True)
os.makedirs("fast", exist_ok=True)

# 1) endcard -> 2s clip, gentle fade-in, silent stereo 48k aac (matches main stream)
run(["ffmpeg", "-y", "-loop", "1", "-t", f"{END_SECS}", "-i", ENDCARD,
     "-f", "lavfi", "-t", f"{END_SECS}", "-i", "anullsrc=r=48000:cl=stereo",
     "-vf", "fade=t=in:st=0:d=0.4,scale=1080:1920,setsar=1,fps=30",
     "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2", "fast/endcard.mp4"])

# 2) concat main + endcard (re-encode = safe stream join) -> master
run(["ffmpeg", "-y", "-i", REND, "-i", "fast/endcard.mp4",
     "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
     "-map", "[v]", "-map", "[a]",
     "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", MASTER])

# 3) share (smaller, faststart)
run(["ffmpeg", "-y", "-i", MASTER,
     "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", SHARE])

def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip())
print("master:", round(dur(MASTER), 2), "s,", os.path.getsize(MASTER) // (1024 * 1024), "MB")
print("share :", round(dur(SHARE), 2), "s,", os.path.getsize(SHARE) // (1024 * 1024), "MB")
