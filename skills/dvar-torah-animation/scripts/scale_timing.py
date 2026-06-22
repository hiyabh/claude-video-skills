# -*- coding: utf-8 -*-
"""TEMPLATE — speed the narration by TEMPO and rescale ALL composition timings so audio,
captions, cards and background stay in sync. Tempo and sync are COUPLED — never speed the
audio without this. TEMPO here MUST equal TEMPO in build_bg_fast.py. Run from build/.
Backs nothing up itself — copy index.html -> index_orig.html and audio.mp3 -> audio_orig.mp3
FIRST, and move *_orig.html OUT of clip/ before linting (duplicate data-composition-id)."""
import re, json, subprocess, os

# ---------- CONFIG ----------
TEMPO = 1.10                 # 1.10 -> 3:14 becomes ~2:58
CLIP = "clip"
SRC_HTML = f"{CLIP}/index_orig.html"      # the pre-speed backup (move it back here to run)
SRC_AUDIO = f"{CLIP}/assets/audio_orig.mp3"
BASE_DUR = "194.04"          # the data-duration string to replace
# ----------------------------

# 1) speed up audio (pitch-preserving)
src = SRC_AUDIO if os.path.exists(SRC_AUDIO) else f"{CLIP}/assets/audio.mp3"
subprocess.run(["ffmpeg", "-y", "-i", src, "-filter:a", f"atempo={TEMPO}",
                "-c:a", "libmp3lame", "-q:a", "2", f"{CLIP}/assets/audio.mp3"],
               check=True, capture_output=True)

# 2) rescale index.html
html = open(SRC_HTML if os.path.exists(SRC_HTML) else f"{CLIP}/index.html", encoding="utf-8").read()

m = re.search(r"var GROUPS=(\[.*?\]);", html, re.S)       # 2a) per-word caption timings
groups = json.loads(m.group(1))
for g in groups:
    g["s"] = round(g["s"] / TEMPO, 3); g["e"] = round(g["e"] / TEMPO, 3)
    g["w"] = [[w[0], round(w[1] / TEMPO, 3), round(w[2] / TEMPO, 3)] for w in g["w"]]
html = html[:m.start(1)] + json.dumps(groups, ensure_ascii=False) + html[m.end(1):]

def rescale(name, html):                                   # 2b) scalar vars
    mm = re.search(rf"var {name}=([0-9.]+);", html)
    val = round(float(mm.group(1)) / TEMPO, 3)
    return html[:mm.start(1)] + str(val) + html[mm.end(1):], val
html, dur = rescale("DUR", html)
html, last = rescale("LAST", html)

html = re.sub(rf'data-duration="{re.escape(BASE_DUR)}"', f'data-duration="{dur}"', html)  # 2c)

open(f"{CLIP}/index.html", "w", encoding="utf-8").write(html)
newdur = float(subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
              "-of", "csv=p=0", f"{CLIP}/assets/audio.mp3"], capture_output=True, text=True).stdout.strip())
print(f"audio x{TEMPO} -> {newdur:.3f}s ; index DUR={dur} LAST={last} (groups={len(groups)})")
print("NOW: rebuild background with same TEMPO, re-pad to DUR, then render.")
