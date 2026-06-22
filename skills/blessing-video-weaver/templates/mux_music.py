# -*- coding: utf-8 -*-
"""Mix ducked background music into the final cut.

Music is loudness-normalized, then sidechain-compressed against the speech
track: whenever someone talks the music drops ~12dB and swells back during
title cards and transitions. Output video stream is copied (no re-encode).
"""
import json
import os
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

VIDEO = os.path.join("work", "final_nomusic.mp4")
MUSIC = os.path.join("work", "music_raw.m4a")
OUT = "אמונה בת 40 - ברכות מכל האחים.mp4"

probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", VIDEO],
    capture_output=True, text=True)
DUR = float(json.loads(probe.stdout)["format"]["duration"])
fade_out_start = DUR - 4.0

fc = (
    "[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[sp1][sp2];"
    "[1:a]aresample=48000,aformat=channel_layouts=stereo,"
    "loudnorm=I=-20:TP=-2.0:LRA=9,"
    f"atrim=0:{DUR:.3f},asetpts=PTS-STARTPTS,"
    f"afade=t=in:st=0:d=2.0,afade=t=out:st={fade_out_start:.3f}:d=4.0[mus];"
    "[mus][sp2]sidechaincompress=threshold=0.02:ratio=10:attack=120:release=700[duck];"
    "[sp1][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97[aout]"
)

cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
       "-i", VIDEO, "-i", MUSIC,
       "-filter_complex", fc,
       "-map", "0:v", "-map", "[aout]",
       "-c:v", "copy",
       "-c:a", "aac", "-b:a", "192k",
       "-movflags", "+faststart",
       OUT]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-1500:])
    raise SystemExit("mux failed")

probe2 = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", OUT],
    capture_output=True, text=True)
info = json.loads(probe2.stdout)["format"]
print(f"DONE: {OUT} | {float(info['duration']):.1f}s | {int(info['size'])/1e6:.1f}MB")
