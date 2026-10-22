#!/usr/bin/env python3
"""Event-recap builder — DRAMATIC MODE (transitions.py + clip-audio timeline).

Use this template instead of build_video.py when the user asks for showy
transitions ("אפקטים", "סיבובים", "גלגול", "פעימות") and/or wants the clips'
own sound (prayer, speeches, singing) to lead the soundtrack. Born on the
Selichot recap, 2026-09-06. What differs from build_video.py:
  1. DRAMATIC TRANSITIONS rendered by transitions.py (spin, roll, flip, punch,
     bounce, whip, pinwheel...) instead of ffmpeg xfade. Each shot is rendered
     to a full-length intermediate; the tail of shot A and the head of shot B
     are extracted as PNGs, composited frame-by-frame, and the bodies +
     transition clips are concatenated.
  2. THE PRAYER IS THE SOUNDTRACK: the clips' own audio is placed on an explicit
     timeline with J-cuts/L-cuts (a clip's chant may start under the previous
     photo and continue under the next), loudness-normalised and crossfaded.
     Music is added afterwards, ducked, by mix_music.py.
  3. "pulse" Ken Burns motion — a heartbeat zoom on stills.

Timeline math is xfade-compatible: shot i+1 starts at
    T[i+1] = sum(dur[0..i]) - sum(td[0..i])
and the transition between i and i+1 occupies [T[i+1], T[i+1] + td[i]].
"""

import os
import shutil
import subprocess
from pathlib import Path

import transitions

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

PHOTO_SUFFIX = "_YYYY-MM-DD_HH-MM-SS"   # >>> EDIT: common suffix of photo_N files
FPS = 30
W, H = 1080, 1920
AUDIO_RATE = 48000
CLIP_LOUDNESS_LUFS = -14
CLIP_XFADE = 0.6          # audio crossfade between consecutive clip segments
PULSE_PERIOD_SEC = 1.5    # heartbeat period for the "pulse" motion
INTER = Path("_intermediates")
OUT_VIDEO = "<event>_recap_vertical.mp4"   # >>> EDIT (silent-music master; mix_music.py adds the bed)

# >>> EDIT: clip stems (no .mp4). Run analyze_clips.py first and note the
# loud/strong windows of each clip next to its name.
VIDEO_A = "video_YYYY-MM-DD_HH-MM-SS (2)"   # e.g. landscape 20.7s: strongest chant 12.5-18
VIDEO_B = "video_YYYY-MM-DD_HH-MM-SS"       # e.g. portrait 9.4s: loud 0-7.7 then silence

# >>> EDIT the SHOT_LIST. Example below is the approved Selichot cut (35.9s).
# Video shots: start = source offset shown on screen; a_lead = seconds of audio
# played BEFORE the shot appears (J-cut, from src start-a_lead); a_tail = seconds
# of audio continued AFTER the shot (L-cut under following photos).
SHOT_LIST = [
    {"type": "photo", "name": "photo_collage", "dur": 3.8, "motion": "zoom_in_slow", "trans": "spin_in",         "td": 0.8},
    {"type": "video", "name": VIDEO_A, "start": 2.0, "dur": 7.0, "a_lead": 2.0, "a_tail": 4.2, "trans": "roll_out_left", "td": 0.8},
    {"type": "photo", "name": "photo_1", "dur": 3.0, "motion": "pulse",            "trans": "rise_tilt",       "td": 0.7},
    {"type": "photo", "name": "photo_2", "dur": 3.0, "motion": "pan_left",         "trans": "punch_in",        "td": 0.6},
    {"type": "video", "name": VIDEO_B, "start": 0.0, "dur": 7.4, "a_lead": 0.0, "a_tail": 0.0, "trans": "pinwheel",      "td": 0.8},
    {"type": "video", "name": VIDEO_A, "start": 13.2, "dur": 7.0, "a_lead": 0.0, "a_tail": 0.5, "trans": "whip_left",    "td": 0.5},
    {"type": "photo", "name": "photo_4", "dur": 3.2, "motion": "pulse",            "trans": "shrink_spin_out", "td": 0.8},
    {"type": "photo", "name": "photo_3", "dur": 5.0, "motion": "zoom_in_slow",     "trans": "fadeblack",       "td": 0.7},
    {"type": "logo",  "name": "logo.png", "dur": 2.2,                              "trans": "fadeblack",       "td": 1.5},
]

