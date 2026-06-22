# -*- coding: utf-8 -*-
"""Assemble the final cut: chapters built with varied xfade transitions, then joined.

Two-level cascade keeps each ffmpeg filter graph small and every piece is
re-encoded at most twice (chapter build + final join). Audio uses acrossfade
with the same duration as the video xfade so A/V stay in sync.
"""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

SEGS = os.path.join("work", "segments")
TITLED = os.path.join("work", "titled")
GFX = os.path.join("gfx", "renders")
PARTS = os.path.join("work", "parts")
os.makedirs(PARTS, exist_ok=True)


def seg(name):
    """Prefer the titled (overlay) version when it exists."""
    t = os.path.join(TITLED, name)
    return t if os.path.exists(t) else os.path.join(SEGS, name)


def gfx(name):
    return os.path.join(GFX, name)


# Each chapter: list of (path, transition-to-NEXT-piece, transition-duration)
# transition on the last piece of a part = transition used when joining parts.
P1 = [
    (seg("seg_01_Z1.mp4"), "slideleft", 0.25),
    (seg("seg_02_G1.mp4"), "zoomin", 0.3),
    (gfx("intro.mp4"), "smoothup", 0.45),
    (gfx("ch1.mp4"), "circleopen", 0.45),
    (seg("seg_03_H1.mp4"), "slideleft", 0.3),
    (seg("seg_04_G2.mp4"), "smoothup", 0.3),
    (seg("seg_05_D1.mp4"), "hlslice", 0.3),
    (seg("seg_06_Y1.mp4"), "radial", 0.45),
]
P2 = [
    (gfx("ch_bina.mp4"), "circleopen", 0.4),
    (seg("seg_07_E1.mp4"), "slideup", 0.3),
    (seg("seg_08_B1.mp4"), "pixelize", 0.35),
    (gfx("ch2.mp4"), "smoothright", 0.4),
    (seg("seg_09_Z2.mp4"), "slideleft", 0.3),
    (seg("seg_10_E2.mp4"), "dissolve", 0.3),
    (seg("seg_11_H6.mp4"), "smoothup", 0.3),
    (seg("seg_12_Z4.mp4"), "hlslice", 0.3),
    (seg("seg_13_D2.mp4"), "zoomin", 0.4),
]
P3 = [
    (gfx("ch3.mp4"), "circleopen", 0.4),
    (seg("seg_14_H2.mp4"), "slideleft", 0.3),
    (seg("seg_15_B2.mp4"), "smoothup", 0.3),
    (seg("seg_16_Y2.mp4"), "radial", 0.4),
]
P4 = [
    (gfx("ch4.mp4"), "circleopen", 0.4),
    (seg("seg_17_E3.mp4"), "slideright", 0.3),
    (seg("seg_18_H4.mp4"), "smoothleft", 0.3),
    (seg("seg_19_A1.mp4"), "dissolve", 0.3),
    (seg("seg_20_H8.mp4"), "smoothup", 0.3),
    (seg("seg_21_H9.mp4"), "fade", 0.25),
    (seg("seg_22_A7.mp4"), "zoomin", 0.4),
]
P5 = [
    (gfx("ch5.mp4"), "circleopen", 0.4),
    (seg("seg_23_S1.mp4"), "slideleft", 0.3),
    (seg("seg_24_H10.mp4"), "hlslice", 0.3),
    (seg("seg_25_Y3.mp4"), "radial", 0.4),
]
P6 = [
    (gfx("ch6.mp4"), "circleopen", 0.4),
    (seg("seg_26_A4.mp4"), "smoothup", 0.3),
    (seg("seg_27_G4.mp4"), "slideright", 0.3),
    (seg("seg_28_B3.mp4"), "pixelize", 0.35),
]
P7 = [
    (gfx("ch7.mp4"), "circleopen", 0.4),
    (seg("seg_29_Z7.mp4"), "slideleft", 0.28),
    (seg("seg_30_Y4.mp4"), "smoothup", 0.28),
    (seg("seg_31_G5.mp4"), "dissolve", 0.28),
    (seg("seg_32_E4.mp4"), "slideright", 0.28),
    (seg("seg_33_S4.mp4"), "smoothleft", 0.28),
    (seg("seg_34_A6.mp4"), "hlslice", 0.28),
    (seg("seg_35_H11.mp4"), "smoothup", 0.28),
    (seg("seg_36_A8.mp4"), "fade", 0.28),
    (seg("seg_37_Z8.mp4"), "fadeblack", 0.6),
    (gfx("outro.mp4"), "fade", 0.4),
]

PARTS_LIST = [("part1", P1), ("part2", P2), ("part3", P3), ("part4", P4),
              ("part5", P5), ("part6", P6), ("part7", P7)]


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True)
    return float(json.loads(out.stdout)["format"]["duration"])


def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=codec_type", "-of", "json", path],
        capture_output=True, text=True)
    return bool(json.loads(out.stdout).get("streams"))


def build_xfade(pieces, out_path):
    """pieces: list of (path, trans_to_next, td). Last piece's trans is unused here."""
    n = len(pieces)
    durs = [probe_duration(p) for p, _, _ in pieces]
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    fc = []
    for i, (p, _, _) in enumerate(pieces):
        cmd += ["-i", p]
        if has_audio(p):
            fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo:d={durs[i]}[a{i}]")
        fc.append(f"[{i}:v]format=yuv420p,settb=AVTB,fps=30[v{i}]")

    vprev, aprev = "v0", "a0"
    offset = 0.0
    for i in range(1, n):
        trans, td = pieces[i - 1][1], pieces[i - 1][2]
        offset += durs[i - 1] - td
        vout, aout = f"vx{i}", f"ax{i}"
        fc.append(f"[{vprev}][v{i}]xfade=transition={trans}:duration={td}:offset={offset:.3f}[{vout}]")
        fc.append(f"[{aprev}][a{i}]acrossfade=d={td}:c1=tri:c2=tri[{aout}]")
        vprev, aprev = vout, aout

    cmd += ["-filter_complex", ";".join(fc),
            "-map", f"[{vprev}]", "-map", f"[{aprev}]",
            "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:], flush=True)
        raise SystemExit(f"xfade build failed: {out_path}")
    print(f"built: {out_path} ({probe_duration(out_path):.1f}s)", flush=True)


# Level 1: build each part
part_files = []
for name, plist in PARTS_LIST:
    out = os.path.join(PARTS, name + ".mp4")
    part_files.append((out, plist[-1][1], plist[-1][2]))
    if os.path.exists(out):
        print(f"skip: {name}", flush=True)
        continue
    build_xfade(plist, out)

# Level 2: join parts (transition of each part = its last piece's transition)
final = os.path.join("work", "final_nomusic.mp4")
if not os.path.exists(final):
    build_xfade(part_files, final)
else:
    print("skip: final_nomusic", flush=True)

print(f"FINAL (no music): {probe_duration(final):.1f}s")
