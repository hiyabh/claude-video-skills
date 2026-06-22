# -*- coding: utf-8 -*-
"""TEMPLATE — build a FAST-CUT 1080x1920 background (no audio) for a drasha video.
Mix Veo clips (video/scene_NN.mp4) and Gemini stills (scenes/*.png, Ken-Burns animated).
Each shot has an ANCHOR = the composition-time second the narrator reaches its topic,
READ FROM THE `GROUPS` ARRAY IN index.html (these include the ~2.5s intro offset — do NOT
use a raw origin-0 transcript).  See references/background-timing.md.  Run from build/."""
import subprocess, os

# ---------- CONFIG ----------
W, H, FPS = 1080, 1920, 30
D = 0.4                              # crossfade overlap (s) — short = snappy cuts
TEMPO = 1.10                         # MUST match scale_timing.py (1.0 if no speed-up pass)
COMP_DUR = 194.04                    # composition data-duration BEFORE speed-up
TOTAL = round(COMP_DUR / TEMPO, 3)   # background length after speed-up
VEO_DIR = "video"                    # video/scene_NN.mp4
IMG_DIR = "scenes"                   # scenes/extra_NN.png (stills for Ken Burns)
IMG_PREFIX = "extra"

# ordered shots: (kind, ref, anchor). kind 'v'=Veo clip idx, 'i'=still idx.
# anchor = composition time (s) from GROUPS, BEFORE /TEMPO (divided below). Comment the words.
SHOTS = [
    ('v', 0,   0.00),   # intro / opening topic
    ('i', 0,  12.64),   # "...secret pipe connecting them"   (GROUPS s for that line)
    ('i', 1,  16.16),   # "...the other flows in"
    # ... ~30-40 shots, ~5-6s apart; reuse hero shots with different motion where topics recur.
]
# ----------------------------

def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip())

def run(a): subprocess.run(a, check=True, capture_output=True)

os.makedirs("fast", exist_ok=True)

anchors = [round(a / TEMPO, 3) for _, _, a in SHOTS]   # composition time after speed-up
assert anchors == sorted(anchors), "anchors must be monotonic"
durs = [anchors[k + 1] - anchors[k] for k in range(len(anchors) - 1)] + [TOTAL - anchors[-1]]
assert min(durs) > D, f"a shot is shorter than crossfade D: {min(durs):.2f}"
print("shots:", len(SHOTS), "total:", round(sum(durs), 3),
      "min/max shot:", round(min(durs), 2), "/", round(max(durs), 2))

def veo_pp(idx):                       # ping-pong (forward+reverse) seamless loop, cached
    pp = f"fast/pp_v{idx:02d}.mp4"
    if os.path.exists(pp): return pp
    src = f"{VEO_DIR}/scene_{idx:02d}.mp4"
    vf = f"scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1"
    fc = f"[0:v]{vf},split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v]"
    run(["ffmpeg", "-y", "-an", "-i", src, "-filter_complex", fc, "-map", "[v]",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", pp])
    return pp

def kenburns_vf(i, need):              # jitter-free Ken Burns, motion varies by shot index
    N = max(1, int(round(need * FPS)))
    base = f"scale={W*3}:{H*3}:flags=lanczos,setsar=1,zoompan=%s:d={N}:s={W}x{H}:fps={FPS},trim=duration={need:.3f}"
    cx, cy = "x='iw/2-(iw/zoom/2)'", "y='ih/2-(ih/zoom/2)'"
    mode = i % 5
    if mode == 0:   z = f"z='1+0.12*on/{N}':{cx}:{cy}"                       # zoom in
    elif mode == 1: z = f"z='1.12-0.12*on/{N}':{cx}:{cy}"                    # zoom out
    elif mode == 2: z = f"z='1.08':x='(iw-iw/zoom)*on/{N}':{cy}"            # pan right
    elif mode == 3: z = f"z='1.08':x='(iw-iw/zoom)*(1-on/{N})':{cy}"        # pan left
    else:           z = f"z='1.08':{cx}:y='(ih-ih/zoom)*(1-on/{N})'"        # pan up
    return base % z

shot_files = []
for i, ((kind, ref, anc), d) in enumerate(zip(SHOTS, durs)):
    need = d + (0 if i == len(SHOTS) - 1 else D)
    out = f"fast/shot_{i:02d}.mp4"
    shot_files.append(out)
    if os.path.exists(out): continue
    if kind == 'v':
        pp = veo_pp(ref); plen = dur(pp)
        off = (i * 1.7) % max(0.1, plen - 0.2)        # vary start so repeats differ
        run(["ffmpeg", "-y", "-an", "-stream_loop", str(int(need // plen) + 2), "-ss", f"{off:.2f}",
             "-i", pp, "-t", f"{need:.3f}", "-vf", f"scale={W}:{H},setsar=1,fps={FPS}",
             "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", out])
    else:
        run(["ffmpeg", "-y", "-loop", "1", "-t", f"{need:.3f}", "-i", f"{IMG_DIR}/{IMG_PREFIX}_{ref:02d}.png",
             "-vf", kenburns_vf(i, need), "-c:v", "libx264", "-crf", "18", "-preset", "medium",
             "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    print(f"shot {i:02d} [{kind}{ref}] @{anc/TEMPO:.1f}s {round(dur(out),2)}s", flush=True)

# xfade-chain; offset_k = anchors[k]
inputs = []
for f in shot_files: inputs += ["-i", f]
fc, prev = [], "0:v"
for k in range(1, len(shot_files)):
    fc.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={D}:offset={anchors[k]:.3f}[v{k}]")
    prev = f"v{k}"
run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", f"[{prev}]",
     "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS),
     "background.mp4"])
print("background.mp4:", round(dur("background.mp4"), 2), "s")
# Then pad to TOTAL: ffmpeg -i background.mp4 -vf "tpad=stop_mode=clone:stop_duration=0.6,fps=30"
#   -t TOTAL clip/assets/background.mp4    (closes the frame-rounding shortfall)