# -bf 0: B-frames give every part a negative start DTS; concat -c copy then overlaps the
# parts and the muxer re-times them -> a freeze + jump inside every transition (2026-10-20).
VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-bf", "0",
        "-pix_fmt", "yuv420p", "-r", f"{FPS}"]


def run(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print("CMD:", " ".join(str(c) for c in cmd))
        print("STDERR:", proc.stderr[-2500:])
        raise RuntimeError(f"Command failed: {cmd[0]}")
    return proc


def ffmpeg(*args):
    return run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args])


def probe(path, entry):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", entry,
                                   "-of", "csv=p=0", path])
    return out.decode().strip()


def get_dim(path):
    w, h = probe(path, "stream=width,height").split(",")[:2]
    return int(w), int(h)


def frames_of(sec):
    return int(round(sec * FPS))


# ---------------------------------------------------------------- timeline
def shot_starts(shots):
    starts, t = [], 0.0
    for i, s in enumerate(shots):
        starts.append(t)
        t += s["dur"] - s["td"]
    total = sum(s["dur"] for s in shots) - sum(s["td"] for s in shots[:-1])
    return starts, total


# ---------------------------------------------------------------- stills
def zoompan_expr(motion, frames):
    f = frames
    center = ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    if motion == "zoom_in":
        return (f"min(1.0+0.15*on/{f},1.15)", *center)
    if motion == "zoom_in_slow":
        return (f"min(1.0+0.08*on/{f},1.08)", *center)
    if motion == "pulse":
        p = PULSE_PERIOD_SEC
        return (f"1.06+0.07*exp(-6*mod(on/{FPS},{p})/{p})", *center)
    if motion == "pan_left":
        return ("1.15", f"(iw-iw/1.15)*(1-on/{f})", "(ih-ih/1.15)/2")
    if motion == "pan_right":
        return ("1.15", f"(iw-iw/1.15)*on/{f}", "(ih-ih/1.15)/2")
    return ("1.0", *center)


def same_orientation(src_dim):
    sw, sh = src_dim
    return abs(sw / sh - W / H) / (W / H) < 0.10


def blur_pad_chain():
    return (f"[0:v]split=2[bg_in][fg_in];"
            f"[bg_in]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H},boxblur=30:5,setsar=1[bg];"
            f"[fg_in]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[padded];")


def photo_filter(motion, dur, src_dim):
    frames = frames_of(dur)
    z, x, y = zoompan_expr(motion, frames)
    zp = f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p,setsar=1[vout]"
    if same_orientation(src_dim):
        return f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase:flags=lanczos,crop={W*2}:{H*2},{zp}"
    return blur_pad_chain() + f"[padded]{zp}"


def video_filter(src_dim):
    tail = f"setsar=1,fps={FPS},format=yuv420p[vout]"
    if same_orientation(src_dim):
        return f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},{tail}"
    return blur_pad_chain() + f"[padded]{tail}"


# ---------------------------------------------------------------- intermediates
def render_logo(shot, out):
    dur = shot["dur"]
    logo_w = min(int(W * 0.62), int(H * 0.40))
    ffmpeg("-f", "lavfi", "-t", f"{dur}", "-i", f"color=c=black:s={W}x{H}:r={FPS}",
           "-loop", "1", "-t", f"{dur}", "-i", shot["name"],
           "-filter_complex",
           f"[1:v]scale={logo_w}:-1:flags=lanczos[logo];"
           f"[0:v][logo]overlay=(W-w)/2:(H-h)/2:format=auto,format=yuv420p,setsar=1[vout]",
           "-map", "[vout]", *VENC, "-frames:v", str(frames_of(dur)), "-an", out)


