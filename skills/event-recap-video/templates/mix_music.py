#!/usr/bin/env python3
"""Mix background music UNDER the clip audio of the rendered master.

v2 (2026-09-06, round 4): the level of the music follows a PLANNED ENVELOPE
(piecewise-linear in dB over time) instead of a sidechain compressor. The
sidechain pumped — every breath in the chant let the music jump up and get
squashed again, which the user heard as "הולך וחוזר ונקטע". A planned envelope
never reacts to the clip audio, so it cannot pump.

USAGE: python mix_music.py   -> writes DELIVERABLE
"""

import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# >>> EDIT per event:
MASTER = "<event>_recap_vertical.mp4"          # output of build_video_dramatic.py (clip audio only)
MUSIC = "מוזיקת רקע - <track name>.m4a"         # profiled track (see SKILL.md "Never mux from t=0")
DELIVERABLE = "01 - <event description>.mp4"

MUSIC_ENTRY_SEC = 0.0        # >>> EDIT: first second where the track is at steady level
FADE_OUT_SEC = 3.5           # synced with the video's fade to black
SILENT_DB = -50.0            # inaudible; -80 made the 3.5s fade drop 17 dB/s and read as a cut

# Music GAIN envelope: (time_sec, dB applied to the track). Linear ramps between
# points; the last point holds until the closing fade. The track sits at about
# -12.5 dB mean, so the resulting levels are: open -21, under chant -30,
# closing -20.5. >>> EDIT the breakpoints to the clip-audio stretch of YOUR cut
# (measure the track mean with volumedetect first; gain = wanted level - mean).
LEVEL_OPEN_DB = -9.0         # collage alone, before the chant enters
LEVEL_UNDER_CHANT_DB = -18.0 # a whisper under the prayer
LEVEL_CLOSING_DB = -8.0      # closing montage: music carries the ending
ENVELOPE_DB = [
    (0.0, SILENT_DB),
    (1.0, LEVEL_OPEN_DB),
    (2.5, LEVEL_UNDER_CHANT_DB),
    (27.0, LEVEL_UNDER_CHANT_DB),
    (30.5, LEVEL_CLOSING_DB),
]


def master_duration():
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", MASTER])
    return float(out.decode().strip())


def envelope_expr(points, total):
    """ffmpeg `volume` expression (linear gain) for a piecewise-linear dB envelope
    ending in a fade to silence over the last FADE_OUT_SEC seconds."""
    pts = list(points) + [(total - FADE_OUT_SEC, points[-1][1]), (total, SILENT_DB)]
    expr = f"{pts[-1][1]}"
    for (t0, d0), (t1, d1) in reversed(list(zip(pts, pts[1:]))):
        seg = f"({d0}+({d1}-{d0})*(t-{t0})/({t1}-{t0}))"
        expr = f"if(lt(t,{t1}),{seg},{expr})"
    expr = f"if(lt(t,{pts[0][0]}),{pts[0][1]},{expr})"
    return f"pow(10,({expr})/20)"


def main():
    dur = master_duration()
    gain = envelope_expr(ENVELOPE_DB, dur)
    fc = (
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{dur:.3f},"
        f"volume='{gain}':eval=frame[mus];"
        f"[0:a][mus]amix=inputs=2:normalize=0,alimiter=limit=0.95[aout]"
    )
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", MASTER, "-ss", f"{MUSIC_ENTRY_SEC}", "-i", MUSIC,
           "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-t", f"{dur:.3f}", "-movflags", "+faststart", DELIVERABLE]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-2000:])
        raise RuntimeError("music mix failed")
    print(f"OK {DELIVERABLE} ({Path(DELIVERABLE).stat().st_size:,} bytes, {dur:.2f}s)")


if __name__ == "__main__":
    main()
