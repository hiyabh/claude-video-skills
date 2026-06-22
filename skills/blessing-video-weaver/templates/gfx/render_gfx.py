# -*- coding: utf-8 -*-
"""Render all graphics pieces: chapter cards (mp4), outro (mp4), lower-thirds (webm alpha)."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
os.makedirs("renders", exist_ok=True)
os.makedirs("vars", exist_ok=True)

CHAPTERS = [
    ("ch1", {"num": "פרק א", "title": "כשמך כן את", "emoji": "✨"}),
    ("ch_bina", {"num": "הפסקה קלה", "title": "רגע... למאיה יש משהו להגיד", "emoji": "🎬"}),
    ("ch2", {"num": "פרק ב", "title": "אישה של מסירות נפש", "emoji": "💪"}),
    ("ch3", {"num": "פרק ג", "title": "פורצת דרך", "emoji": "🚀"}),
    ("ch4", {"num": "פרק ד", "title": "רחוקה - אבל הכי קרובה", "emoji": "🌍"}),
    ("ch5", {"num": "פרק ה", "title": "זיכרונות...", "emoji": "📸"}),
    ("ch6", {"num": "פרק ו", "title": "40 זה ה-20 החדש", "emoji": "🎉"}),
    ("ch7", {"num": "פרק אחרון", "title": "מכל הלב - מכל האחים", "emoji": "❤"}),
]

LOWERS = [
    # EDIT: one entry per person — key matches the .webm name in overlay_segments.py
    ("lt_p1", {"name": "שם ראשון", "tag": "", "badge": False}),
    ("lt_p2", {"name": "שם שני", "tag": "", "badge": False}),
    ("lt_p3", {"name": "שם שלישי", "tag": "", "badge": False}),
    ("lt_p4", {"name": "שם רביעי", "tag": "", "badge": False}),
    ("lt_host1", {"name": "המנחה", "tag": "טייק 1 🎬", "badge": True}),
    ("lt_host2", {"name": "המנחה", "tag": "טייק 2 ❤", "badge": True}),
]

only = sys.argv[1] if len(sys.argv) > 1 else None


def run(name, comp, out, fmt, variables=None):
    if only and only not in name:
        return
    if os.path.exists(out):
        print(f"skip: {name}", flush=True)
        return
    cmd = f'npx hyperframes render -c {comp} -o "{out}" --format {fmt} --quiet'
    if variables is not None:
        vf = os.path.join("vars", name + ".json")
        with open(vf, "w", encoding="utf-8") as f:
            json.dump(variables, f, ensure_ascii=False)
        cmd += f' --variables-file "{vf}"'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = r.returncode == 0 and os.path.exists(out)
    print(("done" if ok else "FAILED") + f": {name}", flush=True)
    if not ok:
        tail = (r.stdout or "") + (r.stderr or "")
        print(tail[-1200:], flush=True)


for name, v in CHAPTERS:
    run(name, "compositions/chapter.html", f"renders/{name}.mp4", "mp4", v)

run("outro", "compositions/outro.html", "renders/outro.mp4", "mp4")

for name, v in LOWERS:
    run(name, "compositions/lower.html", f"renders/{name}.webm", "webm", v)

# text-behind-subject big words (composited between segment video and its cutout)
BEHIND = [
    ("bh_40", {"word": "40", "top": 8}),
    ("bh_balev", {"word": "איתי בלב ❤", "top": 11}),
    ("bh_mazal", {"word": "מזל טוב!", "top": 9}),
]
for name, v in BEHIND:
    run(name, "compositions/behind.html", f"renders/{name}.webm", "webm", v)

print("GFX DONE")
