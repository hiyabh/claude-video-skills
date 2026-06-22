#!/usr/bin/env python3
"""Event-recap montage builder — adapt SHOT_LIST and BASE_DIR for each event.

Renders one intermediate mp4 per shot, then chains them with xfade transitions
into a final mp4. Supports 16:9 and 9:16 outputs. No on-screen text. Optional
silent or with audio (mux audio post-build).

TO ADAPT FOR A NEW EVENT:
  1. Set BASE_DIR to the folder containing the event media
  2. Set PHOTO_SUFFIX to the common suffix of photo filenames (or "" if none)
  3. FIRST run `build_collage.py` to produce `photo_collage<SUFFIX>.jpg`
  4. Edit SHOT_LIST: shot 0 = collage (already set below). Then ~20-25 shots
     across 4 acts (establishing/faces/climax/closing)
  5. Set SPECS for the formats you want (landscape, vertical, or both)
  6. If using a logo card, name the file "logo.png" (ASCII!) at the end of SHOT_LIST
  7. Run: python build_video.py
  8. Mux audio with the command in SKILL.md "Music + Video mux command"

Key rules baked into this template:
  - The video opens INSTANTLY on the collage — no fade-from-black at the start
  - Final fade-to-black happens via the logo card
  - All transitions are crossfades — never hard cuts
"""

import os
import subprocess
import shutil
from pathlib import Path

# >>> EDIT THIS for each event:
BASE_DIR = Path("./event-media")   # <-- set to your folder of photos+clips
# Hebrew chars in the path break subprocess arg encoding on Windows.
# We chdir into BASE_DIR and pass relative paths to ffmpeg/ffprobe.
os.chdir(BASE_DIR)

# >>> EDIT THIS: common timestamp suffix on photos (or "" if none).
# Example: photo_1_2026-05-13_22-25-35.jpg -> PHOTO_SUFFIX = "_2026-05-13_22-25-35"
PHOTO_SUFFIX = "_YYYY-MM-DD_HH-MM-SS"
# Videos already use their full stem in SHOT_LIST, no suffix needed.
FPS = 30
INTERMEDIATES_BASE = BASE_DIR / "_intermediates"

SPECS = {
    "landscape": {"w": 1920, "h": 1080, "out": "<event-name>_landscape.mp4"},
}

# Each shot: type, name, dur/start, motion (photo only), trans, td (transition after this shot)
# Structure: Opening collage + 4 acts. Default target = ~50s total (17 shots).
# Budget: sum(dur) ≈ 55.8s, sum(td[0..N-2]) ≈ 5.8s, final ≈ 50s.
SHOT_LIST = [
    # Act 0 — MANDATORY opening collage (5-photo mosaic, built separately)
    {"type": "photo", "name": "photo_collage", "dur": 3.8, "motion": "zoom_in_slow", "trans": "fade",      "td": 0.5},

    # Act 1 — Establishing (~16s after td): wide scope + an anchor moment
    {"type": "video", "name": "video_example_wide",   "start": 3.0, "dur": 8.0, "trans": "fade",      "td": 0.4},
    {"type": "photo", "name": "photo_widest_crowd",   "dur": 3.0, "motion": "zoom_in",     "trans": "fade",      "td": 0.4},
    {"type": "video", "name": "video_anchor_moment",  "start": 1.0, "dur": 6.0, "trans": "fadewhite", "td": 0.4},

    # Act 2 — Faces & activity (~13s): tight mosaic — feels "many people"
    {"type": "photo", "name": "photo_face_1",         "dur": 2.5, "motion": "zoom_in",     "trans": "fade",      "td": 0.3},
    {"type": "video", "name": "video_busy_action",    "start": 2.0, "dur": 4.5, "trans": "fade",      "td": 0.3},
    {"type": "photo", "name": "photo_face_2",         "dur": 2.2, "motion": "zoom_in",     "trans": "fade",      "td": 0.3},
    {"type": "photo", "name": "photo_dense_crowd_1",  "dur": 2.3, "motion": "pan_left",    "trans": "fade",      "td": 0.3},
    {"type": "photo", "name": "photo_face_3",         "dur": 2.0, "motion": "zoom_in",     "trans": "fade",      "td": 0.3},
    {"type": "photo", "name": "photo_face_4",         "dur": 2.2, "motion": "zoom_in",     "trans": "fadewhite", "td": 0.4},

    # Act 3 — Climax (~7s): density + action peak
    {"type": "photo", "name": "photo_climax_1",       "dur": 2.2, "motion": "zoom_in",     "trans": "fade",      "td": 0.2},
    {"type": "photo", "name": "photo_climax_2",       "dur": 2.0, "motion": "pan_left",    "trans": "fade",      "td": 0.2},
    {"type": "photo", "name": "photo_dense_crowd_2",  "dur": 2.2, "motion": "zoom_in",     "trans": "fade",      "td": 0.2},
    {"type": "photo", "name": "photo_close_action",   "dur": 2.3, "motion": "zoom_in",     "trans": "fadewhite", "td": 0.4},

    # Act 4 — Hero closing + logo (~9s)
    {"type": "photo", "name": "photo_emotional_close","dur": 3.2, "motion": "zoom_in_slow","trans": "fade",      "td": 0.5},
    {"type": "photo", "name": "photo_HERO_FINAL",     "dur": 5.5, "motion": "zoom_in_slow","trans": "fadewhite", "td": 0.7},  # the iconic image
    {"type": "logo",  "name": "logo.png", "dur": 2.0,                                     "trans": "fadeblack", "td": 1.5},
]


