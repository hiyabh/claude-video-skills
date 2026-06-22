# -*- coding: utf-8 -*-
"""OPTIONAL live animation: turn the still scenes into real moving video with
Veo 3.1 (first + last frame interpolation), via the Google Gemini API.

CONCEPT (the chain the user asked for): each clip uses scene_i as the FIRST
frame and scene_{i+1} as the LAST frame; Veo generates a living animation that
morphs between them. Because consecutive clips share a boundary image
(clip N ends on scene_{N+1} = clip N+1's first frame), they concatenate with
SEAMLESS hard cuts — no crossfade needed. Add a closing clip scene_N -> scene_1
to make a perfect loop ("וחוזר חלילה").

COST (verify current rates — they change): Veo 3.1 Lite ~$0.05/s, Fast ~$0.15/s,
Standard ~$0.40/s. 8 clips x 8s on Lite ≈ $3. The spend is on the user's Google
billing — confirm the tier with them first (offer Lite/Fast/Standard).

Models on the key: veo-3.1-lite-generate-preview / veo-3.1-fast-generate-preview /
veo-3.1-generate-preview / veo-2.0-generate-001. Only Veo 3.1 supports lastFrame.

Run:  python generate_video.py 1     # test ONE clip first (validate + tiny cost)
      python generate_video.py all   # generate all (skips existing files)
Out:  assets/video/clip_*.mp4 (8s, 720x1280)
"""
import os, sys, json, base64, time, urllib.request, urllib.error

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(PROJECT, "assets", "images")
OUT = os.path.join(PROJECT, "assets", "video")
MODEL = "veo-3.1-lite-generate-preview"   # change tier per user's budget choice
os.makedirs(OUT, exist_ok=True)

STYLE = ("Children's storybook 2D cartoon animation coming to life, gentle smooth motion, "
         "soft and calm, keep the child's face and clothing consistent, warm lighting, "
         "no text, no captions, family-friendly.")

# (first_scene, last_scene, motion prompt). Close the loop with last->first.
PAIRS = [
    ("scene_01", "scene_02", "the child stands up and steps outside to begin the journey"),
    ("scene_02", "scene_03", "the child and a happy crowd walk forward; the destination appears"),
    # ... one pair per consecutive scene ...
    ("scene_08", "scene_01", "gentle close as the scene softly returns to the start, closing the loop"),
]


def load_key():
    if os.environ.get("GOOGLE_API_KEY"):
        return os.environ["GOOGLE_API_KEY"]
    for line in open(os.path.expanduser("~/projects/openmontage/.env"), encoding="utf-8"):
        if line.startswith("GOOGLE_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("no key")


KEY = load_key()
BASE = "https://generativelanguage.googleapis.com/v1beta"


def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode("ascii")


def http(url, data=None, method="GET"):
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=(json.dumps(data).encode() if data else None),
                                 headers=headers, method=method)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code}: {e.read().decode('utf-8','ignore')[:400]}")
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(10 * (attempt + 1)); continue
            raise
        except Exception as e:
            print(f"  err: {e}")
            if attempt < 3:
                time.sleep(8); continue
            raise


def generate(first_img, last_img, prompt, out_name):
    payload = {"instances": [{
        "prompt": prompt + " " + STYLE,
        "image": {"bytesBase64Encoded": b64(os.path.join(IMG, first_img + ".png")), "mimeType": "image/png"},
        "lastFrame": {"bytesBase64Encoded": b64(os.path.join(IMG, last_img + ".png")), "mimeType": "image/png"},
    }], "parameters": {"aspectRatio": "9:16"}}
    op = http(f"{BASE}/models/{MODEL}:predictLongRunning?key={KEY}", payload, "POST")
    name = op.get("name")
    print(f"  operation: {name}")
    if not name:
        return False
    for i in range(60):
        time.sleep(10)
        st = http(f"{BASE}/{name}?key={KEY}")
        if st.get("done"):
            if "error" in st:
                print("  !! op error:", json.dumps(st["error"])[:400]); return False
            resp = st.get("response", {})
            samples = (resp.get("generateVideoResponse", {}).get("generatedSamples")
                       or resp.get("generatedSamples") or [])
            if not samples:
                print("  !! no samples:", json.dumps(resp)[:400]); return False
            video = samples[0].get("video", {})
            out_path = os.path.join(OUT, out_name + ".mp4")
            if video.get("bytesBase64Encoded"):
                open(out_path, "wb").write(base64.b64decode(video["bytesBase64Encoded"]))
            elif video.get("uri"):
                uri = video["uri"]
                dl = uri + (("&" if "?" in uri else "?") + "key=" + KEY)
                with urllib.request.urlopen(urllib.request.Request(dl), timeout=180) as r:
                    open(out_path, "wb").write(r.read())
            else:
                print("  !! no video data"); return False
            print(f"  SAVED {out_name}.mp4 ({os.path.getsize(out_path)//1024} KB)")
            return True
        print(f"  ...polling ({i+1})")
    print("  !! timeout"); return False


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    for idx, (a, b, p) in enumerate(PAIRS):
        if only != "all" and str(idx + 1) != only:
            continue
        name = f"clip_{idx+1:02d}_{a}_to_{b}"
        out_path = os.path.join(OUT, name + ".mp4")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 100000:
            print(f"== [{idx+1}] {name} exists, skip =="); continue
        print(f"== [{idx+1}] {a} -> {b} ==", flush=True)
        if not generate(a, b, p, name):
            print("  FAILED", name, flush=True)
