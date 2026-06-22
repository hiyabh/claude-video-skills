# -*- coding: utf-8 -*-
"""TEMPLATE — render the closing credit card (logo + attribution) as a 1080x1920 PNG.
RTL Hebrew via python-bidi (no reshaper needed for Hebrew). Warm dark palette + gold glow.
Edit CONFIG, run from build/.  Output -> qc/endcard.png  (make_final.py turns it into 2s)."""
import os
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display

# ---------- CONFIG ----------
W, H = 1080, 1920
OUT = "qc/endcard.png"
LOGO = "assets/logo.png"   # <-- your own logo PNG (optional; comment out if none)
RUB_B = r"C:\Windows\Fonts\Rubik-Bold.ttf"   # Windows; on mac/linux point to your own font
RUB_R = r"C:\Windows\Fonts\Rubik-Regular.ttf"
LINES = [   # (text, font, size, color)  — top to bottom, Hebrew RTL — EDIT to your credits
    ("דבר תורה מונפש",        "B", 76, (255, 211, 110)),
    ("מתוך הבלוג",            "R", 50, (255, 247, 232)),
    ("״שם הבלוג שלך״",         "B", 64, (255, 247, 232)),
    ("מאת ___",               "R", 52, (255, 211, 110)),
]
GOLD = (255, 211, 110)
# ----------------------------

img = Image.new("RGB", (W, H), (13, 10, 5))
top, bot = (26, 18, 7), (8, 6, 3)
for y in range(H):
    f = y / H
    img.paste(tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3)), (0, y, W, y + 1))
d = ImageDraw.Draw(img)

glow = Image.new("L", (W, H), 0)
ImageDraw.Draw(glow).ellipse([W // 2 - 460, 430, W // 2 + 460, 1350], fill=46)
img.paste(Image.new("RGB", (W, H), GOLD), (0, 0), glow)

logo = Image.open(LOGO).convert("RGBA")
lw = 560
logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
img.paste(logo, ((W - lw) // 2, 470), logo)

def centered(text, font, y, fill):
    t = get_display(text)
    bb = d.textbbox((0, 0), t, font=font)
    d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], y), t, font=font, fill=fill)

d.rectangle([W // 2 - 90, 1205, W // 2 + 90, 1209], fill=GOLD)   # divider
y, gaps = 1230, [130, 84, 110, 0]
for (text, fk, size, color), gap in zip(LINES, gaps):
    font = ImageFont.truetype(RUB_B if fk == "B" else RUB_R, size)
    centered(text, font, y, color); y += gap

os.makedirs("qc", exist_ok=True)
img.save(OUT)
print("saved", OUT, img.size)