def run(cmd):
    """Run ffmpeg/ffprobe command, raising on failure."""
    print(">>>", " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDOUT:", proc.stdout[-1500:])
        print("STDERR:", proc.stderr[-2500:])
        raise RuntimeError(f"Command failed: {cmd[0]}")
    return proc


def get_dim(rel_path):
    """rel_path is a string relative to BASE_DIR (we chdir'd there)."""
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0", rel_path
    ])
    parts = out.decode().strip().split(",")
    return int(parts[0]), int(parts[1])


def zoompan_expr(motion, frames):
    """Return (z_expr, x_expr, y_expr) for the given motion."""
    f = frames
    if motion == "zoom_in":
        return ("min(1.0+0.15*on/{f},1.15)".format(f=f),
                "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    if motion == "zoom_in_slow":
        return ("min(1.0+0.08*on/{f},1.08)".format(f=f),
                "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    if motion == "zoom_out":
        return ("max(1.15-0.15*on/{f},1.0)".format(f=f),
                "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    if motion == "pan_right":
        return ("1.15",
                "(iw-iw/1.15)*on/{f}".format(f=f),
                "(ih-ih/1.15)/2")
    if motion == "pan_left":
        return ("1.15",
                "(iw-iw/1.15)*(1-on/{f})".format(f=f),
                "(ih-ih/1.15)/2")
    if motion == "pan_up":
        return ("1.15",
                "(iw-iw/1.15)/2",
                "(ih-ih/1.15)*(1-on/{f})".format(f=f))
    return ("1.0", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")


def build_photo_filter(motion, dur, src_dim, dst):
    """Filter graph for a photo shot."""
    sw, sh = src_dim
    dw, dh = dst
    src_ar = sw / sh
    dst_ar = dw / dh
    same_orient = abs(src_ar - dst_ar) / dst_ar < 0.10
    frames = int(round(dur * FPS))
    zexp, xexp, yexp = zoompan_expr(motion, frames)

    if same_orient:
        # Pre-scale large for smooth zoompan, then crop, then zoompan back to target
        return (
            f"[0:v]scale={dw*2}:{dh*2}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={dw*2}:{dh*2},"
            f"zoompan=z='{zexp}':x='{xexp}':y='{yexp}':d={frames}:s={dw}x{dh}:fps={FPS},"
            f"format=yuv420p,setsar=1[vout]"
        )
    # Different orientation — blur-pad then zoompan
    return (
        f"[0:v]split=2[bg_in][fg_in];"
        f"[bg_in]scale={dw}:{dh}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={dw}:{dh},boxblur=30:5,setsar=1[bg];"
        f"[fg_in]scale={dw}:{dh}:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[padded];"
        f"[padded]zoompan=z='{zexp}':x='{xexp}':y='{yexp}':d={frames}:s={dw}x{dh}:fps={FPS},"
        f"format=yuv420p,setsar=1[vout]"
    )


def build_video_filter(src_dim, dst):
    sw, sh = src_dim
    dw, dh = dst
    src_ar = sw / sh
    dst_ar = dw / dh
    same_orient = abs(src_ar - dst_ar) / dst_ar < 0.10
    if same_orient:
        return (
            f"[0:v]scale={dw}:{dh}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={dw}:{dh},setsar=1,fps={FPS},format=yuv420p[vout]"
        )
    return (
        f"[0:v]split=2[bg_in][fg_in];"
        f"[bg_in]scale={dw}:{dh}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={dw}:{dh},boxblur=30:5,setsar=1[bg];"
        f"[fg_in]scale={dw}:{dh}:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={FPS},format=yuv420p[vout]"
    )


def render_intermediate(shot, idx, dst, out_rel_dir):
    """out_rel_dir is a relative path string from BASE_DIR (we chdir'd there)."""
    out_path = f"{out_rel_dir}/{idx:03d}.mp4"
    name = shot["name"]
    dw, dh = dst
    if shot["type"] == "logo":
        # White background card with logo centered, no motion
        dur = shot["dur"]
        logo_target_w = int(dw * 0.45)
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-t", f"{dur}", "-i", f"color=c=white:s={dw}x{dh}:r={FPS}",
            "-loop", "1", "-t", f"{dur}", "-i", name,
            "-filter_complex",
            f"[1:v]scale={logo_target_w}:-1:flags=lanczos[logo];"
            f"[0:v][logo]overlay=(W-w)/2:(H-h)/2:format=auto,format=yuv420p,setsar=1[vout]",
            "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", f"{FPS}",
            "-t", f"{dur}", "-an",
            out_path
        ]
        run(cmd)
        return out_path
    if shot["type"] == "photo":
        src = f"{name}{PHOTO_SUFFIX}.jpg"
        dur = shot["dur"]
        src_dim = get_dim(src)
        fc = build_photo_filter(shot["motion"], dur, src_dim, dst)
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-t", f"{dur}", "-i", src,
            "-filter_complex", fc, "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", f"{FPS}",
            "-t", f"{dur}", "-an",
            out_path
        ]
    else:
        src = f"{name}.mp4"
        src_dim = get_dim(src)
        start = shot["start"]
        dur = shot["dur"]
        fc = build_video_filter(src_dim, dst)
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start}", "-t", f"{dur}", "-i", src,
            "-filter_complex", fc, "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", f"{FPS}",
            "-t", f"{dur}", "-an",
            out_path
        ]
    run(cmd)
    return out_path


