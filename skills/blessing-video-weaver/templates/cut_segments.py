# -*- coding: utf-8 -*-
"""Cut all script segments from normalized clips (work/norm) into work/segments.

v3 — two-stage cut (fixes the v2 speed bug):
  Stage A: input-side trim (-ss/-t BEFORE -i) + speed change (setpts+atempo,
           SpeakerH 1.15x) + per-segment loudnorm -> clean CFR intermediate.
  Stage B: punch crop (jump-cut masking) + zoompan Ken Burns on the clean
           intermediate. zoompan regenerates CFR timestamps, which is exactly
           why the speedup must be baked in BEFORE it (v2 mixed them in one
           chain and zoompan silently undid the setpts retiming).
"""
import os
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)  # Hebrew-safe relative paths

NORM = os.path.join("work", "norm")
OUT = os.path.join("work", "segments")
os.makedirs(OUT, exist_ok=True)

PUNCH_VF = "scale=622:1106:flags=lanczos,crop=576:1024"
SPEED_H = 1.15
ZOOM_MAX = 0.06

# (index, id, source name, start, end, punch)
SEGS = [
    (1,  "Z1", "גיל",   0.0,   3.1,  False),
    (2,  "G1", "תמר", 0.0,   2.6,  False),
    (3,  "H1", "נועה", 0.0,   12.3, False),
    (4,  "G2", "תמר", 3.8,   27.8, False),
    (5,  "D1", "דוד", 0.0,   13.9, False),
    (6,  "Y1", "יוסי",  0.0,   17.6, False),
    (7,  "E1", "איתן", 0.0,   10.1, False),
    (8,  "B1", "מאיה",  0.0,   14.6, False),
    (9,  "Z2", "גיל",   4.4,   29.9, False),
    (10, "E2", "איתן", 9.8,   25.0, True),
    (11, "H6", "נועה", 69.3,  97.9, False),
    (12, "Z4", "גיל",   29.9,  71.4, True),
    (13, "D2", "דוד", 13.7,  40.7, False),
    (14, "H2", "נועה", 13.6,  43.4, False),
    (15, "B2", "מאיה",  14.5,  31.0, True),
    (16, "Y2", "יוסי",  17.3,  32.8, False),
    (17, "E3", "איתן", 25.0,  36.4, False),
    (18, "H4", "נועה", 45.6,  69.7, True),
    (19, "A1", "שירה",  0.0,   26.5, False),
    (20, "H8", "נועה", 100.4, 119.2, False),
    (21, "H9", "נועה", 121.8, 135.3, True),
    (22, "A7", "שירה",  71.2,  78.7, True),
    (23, "S1", "רוני",  0.0,   33.6, False),
    (24, "H10", "נועה", 135.1, 156.3, False),
    (25, "Y3", "יוסי",  32.5,  56.1, True),
    (26, "A4", "שירה",  35.5,  59.7, False),
    (27, "G4", "תמר", 27.5,  38.9, True),
    (28, "B3", "מאיה",  31.0,  38.4, False),
    (29, "Z7", "גיל",   71.4,  89.2, False),
    (30, "Y4", "יוסי",  55.7,  72.0, True),
    (31, "G5", "תמר", 38.7,  45.4, False),
    (32, "E4", "איתן", 37.1,  45.3, True),
    (33, "S4", "רוני",  33.2,  38.0, True),
    (34, "A6", "שירה",  60.2,  70.6, False),
    (35, "H11", "נועה", 155.9, 168.7, False),
    (36, "A8", "שירה",  79.5,  88.0, True),
    (37, "Z8", "גיל",   89.2,  98.6, True),
]

ENC_V = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"]
ENC_A = ["-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]

for idx, sid, src, start, end, punch in SEGS:
    out = os.path.join(OUT, f"seg_{idx:02d}_{sid}.mp4")
    if os.path.exists(out):
        print(f"skip: {idx:02d}_{sid}", flush=True)
        continue
    src_path = os.path.join(NORM, src + "_n.mp4")
    dur = round(end - start, 3)
    speed = SPEED_H if sid.startswith("H") else 1.0
    out_dur = dur / speed
    tmp = os.path.join(OUT, f"_tmp_{idx:02d}.mp4")

    # Stage A — trim on the INPUT side, apply speed, normalize loudness
    vf_a = (f"setpts=PTS/{speed}," if speed != 1.0 else "") + "fps=30"
    af_a = (f"atempo={speed}," if speed != 1.0 else "") + "loudnorm=I=-15:TP=-1.5:LRA=11"
    cmd_a = (["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
              "-ss", str(start), "-t", str(dur), "-i", src_path,
              "-vf", vf_a, "-af", af_a]
             + ENC_V + ENC_A + ["-movflags", "+faststart", tmp])
    if subprocess.run(cmd_a).returncode != 0:
        print(f"FAILED(A): {idx:02d}_{sid}", flush=True)
        continue

    # Stage B — punch + Ken Burns zoom on the clean CFR intermediate
    frames = max(int(out_dur * 30), 2)
    rate = ZOOM_MAX / frames
    if idx % 2 == 1:
        zexpr = f"min(1+{rate:.6f}*in\\,{1 + ZOOM_MAX})"
    else:
        zexpr = f"max({1 + ZOOM_MAX}-{rate:.6f}*in\\,1.0)"
    # fps=30 is critical: zoompan's default output pacing is 25fps, which
    # silently slows 30fps input by 1.2x and desyncs audio.
    zoompan = (f"zoompan=z='{zexpr}':d=1:fps=30"
               f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=576x1024")
    vf_b = (PUNCH_VF + "," if punch else "") + zoompan
    cmd_b = (["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
              "-i", tmp, "-vf", vf_b]
             + ENC_V + ["-c:a", "copy", "-movflags", "+faststart", out])
    ok = subprocess.run(cmd_b).returncode == 0
    os.remove(tmp)
    print(("done" if ok else "FAILED(B)") + f": {idx:02d}_{sid} ({out_dur:.1f}s)", flush=True)

print("CUT DONE")
