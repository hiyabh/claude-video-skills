#!/usr/bin/env python3
"""Reframe a video to a target aspect ratio with a dynamic, face-tracking crop.

The crop window follows the speaker's face across the clip so the face stays
centered and is never cut off — even when they move within the frame.

Usage:
    python reframe.py INPUT [-o OUTPUT] [--aspect 9:16] [--size 464x848]
                       [--smooth 0.6] [--crf 18]

Examples:
    python reframe.py talk.mov                      # -> talk_reframe.mp4, 9:16
    python reframe.py talk.mov --size 464x848       # match other clips exactly
    python reframe.py wide.mp4 --aspect 4:5         # Instagram portrait
"""
import argparse
import subprocess
import sys

import cv2
import numpy as np

DEFAULT_SMOOTH_SEC = 0.6
MIN_FACE = 70           # px, smallest detectable face side
DETECT_SCALE = 1.1
DETECT_NEIGHBORS = 6


def parse_aspect(text):
    """'9:16' or '0.5625' -> float width/height ratio."""
    if ":" in text:
        w, h = text.split(":")
        return float(w) / float(h)
    return float(text)


def parse_size(text):
    """'464x848' -> (464, 848)."""
    w, h = text.lower().split("x")
    return int(w), int(h)


def even(n):
    """Round to nearest even int (required by yuv420p)."""
    return int(round(n / 2.0)) * 2


def load_cascades():
    base = cv2.data.haarcascades
    front = cv2.CascadeClassifier(base + "haarcascade_frontalface_default.xml")
    prof = cv2.CascadeClassifier(base + "haarcascade_profileface.xml")
    return front, prof


def detect_one(gray, front, prof, src_w):
    """Return (cx, cy) of the largest face in a grayscale frame, or None."""
    faces = front.detectMultiScale(gray, DETECT_SCALE, DETECT_NEIGHBORS,
                                   minSize=(MIN_FACE, MIN_FACE))
    if len(faces) == 0:
        faces = prof.detectMultiScale(gray, DETECT_SCALE, DETECT_NEIGHBORS,
                                      minSize=(MIN_FACE, MIN_FACE))
    if len(faces) == 0:
        flipped = prof.detectMultiScale(cv2.flip(gray, 1), DETECT_SCALE,
                                        DETECT_NEIGHBORS, minSize=(MIN_FACE, MIN_FACE))
        faces = [(src_w - (x + w), y, w, h) for (x, y, w, h) in flipped]
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return x + w / 2.0, y + h / 2.0


def detect_track(path, axis):
    """Scan every frame, return (centers_along_axis, fps, src_w, src_h)."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        sys.exit(f"ERROR: cannot open '{path}'")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    front, prof = load_cascades()
    centers = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        c = detect_one(gray, front, prof, src_w)
        centers.append(None if c is None else (c[0] if axis == "x" else c[1]))
    cap.release()
    return centers, fps, src_w, src_h


def smooth_track(centers, fps, span, limit, smooth_sec, fallback):
    """Interpolate gaps, smooth, convert face-center -> clamped crop origin."""
    arr = np.array([np.nan if c is None else c for c in centers], dtype=float)
    valid = ~np.isnan(arr)
    if valid.sum() == 0:
        arr[:] = fallback
    else:
        xs = np.arange(len(arr))
        arr = np.interp(xs, xs[valid], arr[valid])
    win = max(3, int(round(fps * smooth_sec)))
    win += (win + 1) % 2  # force odd
    padded = np.pad(arr, win // 2, mode="edge")
    arr = np.convolve(padded, np.ones(win) / win, mode="valid")
    origin = np.clip(arr - span / 2.0, 0, max(0, limit))
    return origin, int(valid.sum())


def compute_window(src_w, src_h, ratio):
    """Pick crop dims + tracking axis so cropped region matches target ratio."""
    src_ratio = src_w / src_h
    if src_ratio > ratio:                      # source too wide -> crop width
        cw, ch, axis = even(src_h * ratio), src_h, "x"
    else:                                      # source too tall -> crop height
        cw, ch, axis = src_w, even(src_w / ratio), "y"
    return cw, ch, axis


def render(path, out, origin, cw, ch, axis, out_w, out_h, fps, crf):
    """Crop each frame along the tracked axis, scale, mux original audio."""
    cap = cv2.VideoCapture(path)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-s", f"{out_w}x{out_h}", "-r", str(fps), "-i", "pipe:0",
        "-i", path, "-map", "0:v:0", "-map", "1:a:0?",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", out,
    ], stdin=subprocess.PIPE)
    i, n = 0, len(origin)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        o = int(round(origin[min(i, n - 1)]))
        if axis == "x":
            strip = frame[0:ch, o:o + cw]
        else:
            strip = frame[o:o + ch, 0:cw]
        out_frame = cv2.resize(strip, (out_w, out_h), interpolation=cv2.INTER_LANCZOS4)
        ff.stdin.write(out_frame.tobytes())
        i += 1
    cap.release()
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ERROR: ffmpeg failed during encode")
    return i


def main():
    p = argparse.ArgumentParser(description="Face-tracking video reframe")
    p.add_argument("input")
    p.add_argument("-o", "--output")
    p.add_argument("--aspect", default="9:16", help="target W:H (default 9:16)")
    p.add_argument("--size", help="exact output WxH, e.g. 464x848 (overrides scale)")
    p.add_argument("--smooth", type=float, default=DEFAULT_SMOOTH_SEC,
                   help="smoothing window seconds (default 0.6)")
    p.add_argument("--crf", type=int, default=18, help="x264 quality (default 18)")
    args = p.parse_args()

    out = args.output or _default_out(args.input)
    # If an exact --size is given, derive the crop ratio from it so the crop
    # matches the output and nothing is stretched; otherwise use --aspect.
    if args.size:
        size_w, size_h = parse_size(args.size)
        ratio = size_w / size_h
    else:
        ratio = parse_aspect(args.aspect)

    # Probe + detect (axis decided from source vs target ratio).
    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        sys.exit(f"ERROR: cannot open '{args.input}'")
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    cw, ch, axis = compute_window(src_w, src_h, ratio)

    centers, fps, src_w, src_h = detect_track(args.input, axis)
    span = cw if axis == "x" else ch
    limit = (src_w - cw) if axis == "x" else (src_h - ch)
    fallback = (src_w if axis == "x" else src_h) / 2.0
    origin, detected = smooth_track(centers, fps, span, limit, args.smooth, fallback)

    if args.size:
        out_w, out_h = parse_size(args.size)
    else:
        out_w, out_h = even(cw), even(ch)

    print(f"source {src_w}x{src_h} -> crop {cw}x{ch} (track {axis}) "
          f"-> out {out_w}x{out_h} | faces {detected}/{len(centers)}")
    n = render(args.input, out, origin, cw, ch, axis, out_w, out_h, fps, args.crf)
    print(f"done: {n} frames -> {out}")


def _default_out(path):
    import os
    stem, _ = os.path.splitext(path)
    return f"{stem}_reframe.mp4"


if __name__ == "__main__":
    main()