def build_final(intermediates, shots, out_path):
    """intermediates is a list of relative path strings."""
    n = len(intermediates)
    if n < 2:
        raise ValueError("Need at least 2 shots")

    inputs = []
    for p in intermediates:
        inputs.extend(["-i", p])

    durs = [s["dur"] for s in shots]
    tds = [s["td"] for s in shots]
    transes = [s["trans"] for s in shots]

    # Cascading xfade: between shot i and shot i+1 use transes[i] with duration tds[i]
    # offset_i = sum(durs[0..i]) - sum(tds[0..i-1]) - tds[i]
    filter_parts = []
    prev_label = "[0:v]"
    for i in range(n - 1):
        td = tds[i]
        trans = transes[i]
        # Special-case fadeblack at the very last junction
        # Otherwise xfade as usual
        cum_dur = sum(durs[:i + 1])
        cum_td = sum(tds[:i])
        offset = cum_dur - cum_td - td
        out_label = f"[v{i}]" if i < n - 2 else "[vchain]"
        filter_parts.append(
            f"{prev_label}[{i+1}:v]xfade=transition={trans}:duration={td}:offset={offset:.3f}{out_label}"
        )
        prev_label = out_label

    # Total duration after all xfades:
    total = sum(durs) - sum(tds[:n - 1])

    # Apply a final fade-out using tds[-1] (the closing transition)
    final_fade_dur = tds[-1]
    final_fade_start = total - final_fade_dur
    # Color: black if closing trans is fadeblack, white if fadewhite, else black
    fade_color = "black"
    if transes[-1] == "fadewhite":
        fade_color = "white"
    # NO intro fade — the video opens instantly on the collage at full brightness
    # (per user directive 2026-05-18). Only fade-out at the end remains.
    filter_parts.append(
        f"[vchain]fade=t=out:st={final_fade_start:.3f}:d={final_fade_dur}:color={fade_color}[vout]"
    )

    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", f"{FPS}",
        "-movflags", "+faststart",
        "-an",
        out_path
    ]
    run(cmd)


def build_spec(spec_name):
    spec = SPECS[spec_name]
    dst = (spec["w"], spec["h"])
    # Use relative paths (we chdir'd to BASE_DIR)
    out_rel_dir = f"_intermediates/{spec_name}"
    if Path(out_rel_dir).exists():
        shutil.rmtree(out_rel_dir)
    Path(out_rel_dir).mkdir(parents=True, exist_ok=True)

    print(f"\n=== {spec_name.upper()} {spec['w']}x{spec['h']} — {len(SHOT_LIST)} shots ===")
    intermediates = []
    for i, shot in enumerate(SHOT_LIST):
        kind = shot["type"]
        nm = shot["name"]
        print(f"  [{i+1:02d}/{len(SHOT_LIST)}] {kind:5s} {nm}")
        intermediates.append(render_intermediate(shot, i, dst, out_rel_dir))

    out_path = spec["out"]
    print(f"\n  Concat -> {out_path}")
    build_final(intermediates, SHOT_LIST, out_path)
    print(f"  OK {out_path}")


def main():
    Path("_intermediates").mkdir(parents=True, exist_ok=True)
    for spec_name in ["landscape"]:
        build_spec(spec_name)
    print("\nAll builds complete.")


if __name__ == "__main__":
    main()
