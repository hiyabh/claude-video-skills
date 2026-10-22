#!/usr/bin/env python3
"""Overlay the logo as a persistent corner watermark for the WHOLE video.

User directive (2026-07-07): every recap should carry the logo in a corner
throughout, in addition to the big logo card at the end. Run this on the final
MUXED master (with audio); it re-encodes the video and copies the audio through.

Order in the pipeline:
  build_video.py -> mux audio -> add_watermark.py -> WhatsApp export -> organize

USAGE:
  1. Set BASE_DIR, MASTER (the muxed deliverable), LOGO.
  2. Tune CORNER / SIZE_RATIO / PAD_RATIO / OPACITY if needed.
  3. Run: python add_watermark.py   (writes MASTER in place via a temp file)
"""

import os
import subprocess
from pathlib import Path

# >>> EDIT per event:
BASE_DIR = Path("./event-media")   # <-- set to your folder of photos+clips
MASTER = "01 - <event-name>.mp4"   # the final muxed deliverable (has audio)
LOGO = "logo.png"                   # ASCII-named logo (transparent PNG recommended)
os.chdir(BASE_DIR)

# Watermark placement/appearance
CORNER = "tr"        # 'tr' top-right | 'tl' top-left | 'br' bottom-right | 'bl' bottom-left
SIZE_RATIO = 0.14    # logo width as a fraction of frame width
PAD_RATIO = 0.035    # padding from the edges, fraction of frame width
OPACITY = 0.88       # 0..1 — slight transparency so it reads as a watermark

FPS = 30
CRF = 18


def overlay_xy(corner):
    """Return the ffmpeg overlay x:y expression for the chosen corner."""
    pad = "PAD"
    return {
        "tl": f"{pad}:{pad}",
        "tr": f"main_w-overlay_w-{pad}:{pad}",
        "bl": f"{pad}:main_h-overlay_h-{pad}",
        "br": f"main_w-overlay_w-{pad}:main_h-overlay_h-{pad}",
    }[corner]


def main():
    # Probe frame width to compute pixel sizes
    w = int(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width", "-of", "csv=p=0", MASTER
    ]).decode().strip())
    logo_w = int(w * SIZE_RATIO)
    pad = int(w * PAD_RATIO)
    xy = overlay_xy(CORNER).replace("PAD", str(pad))
    # -shortest cannot bound the looped logo when the master has no audio stream
    # (2026-08-25: a silent master produced a 99-minute file); pin the length explicitly.
    master_dur = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", MASTER
    ]).decode().strip()

    tmp = "_wm_tmp.mp4"
    fc = (
        f"[1:v]scale={logo_w}:-1:flags=lanczos,format=rgba,"
        f"colorchannelmixer=aa={OPACITY}[wm];"
        f"[0:v][wm]overlay={xy}:format=auto,format=yuv420p[vout]"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        # No -loop on the logo: a looped 25fps still made overlay + -r 30 duplicate/drop frames
        # (freeze + jump inside transitions, 2026-10-20). overlay repeats the single frame itself.
        "-i", MASTER, "-i", LOGO,
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "medium", "-crf", f"{CRF}",
        "-pix_fmt", "yuv420p", "-r", f"{FPS}",
        "-c:a", "copy", "-movflags", "+faststart",
        "-t", master_dur, "-shortest", tmp,
    ]
    print(">>> overlaying watermark:", CORNER, f"{int(SIZE_RATIO*100)}% @ opacity {OPACITY}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-2000:])
        raise RuntimeError("watermark overlay failed")

    os.replace(tmp, MASTER)
    print(f"OK watermarked -> {MASTER} ({Path(MASTER).stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
