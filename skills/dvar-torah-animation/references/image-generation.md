# Illustrations — Google Gemini image (`gemini-3-pro-image`)

Flat 2D storybook B-roll, 9:16, **one consistent STYLE block on every call** so all images look
like one set. This is what made the Chukat set cohere across 27 illustrations.

## API key
Set your own `GOOGLE_API_KEY` (from Google AI Studio) as an environment variable —
the same key does Gemini image + Veo. Load it from the env, don't hardcode.

```python
import os
def load_key():
    if os.environ.get("GOOGLE_API_KEY"):
        return os.environ["GOOGLE_API_KEY"]
    # optional fallback: a local .env file you control
    for line in open(os.path.expanduser("~/projects/openmontage/.env"), encoding="utf-8"):
        if line.startswith("GOOGLE_API_KEY="):
            return line.split("=", 1)[1].strip()
```

## Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image:generateContent?key=KEY
body: {"contents":[{"parts":[{"text": SUBJECT + STYLE}]}],
       "generationConfig":{"imageConfig":{"aspectRatio":"9:16"}}}
```
Image bytes come back base64 in `candidates[].content.parts[].inlineData.data`. Retry on 429/500/503
with backoff. Then **normalize to exactly 1080×1920**:
`ffmpeg -i raw.png -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" out.png`

## The modesty STYLE block (religious-Zionist / Dati-Leumi — STRICT)
Append verbatim to every subject prompt. The user rejected ~5 rounds before this exact wording
passed; do not soften it. The figures must read as **religious-Zionist (Dati-Leumi)** — knitted
kippah, NOT chareidi black hat:

```
 ART STYLE: flat 2D vector cartoon storybook illustration, soft rounded shapes, clean thick
 outlines, warm golden cozy color palette, gentle shading, vertical 9:16 framing.
 MODESTY (STRICT, non-negotiable): every human is an observant RELIGIOUS-ZIONIST (Dati-Leumi)
 Jew dressed fully modestly - men and boys wear a KNITTED KIPPAH (kippah seruga), NOT a chareidi
 black hat, beard optional, a long-sleeved shirt with tzitzit; women have their hair fully
 covered with a headscarf (tichel), long sleeves to the wrist, a high neckline, and a long
 skirt. No immodest clothing, no exposed skin beyond face and hands, no bare arms or legs, no
 tight clothing. Reverent, wholesome, family-friendly.
 No text, no Hebrew or English letters, no captions, no logos, no watermark.
```
For **biblical/Temple scenes** swap modern dress for period desert robes / accurate bigdei kehuna
(append per-subject), but keep the modesty rules.

## Modesty / accuracy specifics that need a visual check
Generate, then **Read the PNG** for any frame with these — the model gets them wrong ~1 in 3:
- **A bride**: must wear a **tichel/headscarf with her face uncovered** — NOT a face veil. (We had
  to regenerate the chuppah once for exactly this. Prompt: *"hair fully covered with a cloth
  HEADSCARF (a tichel), NOT wearing any face veil, her face fully visible and smiling"*.)
- **Clergy (Aharon / Kohen Gadol)**: white robes + **choshen (12-stone breastplate) + mitznefet
  (turban)**; reconciling a couple **without touching the woman** (hands gesture only).
- **Biblical desert scenes**: authentic desert garb, not modern dress.
- **Boys** wear a kippah; **girls** do not (only married women cover hair).

## Quantity & cohesion
- Generate **2–3× the number of narration paragraphs** so the background can cut fast.
- Tag each image to a narration beat at creation time (a `seg`/anchor note) — you'll need it when
  you place shots in `build_bg_fast.py`.
- Keep subjects symbolic where people aren't needed (a glowing pipe, coins-and-wheat, a balance
  scale, an open Gemara, Shabbat candles) — cheap variety that's always modest.
