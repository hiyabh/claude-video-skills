# -*- coding: utf-8 -*-
"""Generate consistent children's-storybook illustrations with Google Gemini
(gemini-3-pro-image / "Nano Banana Pro").

TWO key techniques proven in production:
  1. ANCHOR CHARACTER — generate the hero ONCE, then pass that image as a
     reference to every scene so the character stays identical across the clip.
  2. REFERENCE PHOTO (optional) — turn a real photo of the child into the
     storybook hero (keeps likeness + e.g. a real kippah). Apply EXIF rotation
     first (phone photos are often sideways): see fix_orientation() below.

Setup:
  - API key: set GOOGLE_API_KEY in the environment (from Google AI Studio).
  - Models available on that key: imagen-4.0-*, gemini-3-pro-image (verify with
    GET /v1beta/models?key=KEY). gemini-3-pro-image accepts a reference image →
    best for character consistency.
  - Output: assets/images/hero_<name>.png + scene_*.png (9:16 for shorts).

Edit the CONFIG block (STYLE, HERO, SCENES) for a new song, then run:
  python generate_images.py            # hero + all scenes
"""
import os, base64, json, time, urllib.request, urllib.error

# ----------------------- CONFIG (edit per song) -----------------------
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
OUT_DIR = os.path.join(PROJECT, "assets", "images")
MODEL = "gemini-3-pro-image"
ASPECT = "9:16"   # "16:9" for TV/YouTube

STYLE = (
    "children's storybook illustration, warm flat colors, soft rounded shapes, "
    "gentle golden-hour lighting, joyful and cheerful mood, kid-friendly, vibrant, "
    "clean simple shapes, no text, vertical 9:16 composition"
)

# Hero character. If REF_PHOTO is set, the hero is generated FROM that photo
# (likeness preserved). Otherwise it is generated from this text alone.
REF_PHOTO = None  # e.g. os.path.join(PROJECT, "assets", "child_ref_upright.png")
HERO = (
    "Full-body character design of a happy 5-year-old child with a big warm smile "
    "and big bright eyes, friendly cartoon proportions, standing facing forward on a "
    "plain soft cream background. " + STYLE
)

# (output_name, scene prompt). The hero image is auto-appended as a reference.
SCENES = [
    ("scene_01", "the hero waking up at home in soft morning light, excited"),
    ("scene_02", "the hero walking happily outside toward a big adventure"),
    # ... add 4-8 scenes that follow the lyrics, in narrative order.
]
# ----------------------------------------------------------------------

os.makedirs(OUT_DIR, exist_ok=True)


def load_key():
    if os.environ.get("GOOGLE_API_KEY"):
        return os.environ["GOOGLE_API_KEY"]
    env = os.path.expanduser("~/projects/openmontage/.env")
    for line in open(env, encoding="utf-8"):
        if line.startswith("GOOGLE_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GOOGLE_API_KEY not found")


KEY = load_key()
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"


def fix_orientation(src, dst):
    """Apply EXIF rotation so the face is upright before using as a reference."""
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(src))
    im.thumbnail((1024, 1365))   # medium size for upload
    im.save(dst)
    return dst


def post(payload, tries=4):
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(tries):
        try:
            req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            print(f"  HTTP {e.code} (try {attempt+1}): {body[:300]}")
            if e.code in (429, 500, 503) and attempt < tries - 1:
                time.sleep(8 * (attempt + 1)); continue
            raise
        except Exception as e:
            print(f"  err (try {attempt+1}): {e}")
            if attempt < tries - 1:
                time.sleep(6); continue
            raise


def extract_image(resp):
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    return None


def gen(prompt, out_name, ref_b64=None, ref_note=None):
    parts = [{"text": prompt}]
    if ref_b64:
        parts.append({"inlineData": {"mimeType": "image/png", "data": ref_b64}})
        parts.append({"text": ref_note or
                      "Keep the character's face, hair and clothing EXACTLY identical "
                      "to the reference image. Same character."})
    payload = {"contents": [{"parts": parts}],
               "generationConfig": {"responseModalities": ["IMAGE"],
                                    "imageConfig": {"aspectRatio": ASPECT}}}
    img = extract_image(post(payload))
    if not img:
        print("  !! no image returned"); return None
    path = os.path.join(OUT_DIR, out_name + ".png")
    open(path, "wb").write(img)
    print(f"  saved {out_name}.png ({len(img)//1024} KB)")
    return img


def main():
    print("== hero ==")
    if REF_PHOTO:
        ref = fix_orientation(REF_PHOTO, os.path.join(OUT_DIR, "_ref_upright.png"))
        rb = base64.b64encode(open(ref, "rb").read()).decode("ascii")
        hero = gen(HERO, "hero",
                   ref_b64=rb,
                   ref_note="The cartoon child MUST clearly resemble the child in the photo "
                            "(face, hair, and any kippah/hat). Turn them into a cute cartoon.")
    else:
        hero = gen(HERO, "hero")
    if not hero:
        print("HERO FAILED — aborting"); return
    hb = base64.b64encode(hero).decode("ascii")

    for name, prompt in SCENES:
        print(f"== {name} ==")
        try:
            gen(prompt + " " + STYLE, name, ref_b64=hb)
        except Exception as e:
            print("  ERR", name, e)
        time.sleep(2)
    print("\nDONE →", OUT_DIR)


if __name__ == "__main__":
    main()