def render_photo(shot, out):
    src = shot.get("file") or f"{shot['name']}{PHOTO_SUFFIX}.jpg"
    dur = shot["dur"]
    ffmpeg("-loop", "1", "-t", f"{dur}", "-i", src,
           "-filter_complex", photo_filter(shot["motion"], dur, get_dim(src)),
           "-map", "[vout]", *VENC, "-frames:v", str(frames_of(dur)), "-an", out)


def render_video(shot, out):
    src = f"{shot['name']}.mp4"
    dur = shot["dur"]
    ffmpeg("-ss", f"{shot['start']}", "-t", f"{dur}", "-i", src,
           "-filter_complex", video_filter(get_dim(src)),
           "-map", "[vout]", *VENC, "-frames:v", str(frames_of(dur)), "-an", out)


def render_intermediates(shots):
    d = INTER / "shots"
    d.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, shot in enumerate(shots):
        out = str(d / f"{i:03d}.mp4")
        print(f"  [{i+1:02d}/{len(shots)}] {shot['type']:5s} {shot['name']}")
        {"logo": render_logo, "photo": render_photo, "video": render_video}[shot["type"]](shot, out)
        paths.append(out)
    return paths


# ---------------------------------------------------------------- transitions
def extract_png(src, out_dir, n, start=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    args = []
    if start is not None:
        args += ["-ss", f"{start:.3f}"]
    ffmpeg(*args, "-i", src, "-frames:v", str(n), "-vsync", "0", str(out_dir / "%03d.png"))


def render_transition_clip(i, shots, inters):
    td, name = shots[i]["td"], shots[i]["trans"]
    n = frames_of(td)
    d = INTER / "trans" / f"{i:02d}"
    if d.exists():
        shutil.rmtree(d)
    extract_png(inters[i], d / "a", n, start=shots[i]["dur"] - td)
    extract_png(inters[i + 1], d / "b", n)
    got = transitions.render_transition(name, d / "a", d / "b", d / "t")
    out = str(d / "clip.mp4")
    ffmpeg("-framerate", f"{FPS}", "-i", str(d / "t" / "%03d.png"),
           *VENC, "-frames:v", str(got), "-an", out)
    print(f"  transition {i:02d} {name:16s} {got} frames")
    return out


def render_body(i, shots, inters):
    s = shots[i]
    head = shots[i - 1]["td"] if i > 0 else 0.0
    last = i == len(shots) - 1
    tail = 0.0 if last else s["td"]
    length = s["dur"] - head - tail
    out = str(INTER / "shots" / f"{i:03d}_body.mp4")
    vf = []
    if last:
        vf = ["-vf", f"fade=t=out:st={length - s['td']:.3f}:d={s['td']}:color=black"]
    ffmpeg("-ss", f"{head:.3f}", "-i", inters[i], *vf, *VENC,
           "-frames:v", str(frames_of(length)), "-an", out)
    return out


def build_video_track(shots, inters, out_path):
    parts = []
    for i in range(len(shots)):
        parts.append(render_body(i, shots, inters))
        if i < len(shots) - 1:
            parts.append(render_transition_clip(i, shots, inters))
    # concat demuxer resolves entries relative to the list file's directory
    lst = INTER / "concat.txt"
    lst.write_text("".join(f"file '{Path(p).relative_to(INTER).as_posix()}'\n" for p in parts),
                   encoding="utf-8")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", out_path)


# ---------------------------------------------------------------- audio
def measure_lufs(src, start, length):
    """Integrated loudness of a source window (ebur128). Single-pass `loudnorm`
    is avoided on purpose: its 3s lookahead breaks `adelay` placement."""
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{start:.3f}", "-t", f"{length:.3f}",
                           "-i", src, "-vn", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    for line in proc.stderr.splitlines():
        if line.strip().startswith("I:") and "LUFS" in line:
            return float(line.split(":")[1].split("LUFS")[0])
    raise RuntimeError(f"could not measure loudness of {src}")


def build_audio_track(shots, total, out_path):
    starts, _ = shot_starts(shots)
    inputs, chains, labels = [], [], []
    k = 0
    for i, s in enumerate(shots):
        if s["type"] != "video":
            continue
        lead, tail = s.get("a_lead", 0.0), s.get("a_tail", 0.0)
        src_start = s["start"] - lead
        length = lead + s["dur"] + tail
        src_len = float(probe(f"{s['name']}.mp4", "format=duration"))
        assert src_start >= 0 and src_start + length <= src_len + 0.05, \
            f"shot {i}: audio window {src_start:.2f}+{length:.2f}s exceeds source ({src_len:.2f}s)"
        t0 = starts[i] - lead
        delay_ms = int(round(t0 * 1000))
        gain_db = CLIP_LOUDNESS_LUFS - measure_lufs(f"{s['name']}.mp4", src_start, length)
        inputs += ["-ss", f"{src_start:.3f}", "-t", f"{length:.3f}", "-i", f"{s['name']}.mp4"]
        chains.append(
            f"[{k}:a]aresample={AUDIO_RATE},aformat=channel_layouts=stereo,"
            f"volume={gain_db:.2f}dB,alimiter=limit=0.89:attack=5:release=60,"
            f"atrim=0:{length:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={CLIP_XFADE},afade=t=out:st={length - CLIP_XFADE:.3f}:d={CLIP_XFADE},"
            f"adelay={delay_ms}|{delay_ms}[c{k}]")
        labels.append(f"[c{k}]")
        print(f"  audio: {s['name']} src {src_start:.1f}-{src_start+length:.1f}s -> timeline "
              f"{t0:.1f}-{t0+length:.1f}s  gain {gain_db:+.1f} dB")
        k += 1
    chains.append(f"{''.join(labels)}amix=inputs={k}:normalize=0:dropout_transition=0,"
                  f"apad,atrim=0:{total:.3f}[aout]")
    ffmpeg(*inputs, "-filter_complex", ";".join(chains), "-map", "[aout]",
           "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", out_path)


# ---------------------------------------------------------------- main
def main():
    if INTER.exists():
        shutil.rmtree(INTER)
    INTER.mkdir()
    starts, total = shot_starts(SHOT_LIST)
    print(f"=== {W}x{H} — {len(SHOT_LIST)} shots, total {total:.2f}s")
    for i, (s, t) in enumerate(zip(SHOT_LIST, starts)):
        print(f"  T{i}={t:5.2f}s  {s['type']:5s} {s['name']:32s} dur {s['dur']} -> {s['trans']} {s['td']}s")

    print("\n-- intermediates")
    inters = render_intermediates(SHOT_LIST)
    print("\n-- video track (bodies + transitions)")
    build_video_track(SHOT_LIST, inters, str(INTER / "video_only.mp4"))
    print("\n-- audio track (clip audio timeline)")
    build_audio_track(SHOT_LIST, total, str(INTER / "clip_audio.m4a"))
    print("\n-- mux")
    ffmpeg("-i", str(INTER / "video_only.mp4"), "-i", str(INTER / "clip_audio.m4a"),
           "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
           "-movflags", "+faststart", OUT_VIDEO)
    dur = probe(OUT_VIDEO, "format=duration")
    nframes = probe(OUT_VIDEO, "stream=nb_frames").split(",")[0]
    print(f"OK {OUT_VIDEO}: {dur}s, {nframes} frames (expected {frames_of(total)})")


if __name__ == "__main__":
    main()
