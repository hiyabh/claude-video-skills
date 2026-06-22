# -*- coding: utf-8 -*-
"""TEMPLATE — generate the 2D illustration B-roll for a drasha video.
Gemini `gemini-3-pro-image`, 9:16, ONE shared STYLE block per call for cohesion.
Edit the CONFIG + SCENES below, then run from build/.  Output -> scenes/scene_NN.png.
See references/image-generation.md for the modesty rules and which frames to eyeball."""
import os, json, base64, time, subprocess, urllib.request, urllib.error

# ---------- CONFIG ----------
ENV_PATH = os.path.expanduser("~/projects/openmontage/.env")  # fallback; prefer GOOGLE_API_KEY env var
MODEL = "gemini-3-pro-image"
OUT_DIR = "scenes"
PREFIX = "scene"          # -> scenes/scene_00.png ; use "extra" for a second batch

# STYLE: religious-Zionist (Dati-Leumi) modest default. Knitted kippah, NOT a black hat.
# Do NOT soften — see image-generation.md. Biblical scenes: append period garb per-subject.
STYLE = (
 " ART STYLE: flat 2D vector cartoon storybook illustration, soft rounded shapes, "
 "clean thick outlines, warm golden cozy color palette, gentle shading, vertical 9:16 framing. "
 "MODESTY (STRICT, non-negotiable): every human is an observant RELIGIOUS-ZIONIST (Dati-Leumi) Jew "
 "dressed fully modestly - men and boys wear a KNITTED KIPPAH (kippah seruga), NOT a chareidi black "
 "hat, beard optional, a long-sleeved shirt with tzitzit; "
 "women have their hair fully covered with a headscarf (tichel), long sleeves to the wrist, a high "
 "neckline, and a long skirt. No immodest clothing, no exposed skin beyond face and hands, no bare "
 "arms or legs, no tight clothing. Reverent, wholesome, family-friendly. "
 "No text, no Hebrew or English letters, no captions, no logos, no watermark.")

# index -> subject. Tag each to a narration beat in a comment (you'll need it for anchors).
SCENES = {
 0: "A devout religious Jewish man wrapped in a white tallit in heartfelt prayer at sunrise, "
    "two softly glowing icons above him - a warm home with a wedding ring, and golden wheat with "
    "coins - linked by a luminous golden stream of light.",            # seg0: secret pipe
 1: "An open glowing Talmud volume on a wooden shtender bathed in soft golden light, a small "
    "home-icon and coins-icon hovering above linked by a thread of light, reverent night study.",  # seg: gemara
 # ... add one per topic beat; generate 2-3x the number of narration paragraphs.
}
# ----------------------------

def load_key():
    if os.environ.get("GOOGLE_API_KEY"):
        return os.environ["GOOGLE_API_KEY"]
    for line in open(ENV_PATH, encoding="utf-8"):
        if line.startswith("GOOGLE_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GOOGLE_API_KEY not found")
KEY = load_key()
BASE = "https://generativelanguage.googleapis.com/v1beta"

def http_post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    for a in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print("  HTTP", e.code, e.read().decode("utf-8", "ignore")[:300], flush=True)
            if e.code in (429, 500, 503) and a < 3:
                time.sleep(12 * (a + 1)); continue
            raise

def extract_png(resp):
    for c in resp.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            d = p.get("inlineData") or p.get("inline_data")
            if d and d.get("data"):
                return base64.b64decode(d["data"])
    return None

def normalize(raw, out):
    tmp = out + ".raw"
    open(tmp, "wb").write(raw)
    subprocess.run(["ffmpeg", "-y", "-i", tmp, "-vf",
                    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1", out],
                   check=True, capture_output=True)
    os.remove(tmp)

os.makedirs(OUT_DIR, exist_ok=True)
for n, subj in SCENES.items():
    out = f"{OUT_DIR}/{PREFIX}_{n:02d}.png"
    if os.path.exists(out) and os.path.getsize(out) > 50000:
        print("skip", out); continue
    print(f"== {PREFIX} {n} ==", flush=True)
    resp = http_post(f"{BASE}/models/{MODEL}:generateContent?key={KEY}",
                     {"contents": [{"parts": [{"text": subj + STYLE}]}],
                      "generationConfig": {"imageConfig": {"aspectRatio": "9:16"}}})
    raw = extract_png(resp)
    if not raw:
        print("  NO IMAGE", json.dumps(resp)[:300]); continue
    normalize(raw, out)
    print("  SAVED", out, os.path.getsize(out) // 1024, "KB", flush=True)
print("DONE")
