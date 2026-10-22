#!/usr/bin/env python3
"""Overlay a beautiful poster-style Hebrew title onto the opening collage.

Bakes an elegant title (eyebrow + main title + subtitle) into the collage JPG so
it becomes shot 0 of the recap video. This is the ONE place on-screen text is
allowed (user directive 2026-07-07) — the rest of the video stays text-free.

Handles Hebrew RTL correctly via python-bidi, uses a rounded display font
(Rubik-Bold), and adds a gradient scrim + radial glow + text stroke + drop shadow
so the title reads clearly over any photo. Works for any collage size (1080x1920,
1920x1080, 1080x1080) — all sizes scale with frame width.

REQUIRES: pip install pillow python-bidi   (both already present on this machine)

USAGE:
  1. FIRST run build_collage.py to produce the plain mosaic.
  2. Set BASE_DIR + PHOTO_SUFFIX + the title text below.
  3. Run: python add_collage_title.py   (overwrites the collage in place)
  4. THEN run build_video.py.
  Re-tuning the title? Re-run build_collage.py (restores the plain base) before
  re-running this, since it overwrites the collage.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from bidi.algorithm import get_display

# >>> EDIT THIS:
BASE_DIR = Path("./event-media")   # <-- set to your folder of photos+clips
PHOTO_SUFFIX = "_YYYY-MM-DD_HH-MM-SS"
os.chdir(BASE_DIR)

COLLAGE = f"photo_collage{PHOTO_SUFFIX}.jpg"

# >>> EDIT per event (Hebrew, logical order — bidi is applied automatically).
# EYEBROW = small kicker line; TITLE_LINES = big title (one entry per line so YOU
# control the line breaks); SUBTITLE = the community/organization name.
EYEBROW     = "הפנינג"
TITLE_LINES = ["פתיחת הקיץ", "הגדול"]
SUBTITLE    = "שם הקהילה"

# Fonts (Windows). Rubik-Bold = rounded modern Hebrew display face — swap for any
# Hebrew-capable TTF/OTF (Alef-Bold, Assistant, Heebo, Arial Bold all work).
FONT_BOLD = r"C:\Windows\Fonts\Rubik-Bold.ttf"
FONT_REG  = r"C:\Windows\Fonts\Rubik-Regular.ttf"

# Palette
WHITE  = (255, 255, 255)
GOLD   = (255, 200, 70)     # warm summer accent for the eyebrow
SHADOW = (0, 0, 0)

MARGIN_RATIO = 0.90         # max text width as fraction of frame width
TITLE_CENTER_Y = 0.74       # vertical center of the title block (fraction of H)


def rtl(s):
    return get_display(s)


def fit_font(path, text, max_w, start, min_size=28):
    """Largest font size (<= start) whose rendered width fits max_w."""
    size = start
    while size > min_size:
        f = ImageFont.truetype(path, size)
        w = f.getbbox(text)[2] - f.getbbox(text)[0]
        if w <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(path, min_size)


def line_h(f):
    # Measured from the ascender line (anchor "ma" draws from there), so the
    # returned height covers the glyphs' real bottom, not just their ink box.
    b = f.getbbox("ראגּל")
    return b[3]


def draw_center(draw, cx, y, text, font, fill, stroke_w=0, stroke_fill=SHADOW):
    draw.text((cx, y), text, font=font, fill=fill, anchor="ma",
              stroke_width=stroke_w, stroke_fill=stroke_fill)


def main():
    img = Image.open(COLLAGE).convert("RGB")
    W, H = img.size
    cx = W // 2
    max_w = int(W * MARGIN_RATIO)

    # --- 1. Scrim: bottom vertical gradient + radial glow anchoring the title ---
    vgrad = Image.new("L", (1, H), 0)
    vpx = vgrad.load()
    for y in range(H):
        a = 0
        t = (y - 0.56 * H) / (0.44 * H)   # start low so faces above stay bright
        if t > 0:
            a = int(min(1.0, t) ** 1.6 * 175)
        tt = (0.10 * H - y) / (0.10 * H)  # subtle top balance
        if tt > 0:
            a = max(a, int(tt * 55))
        vpx[0, y] = a
    vgrad = vgrad.resize((W, H))

    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    gcx, gcy = W // 2, int(H * TITLE_CENTER_Y)
    rx, ry = int(W * 0.62), int(H * 0.20)
    gdraw.ellipse([gcx - rx, gcy - ry, gcx + rx, gcy + ry], fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(int(W * 0.09)))

    scrim = Image.composite(Image.new("L", (W, H), 255), Image.new("L", (W, H), 0), vgrad)
    scrim = ImageChops.lighter(scrim, glow)
    img = Image.composite(Image.new("RGB", (W, H), SHADOW), img, scrim)

    draw = ImageDraw.Draw(img)

    # --- 2. Fit the fonts (scale with frame width) ---
    main_size = int(W * 0.155)
    main_fonts = [fit_font(FONT_BOLD, rtl(t), max_w, main_size) for t in TITLE_LINES]
    sub_f = fit_font(FONT_REG, rtl(SUBTITLE), max_w, int(W * 0.052))
    eb_text = rtl("  ".join(list(EYEBROW)))   # airy letter tracking
    eb_font = fit_font(FONT_BOLD, eb_text, max_w, int(W * 0.062))

    gap_small = int(H * 0.012)
    gap_med = int(H * 0.020)
    eb_h = line_h(eb_font)
    main_hs = [line_h(f) for f in main_fonts]
    sub_h = line_h(sub_f)
    block_h = (eb_h + gap_med + sum(main_hs) + gap_small * (len(main_fonts) - 1)
               + gap_med + sub_h)
    top = int(H * TITLE_CENTER_Y - block_h / 2)

    # --- 3. Eyebrow (gold) ---
    y = top
    draw_center(draw, cx, y, eb_text, eb_font, GOLD,
                stroke_w=max(2, W // 360), stroke_fill=(90, 45, 0))
    y += eb_h + gap_med

    # --- 4. Main title: soft drop shadow, then white text with dark stroke ---
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    yy = y
    for txt, f, h in zip(TITLE_LINES, main_fonts, main_hs):
        sdraw.text((cx + int(W * 0.006), yy + int(H * 0.006)), rtl(txt), font=f,
                   fill=(0, 0, 0, 170), anchor="ma")
        yy += h + gap_small
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(int(W * 0.010)))
    img = Image.alpha_composite(img.convert("RGBA"), shadow_layer).convert("RGB")
    draw = ImageDraw.Draw(img)

    stroke_w = max(4, W // 150)
    yy = y
    for txt, f, h in zip(TITLE_LINES, main_fonts, main_hs):
        draw_center(draw, cx, yy, rtl(txt), f, WHITE,
                    stroke_w=stroke_w, stroke_fill=(20, 30, 55))
        yy += h + gap_small
    y = yy - gap_small + gap_med

    # --- 5. Subtitle (soft white) ---
    draw_center(draw, cx, y, rtl(SUBTITLE), sub_f, (240, 245, 255),
                stroke_w=max(2, W // 400), stroke_fill=(0, 0, 0))

    img.save(COLLAGE, quality=94)
    print(f"OK titled {COLLAGE} ({Path(COLLAGE).stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
